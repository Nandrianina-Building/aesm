import hashlib
import hmac
import json
import os
from datetime import date, timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Role, User
from apps.certificates.models import MemberCard, Quitus, Receipt
from apps.documents.models import Document
from apps.events import services as ev
from apps.events.models import Event, Reservation
from apps.finance import services as fin
from apps.finance.models import BudgetEntry
from apps.memberships import services as ms
from apps.payments import services as pay
from apps.payments.models import ContributionDue, ContributionType, Payment

PWD = "Tr0ub4dor-Long-Pass!"


def make_user(matricule, role=None, status="active", phone=None):
    u = User.objects.create_user(matricule, PWD, first_name=matricule.title(), last_name="Test", phone=phone or f"034{abs(hash(matricule)) % 10**7:07d}",
                                 account_status=status)
    if role:
        u.roles.add(Role.objects.get(code=role))
    return u


class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("init_aesm", verbosity=0)
        cls.admin = make_user("ADM1", "super_admin")
        cls.treasurer = make_user("TRE1", "treasurer")
        cls.secretary = make_user("SEC1", "secretary")
        cls.president = make_user("PRE1", "president")
        cls.events_mgr = make_user("EVT1", "event_manager")
        cls.m1 = make_user("MEM1")
        cls.m2 = make_user("MEM2")
        cls.contrib = ContributionType.objects.create(
            name="Adhésion", amount=2000, start_date=date.today() - timedelta(days=1), end_date=date.today() + timedelta(days=60),
            audience="all_members", period_label="2026")
        pay.generate_dues_for_contribution(cls.contrib)

    def login(self, user):
        self.client.force_login(user)

    def new_payment(self, user, ref="TX1", due=None):
        due = due or ContributionDue.objects.get(user=user, contribution=self.contrib)
        p, _ = pay.create_payment(user, due=due, method="simulation", external_reference=ref, payer_phone="0340000000",
                                  idempotency_key=f"k-{user.pk}-{ref}")
        return p


class MembershipTests(Base):
    def test_application_acceptance_creates_card_profile_and_dues(self):
        u = make_user("NEW1", status="pending")
        m = ms.submit_application(u)
        ms.accept(m, self.secretary)
        u.refresh_from_db()
        self.assertEqual(u.account_status, "active")
        self.assertTrue(MemberCard.objects.filter(user=u).exists())
        self.assertTrue(u.profile.member_number.startswith("AESM-"))
        with self.assertRaises(ms.TransitionError):
            ms.accept(m, self.secretary)  # transition interdite : déjà acceptée

    def test_refused_can_resubmit(self):
        u = make_user("REF1", status="pending")
        m = ms.submit_application(u)
        ms.refuse(m, self.secretary, "dossier incomplet")
        ms.submit_application(u)
        self.assertEqual(u.memberships.get().status, "pending")

    def test_registration_rejects_duplicates_and_weak_password(self):
        data = {"last_name": "A", "first_name": "B", "matricule": "MEM1", "phone": "0341234567", "password1": "short", "password2": "short"}
        r = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(phone="0341234567").exists())


class PaymentTests(Base):
    def test_full_payment_flow(self):
        p = self.new_payment(self.m1)
        with self.assertRaises(pay.PaymentError):
            pay.confirm_payment(p.pk, self.treasurer, received_amount=Decimal("1500"))  # mauvais montant
        pay.confirm_payment(p.pk, self.treasurer, received_amount=Decimal("2000"))
        pay.confirm_payment(p.pk, self.treasurer, received_amount=Decimal("2000"))  # idempotent
        p.refresh_from_db()
        self.assertEqual(p.status, "confirmed")
        self.assertEqual(Receipt.objects.filter(payment=p).count(), 1)
        self.assertEqual(Quitus.objects.filter(user=self.m1).count(), 1)
        self.assertEqual(BudgetEntry.objects.filter(payment=p).count(), 1)
        self.assertEqual(fin.summary()["income"], 2000)
        self.assertEqual(ContributionDue.objects.get(user=self.m1).status, "paid")

    def test_no_double_payment_and_unique_reference(self):
        self.new_payment(self.m1, "TXA")
        due = ContributionDue.objects.get(user=self.m1)
        with self.assertRaises(pay.PaymentError):
            pay.create_payment(self.m1, due=due, method="simulation", external_reference="TXB", idempotency_key="other")
        with self.assertRaises(pay.PaymentError):
            pay.create_payment(self.m2, due=ContributionDue.objects.get(user=self.m2), method="simulation", external_reference="TXA", idempotency_key="k2")

    def test_reject_then_refund_revokes_quitus(self):
        p = self.new_payment(self.m1)
        pay.confirm_payment(p.pk, self.treasurer)
        pay.refund_payment(p.pk, self.treasurer, "erreur")
        self.assertEqual(Quitus.objects.get(user=self.m1).status, "revoked")
        self.assertEqual(fin.summary()["income"], 0)
        self.assertEqual(ContributionDue.objects.get(user=self.m1).status, "unpaid")
        with self.assertRaises(pay.PaymentError):
            pay.confirm_payment(p.pk, self.treasurer)  # un paiement remboursé ne se reconfirme pas

    def test_amount_comes_from_server_and_simulated_success(self):
        self.login(self.m1)
        due = ContributionDue.objects.get(user=self.m1)
        r = self.client.post(reverse("payments:pay_due", args=[due.pk]), {"idempotency_key": "abc", "amount": "1", "method": "tokipay"})
        p = Payment.objects.get()
        self.assertEqual((p.amount, p.method, p.status), (2000, "simulation", "pending"))
        self.assertRedirects(r, reverse("payments:simulate", args=[p.reference]))
        self.client.post(reverse("payments:simulate", args=[p.reference]), {"outcome": "success"})
        p.refresh_from_db()
        self.assertEqual(p.status, "confirmed")
        self.assertTrue(Receipt.objects.filter(payment=p).exists())
        self.assertTrue(Quitus.objects.filter(user=self.m1).exists())
        self.assertEqual(fin.summary()["income"], 2000)

    def test_simulated_failure_and_cancel_then_retry(self):
        self.login(self.m1)
        due = ContributionDue.objects.get(user=self.m1)
        for outcome, status in (("fail", "failed"), ("cancel", "cancelled")):
            self.client.post(reverse("payments:pay_due", args=[due.pk]), {"idempotency_key": f"k-{outcome}"})
            p = Payment.objects.filter(status="pending").get()
            self.client.post(reverse("payments:simulate", args=[p.reference]), {"outcome": outcome})
            p.refresh_from_db()
            self.assertEqual(p.status, status)
            self.assertEqual(ContributionDue.objects.get(pk=due.pk).status, "unpaid")
        self.client.post(reverse("payments:pay_due", args=[due.pk]), {"idempotency_key": "k-final"})
        p = Payment.objects.filter(status="pending").get()
        self.client.post(reverse("payments:simulate", args=[p.reference]), {"outcome": "success"})
        self.assertEqual(ContributionDue.objects.get(pk=due.pk).status, "paid")

    def test_simulation_is_owner_only_once_only_and_can_be_disabled(self):
        p = self.new_payment(self.m1)
        self.login(self.m2)
        self.assertEqual(self.client.post(reverse("payments:simulate", args=[p.reference]), {"outcome": "success"}).status_code, 404)
        self.login(self.m1)
        self.client.post(reverse("payments:simulate", args=[p.reference]), {"outcome": "success"})
        self.client.post(reverse("payments:simulate", args=[p.reference]), {"outcome": "fail"})  # 2e résultat ignoré
        p.refresh_from_db()
        self.assertEqual(p.status, "confirmed")
        p2 = self.new_payment(self.m2, "TXQ")
        self.login(self.m2)
        with override_settings(PAYMENT_SIMULATION_ENABLED=False):
            self.assertEqual(self.client.post(reverse("payments:simulate", args=[p2.reference]), {"outcome": "success"}).status_code, 404)
            with self.assertRaises(pay.PaymentError):
                pay.simulate_outcome(p2.pk, self.m2, "success")

    def test_tokipay_not_configured_fails_cleanly(self):
        due = ContributionDue.objects.get(user=self.m1)
        with self.assertRaises(pay.PaymentError):
            pay.create_payment(self.m1, due=due, method="tokipay", idempotency_key="t1")
        self.assertEqual(Payment.objects.count(), 0)

    def test_idempotent_submission(self):
        due = ContributionDue.objects.get(user=self.m1)
        a, c1 = pay.create_payment(self.m1, due=due, method="simulation", external_reference="Z1", idempotency_key="same")
        b, c2 = pay.create_payment(self.m1, due=due, method="simulation", external_reference="Z1", idempotency_key="same")
        self.assertEqual(a.pk, b.pk)
        self.assertFalse(c2)

    @override_settings()
    def test_webhook_signature_and_replay(self):
        p = self.new_payment(self.m1)
        Payment.objects.filter(pk=p.pk).update(method="tokipay")
        body = json.dumps({"event_id": "e1", "reference": p.reference, "status": "success", "amount": 2000, "currency": "MGA"}).encode()
        url = reverse("payments:webhook", args=["tokipay"])
        os.environ.pop("WEBHOOK_SECRET_TOKIPAY", None)
        self.assertEqual(self.client.post(url, body, content_type="application/json").status_code, 403)
        os.environ["WEBHOOK_SECRET_TOKIPAY"] = "s3cret"
        try:
            self.assertEqual(self.client.post(url, body, content_type="application/json", HTTP_X_SIGNATURE="bad").status_code, 403)
            sig = hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
            self.assertEqual(self.client.post(url, body, content_type="application/json", HTTP_X_SIGNATURE=sig).status_code, 200)
            self.client.post(url, body, content_type="application/json", HTTP_X_SIGNATURE=sig)  # rejeu
        finally:
            os.environ.pop("WEBHOOK_SECRET_TOKIPAY")
        p.refresh_from_db()
        self.assertEqual(p.status, "confirmed")
        self.assertEqual(Receipt.objects.count(), 1)


class AccessControlTests(Base):
    def test_idor_payment_receipt_quitus(self):
        p = self.new_payment(self.m1)
        pay.confirm_payment(p.pk, self.treasurer)
        self.login(self.m2)
        self.assertEqual(self.client.get(reverse("payments:detail", args=[p.reference])).status_code, 404)
        self.assertEqual(self.client.get(reverse("certificates:receipt_pdf", args=[p.receipt.number])).status_code, 404)
        q = Quitus.objects.get()
        self.assertEqual(self.client.get(reverse("certificates:quitus_pdf", args=[q.number])).status_code, 404)
        self.login(self.m1)
        self.assertEqual(self.client.get(reverse("certificates:quitus_pdf", args=[q.number])).status_code, 200)
        self.assertEqual(self.client.get(reverse("certificates:receipt_pdf", args=[p.receipt.number])).status_code, 200)

    def test_gestion_requires_permission(self):
        self.login(self.m1)
        self.assertEqual(self.client.get(reverse("gestion:home")).status_code, 403)
        self.login(self.secretary)
        self.assertEqual(self.client.get(reverse("gestion:payments")).status_code, 403)
        p = self.new_payment(self.m1)
        self.assertEqual(self.client.post(reverse("gestion:payment_confirm", args=[p.reference]), {"received_amount": "2000"}).status_code, 403)
        self.login(self.treasurer)
        self.assertEqual(self.client.post(reverse("gestion:payment_confirm", args=[p.reference]), {"received_amount": "2000"}).status_code, 302)
        self.assertEqual(self.client.get(reverse("gestion:audit")).status_code, 403)  # le trésorier n'a pas accès au journal
        self.login(self.president)
        self.assertEqual(self.client.get(reverse("gestion:audit")).status_code, 200)

    def test_anonymous_redirected_and_pending_user_blocked_from_member_pages(self):
        r = self.client.get(reverse("payments:dues"))
        self.assertEqual(r.status_code, 302)
        pending = make_user("PEN1", status="pending")
        self.login(pending)
        self.assertEqual(self.client.get(reverse("payments:dues")).status_code, 403)

    def test_login_lockout(self):
        for _ in range(6):
            self.client.post(reverse("accounts:login"), {"username": "MEM1", "password": "wrong"})
        r = self.client.post(reverse("accounts:login"), {"username": "MEM1", "password": PWD})
        self.assertEqual(r.status_code, 200)  # verrouillé malgré le bon mot de passe
        self.assertFalse("_auth_user_id" in self.client.session)


def pdf_file(name="a.pdf", content=b"%PDF-1.4 test"):
    return SimpleUploadedFile(name, content, content_type="application/pdf")


class DocumentTests(Base):
    def test_visibility_and_upload_validation(self):
        pub = Document.objects.create(title="Public", file=pdf_file(), visibility="public", uploaded_by=self.secretary)
        priv = Document.objects.create(title="Privé", file=pdf_file(), visibility="members", uploaded_by=self.secretary)
        self.assertEqual(self.client.get(reverse("documents:download", args=[pub.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("documents:download", args=[priv.pk])).status_code, 404)
        self.login(self.m1)
        self.assertEqual(self.client.get(reverse("documents:download", args=[priv.pk])).status_code, 200)
        pub.refresh_from_db()
        self.assertEqual(pub.download_count, 1)
        self.login(self.secretary)
        r = self.client.post(reverse("gestion:document_create"), {"title": "Faux", "doc_type": "cours", "level": "all", "visibility": "public",
                             "status": "published", "file": SimpleUploadedFile("x.pdf", b"MZ not a pdf")})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Document.objects.count(), 2)
        r = self.client.post(reverse("gestion:document_create"), {"title": "Exe", "doc_type": "cours", "level": "all", "visibility": "public",
                             "status": "published", "file": SimpleUploadedFile("x.exe", b"%PDF-1")})
        self.assertEqual(Document.objects.count(), 2)

    def test_private_storage_has_no_public_url(self):
        d = Document.objects.create(title="P", file=pdf_file(), visibility="members")
        with self.assertRaises(ValueError):
            d.file.url


class EventTests(Base):
    def make_event(self, **kw):
        defaults = dict(title="Sortie", description="d", starts_at=timezone.now() + timedelta(days=10), location="L", capacity=1,
                        registration_deadline=timezone.now() + timedelta(days=5), price=0, status="open")
        defaults.update(kw)
        return Event.objects.create(**defaults)

    def test_capacity_and_duplicates(self):
        e = self.make_event()
        r = ev.reserve(e.pk, self.m1)
        self.assertEqual(r.status, "confirmed")
        with self.assertRaises(ev.ReservationError):
            ev.reserve(e.pk, self.m1)
        with self.assertRaises(ev.CapacityError):
            ev.reserve(e.pk, self.m2)

    def test_non_member_blocked_and_closed_event(self):
        e = self.make_event(capacity=5)
        pending = make_user("PEN2", status="pending")
        with self.assertRaises(ev.ReservationError):
            ev.reserve(e.pk, pending)
        closed = self.make_event(registration_deadline=timezone.now() - timedelta(hours=1))
        with self.assertRaises(ev.ReservationError):
            ev.reserve(closed.pk, self.m1)

    def test_ticket_single_use(self):
        e = self.make_event()
        r = ev.reserve(e.pk, self.m1)
        token = r.ticket.token
        ev.check_in(token, self.events_mgr)
        with self.assertRaises(ev.TicketError):
            ev.check_in(token, self.events_mgr)

    def test_paid_event_flow_expiry_and_cancel(self):
        e = self.make_event(price=5000, capacity=1)
        r = ev.reserve(e.pk, self.m1)
        self.assertEqual(r.status, "pending")
        with self.assertRaises(ev.CapacityError):
            ev.reserve(e.pk, self.m2)  # la place est retenue pendant l'attente
        Reservation.objects.filter(pk=r.pk).update(expires_at=timezone.now() - timedelta(minutes=1))
        ev.reserve(e.pk, self.m2)  # délai dépassé : place libérée
        r2 = Reservation.objects.get(user=self.m2)
        p, _ = pay.create_payment(self.m2, reservation=r2, method="simulation", external_reference="EV1", idempotency_key="ev1")
        pay.confirm_payment(p.pk, self.treasurer, received_amount=Decimal("5000"))
        r2.refresh_from_db()
        self.assertEqual(r2.status, "confirmed")
        self.assertTrue(r2.ticket.token)
        self.assertEqual(fin.summary()["income"], 5000)
        ev.cancel_reservation(r2.pk, self.m2, "x")
        r2.ticket.refresh_from_db()
        self.assertEqual(r2.ticket.status, "revoked")

    def test_cancel_deadline(self):
        e = self.make_event(starts_at=timezone.now() + timedelta(hours=3), registration_deadline=timezone.now() + timedelta(hours=1), capacity=3)
        r = ev.reserve(e.pk, self.m1)
        with self.assertRaises(ev.ReservationError):
            ev.cancel_reservation(r.pk, self.m1)


class FinanceTests(Base):
    def make_entry(self, **kw):
        d = dict(reference=fin.new_reference(), kind="expense", category="transport", description="Bus", amount=1000, date=date.today(),
                 responsible=self.treasurer)
        d.update(kw)
        return BudgetEntry.objects.create(**d)

    def test_only_validated_counted_and_immutable(self):
        e = self.make_entry()
        self.assertEqual(fin.summary()["expense"], 0)
        fin.validate_entry(e, self.president)
        self.assertEqual(fin.summary()["expense"], 1000)
        e.refresh_from_db()
        e.description = "triche"
        with self.assertRaises(PermissionError):
            e.save()
        with self.assertRaises(PermissionError):
            e.delete()
        fin.reverse_entry(e, self.treasurer, "erreur de saisie")
        self.assertEqual(fin.summary()["expense"], 0)
        with self.assertRaises(fin.FinanceError):
            fin.reverse_entry(e, self.treasurer, "encore")

    def test_report_workflow_and_versions(self):
        fin.validate_entry(self.make_entry(), self.president)
        start, end = date.today().replace(month=1, day=1), date.today().replace(month=12, day=31)
        r = fin.create_report("Rapport", start, end, self.treasurer)
        with self.assertRaises(fin.FinanceError):
            fin.publish_report(r, self.treasurer)  # doit être validé d'abord
        fin.validate_report(r, self.president)
        fin.publish_report(r, self.treasurer)
        r2 = fin.create_report("Rapport", start, end, self.treasurer)
        self.assertEqual(r2.version, 2)
        self.login(self.m1)
        self.assertEqual(self.client.get(reverse("finance_member:detail", args=[r.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("finance_member:detail", args=[r2.pk])).status_code, 404)  # brouillon non visible
        for name in ("report_pdf", "report_xlsx"):
            self.assertEqual(self.client.get(reverse(f"finance_member:{name}", args=[r.pk])).status_code, 200)


class VerificationAndAuditTests(Base):
    def test_verify_public_page_and_revocation(self):
        p = self.new_payment(self.m1)
        pay.confirm_payment(p.pk, self.treasurer)
        q = Quitus.objects.get()
        url = reverse("verify:check", args=[q.token])
        r = self.client.get(url)
        self.assertContains(r, "Valide")
        self.assertNotContains(r, self.m1.matricule)  # matricule masqué
        from apps.certificates.services import revoke_quitus
        revoke_quitus(q, self.treasurer, "fraude")
        self.assertContains(self.client.get(url), "Révoqué")
        self.assertContains(self.client.get(reverse("verify:check", args=["inconnu"])), "Aucun document")

    def test_audit_log_append_only(self):
        from apps.audit.models import AuditLog
        from apps.audit.services import log
        entry = log(self.admin, "test", "x", new="password=123")
        self.assertEqual(entry.new_value, "[masqué]")
        entry.action = "x"
        with self.assertRaises(PermissionError):
            entry.save()
        with self.assertRaises(PermissionError):
            entry.delete()
        with self.assertRaises(PermissionError):
            AuditLog.objects.all().delete()

    def test_payment_confirmation_is_audited(self):
        from apps.audit.models import AuditLog
        p = self.new_payment(self.m1)
        pay.confirm_payment(p.pk, self.treasurer)
        self.assertTrue(AuditLog.objects.filter(action="validation_paiement", resource=p.reference).exists())


class SmokeTests(Base):
    def test_public_pages(self):
        for name in ("core:home", "core:about", "core:bureau", "core:contact", "publications:list", "events:list", "documents:list",
                     "accounts:login", "accounts:register", "accounts:password_reset"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_member_and_admin_pages(self):
        p = self.new_payment(self.m1)
        pay.confirm_payment(p.pk, self.treasurer)
        self.login(self.m1)
        for name in ("dashboard:home", "memberships:apply", "payments:dues", "payments:list", "certificates:receipt_list", "certificates:quitus_list",
                     "certificates:card", "certificates:card_pdf", "events_member:list", "finance_member:list", "notifications:list",
                     "support:list", "support:create", "accounts:profile", "accounts:password_change"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.login(self.admin)
        for name in ("home", "users", "memberships", "contributions", "contribution_create", "dues", "payments", "quitus", "cards", "events",
                     "event_create", "scan", "finance", "entries", "entry_create", "reports", "report_create", "publications", "publication_create",
                     "comments", "documents", "document_create", "support", "officers", "officer_create", "audit", "settings", "contacts", "broadcast"):
            self.assertEqual(self.client.get(reverse(f"gestion:{name}")).status_code, 200, name)
        self.assertEqual(self.client.get(reverse("gestion:payment_detail", args=[p.reference])).status_code, 200)

    def test_security_headers_and_logout_post_only(self):
        r = self.client.get(reverse("core:home"))
        self.assertIn("Content-Security-Policy", r)
        self.login(self.m1)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)


class SeedDemoTests(TestCase):
    def test_seed_runs_and_is_consistent(self):
        from apps.finance import services as fin
        call_command("seed_demo", members=14, verbosity=0)
        self.assertGreaterEqual(User.objects.filter(matricule__startswith="SOC26-").count(), 14)
        self.assertGreater(Payment.objects.filter(status="confirmed").count(), 0)
        self.assertEqual(Receipt.objects.count(), Payment.objects.filter(status__in=("confirmed", "refunded")).count())
        self.assertGreater(Event.objects.count(), 5)
        self.assertGreater(fin.summary()["income"], 0)
        call_command("seed_demo", members=14, verbosity=0)  # 2e appel : ignoré (idempotent)
        self.assertEqual(User.objects.filter(matricule__startswith="SOC26-").count(), 14)
