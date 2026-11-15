"""Jeu de données de démonstration complet (toutes les tables).

    python manage.py seed_demo                 # ~120 membres, cotisations, paiements, événements, finances...
    python manage.py seed_demo --members 300   # plus de volume
    python manage.py seed_demo --force         # ajoute un nouveau lot même si des données existent

Les données passent par les vraies fonctions métier (adhésions, paiements simulés, billets, écritures...) :
elles sont donc cohérentes (reçus, quitus, soldes, numéros). NE PAS utiliser en production.
Mot de passe de tous les comptes : DemoAESM-2026!x
"""
import io
import random
import uuid
from datetime import date, datetime, time, timedelta

from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

PASSWORD = "DemoAESM-2026!x"

FIRST = ["Miora", "Hery", "Tiana", "Fanja", "Nirina", "Lalaina", "Faly", "Voahangy", "Mamy", "Soa", "Rindra", "Haja", "Tojo", "Ony", "Ando",
         "Njaka", "Fenitra", "Aina", "Mialy", "Toky", "Anja", "Volana", "Sitraka", "Santatra", "Mahefa", "Tahina", "Hanitra", "Lova", "Koloina",
         "Fidy", "Nomena", "Riana", "Bakoly", "Hasina", "Narindra", "Mendrika", "Faniry", "Tsiry", "Nantenaina", "Zo", "Kanto", "Elia", "Mirana",
         "Herilala", "Onja", "Tantely", "Vola", "Joro", "Rova", "Sarobidy"]
LAST = ["Rakotoarisoa", "Randrianarisoa", "Rasolofo", "Andrianjafy", "Rakotomalala", "Ratsimbazafy", "Razafindrakoto", "Rabemananjara",
        "Ravelonarivo", "Andriamanana", "Rajaonarison", "Randriamampionona", "Rasoanaivo", "Raharimalala", "Rakotonirina", "Ramanantsoa",
        "Rasamoelina", "Razafimahefa", "Ravoavy", "Andrianasolo", "Rakotobe", "Ranaivo", "Rahaingo", "Randrianantenaina", "Razanamahefa",
        "Rakotovao", "Randriambololona", "Rasolonjatovo", "Ratovoson", "Raveloson", "Andriantsoa", "Rakoto", "Rabary", "Ramarosaona"]

PUB_TEXT = [
    "L'AESM poursuit sa mission d'accompagnement des étudiants en sociologie, avec de nouvelles activités pédagogiques et associatives.",
    "Les inscriptions sont ouvertes à tous les membres à jour de leur cotisation. Pensez à vérifier votre situation dans votre espace personnel.",
    "Cette initiative est le fruit d'un travail collectif du bureau et des étudiants volontaires. Merci à toutes et à tous pour votre engagement.",
    "Les modalités pratiques, les horaires et le lieu sont précisés ci-dessous. Les places étant limitées, réservez rapidement.",
    "Pour toute question, contactez le secrétariat via la page Contact ou ouvrez une réclamation depuis votre espace membre.",
]
COMMENTS = ["Très bonne initiative, merci au bureau !", "Est-ce que les étudiants de L1 peuvent participer ?", "Information utile, j'ai partagé avec ma promotion.",
            "Pouvez-vous préciser l'horaire exact ?", "Bravo pour l'organisation, on attend la suite.", "Merci pour la transparence sur les comptes.",
            "Y aura-t-il un support de cours disponible après ?", "Je confirme ma participation.", "Belle annonce, hâte d'y être !",
            "Serait-il possible d'avoir ce document en version imprimée ?", "Super, c'est exactement ce qu'il nous fallait.", "Merci à l'équipe du secrétariat."]


def aware(day, rnd):
    return timezone.make_aware(datetime.combine(day, time(rnd.randint(7, 20), rnd.randint(0, 59))))


def rand_day(rnd, start, end):
    if end <= start:
        return start
    return start + timedelta(days=rnd.randint(0, (end - start).days))


def make_pdf(title, lines):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(60, 780, title[:70])
    c.setFont("Helvetica", 11)
    y = 740
    for line in lines:
        c.drawString(60, y, line[:95])
        y -= 18
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(60, 60, "Document de démonstration - AESM")
    c.showPage()
    c.save()
    return buf.getvalue()


class Command(BaseCommand):
    help = "Remplit toutes les tables avec un jeu de données de démonstration complet."

    def add_arguments(self, parser):
        parser.add_argument("--members", type=int, default=120)
        parser.add_argument("--force", action="store_true")

    # ------------------------------------------------------------------
    def handle(self, *args, **opts):
        from apps.accounts.models import User
        call_command("init_aesm", verbosity=0)
        if User.objects.filter(matricule__startswith="SOC26-").exists() and not opts["force"]:
            self.stdout.write(self.style.WARNING("Données de démonstration déjà présentes (utilisez --force pour en ajouter)."))
            return
        self.rnd = random.Random(2026 if not opts["force"] else random.randint(1, 10**6))
        self.today = date.today()
        self.year = self.today.year
        self.pwd_hash = make_password(PASSWORD)
        self.n_members = max(opts["members"], 12)
        steps = [self.settings_and_staff, self.officers, self.contributions, self.members, self.dues_and_payments, self.events,
                 self.publications, self.documents, self.finance, self.support, self.misc]
        for step in steps:
            self.stdout.write(f"... {step.__name__}")
            step()
        self.report()

    # ------------------------------------------------------------------ utilitaires
    def user(self, matricule, last, first, status, roles=()):
        from apps.accounts.models import Role, User
        sex = self.rnd.choice("FM")
        phones = getattr(self, "_phones", set())
        while True:
            phone = self.rnd.choice(["032", "033", "034", "038"]) + "".join(self.rnd.choice("0123456789") for _ in range(7))
            if phone not in phones and not User.objects.filter(phone=phone).exists():
                break
        phones.add(phone)
        self._phones = phones
        email = None
        if self.rnd.random() < 0.65:
            email = f"{first.lower()}.{last.lower()}.{matricule.lower()}@exemple.mg"
        u = User(matricule=matricule, last_name=last, first_name=first, phone=phone, sex=sex, email=email, email_verified=bool(email) and self.rnd.random() < 0.7,
                 account_status=status, password=self.pwd_hash, is_active=status != "disabled")
        u.save()
        for code in roles:
            u.roles.add(Role.objects.get(code=code))
        return u

    def backdate_payment(self, p, day):
        from apps.certificates.models import Quitus, Receipt
        from apps.finance.models import BudgetEntry
        from apps.payments.models import ContributionDue, Payment
        dt = aware(day, self.rnd)
        Payment.objects.filter(pk=p.pk).update(created_at=dt, updated_at=dt, confirmed_at=dt if p.status == "confirmed" else None)
        BudgetEntry.objects.filter(payment=p).update(date=day)
        Receipt.objects.filter(payment=p).update(issued_at=dt)
        Quitus.objects.filter(payment=p).update(issued_at=dt)
        if p.due_id:
            ContributionDue.objects.filter(pk=p.due_id, status="paid").update(paid_at=dt)

    def pay(self, user, *, due=None, reservation=None, outcome="paid", day=None):
        from apps.payments import services as pay
        p, _ = pay.create_payment(user, due=due, reservation=reservation, method="simulation", idempotency_key=f"seed-{uuid.uuid4().hex}")
        if outcome == "paid":
            p = pay.confirm_payment(p.pk, by=None, source="simulation")
        elif outcome == "failed":
            p = pay.reject_payment(p.pk, None, "Échec simulé")
        elif outcome == "cancelled":
            from apps.payments.models import Payment
            Payment.objects.filter(pk=p.pk).update(status="cancelled", failure_reason="Annulé par le membre")
            p.refresh_from_db()
        elif outcome == "verifying":
            from apps.payments.models import Payment
            Payment.objects.filter(pk=p.pk).update(status="verifying")
            p.refresh_from_db()
        if day:
            self.backdate_payment(p, day)
        return p

    # ------------------------------------------------------------------ étapes
    def settings_and_staff(self):
        from apps.core.models import SiteSetting
        values = {"opening_balance": "150000", "contact_email": "contact@aesm.mg", "contact_phone": "+261 34 00 000 00",
                  "contact_address": "Faculté DEGS, Université d'Antananarivo, Ankatso, Antananarivo 101", "facebook_url": "https://facebook.com/aesm.madagascar"}
        for k, v in values.items():
            SiteSetting.objects.update_or_create(key=k, defaults={"value": v})
        spec = [("ADMIN01", "Rakotoarisoa", "Tiana", "super_admin"), ("PRES01", "Randrianarisoa", "Hery", "president"),
                ("TRES01", "Rasoanaivo", "Fanja", "treasurer"), ("SECR01", "Rabemananjara", "Miora", "secretary"),
                ("SECR02", "Ravelonarivo", "Lalaina", "secretary"), ("EVEN01", "Andriamanana", "Faly", "event_manager")]
        from apps.accounts.models import User
        for mat, last, first, role in spec:
            if not User.objects.filter(matricule=mat).exists():
                self.user(mat, last, first, "active", (role,))
        self.admin = User.objects.get(matricule="ADMIN01")
        self.pres = User.objects.get(matricule="PRES01")
        self.treas = User.objects.get(matricule="TRES01")
        self.sec = User.objects.get(matricule="SECR01")
        self.sec2 = User.objects.get(matricule="SECR02")
        self.evt = User.objects.get(matricule="EVEN01")

    def officers(self):
        from apps.core.models import Officer
        if Officer.objects.exists():
            return
        cur = [("Président", "Randrianarisoa", "Hery"), ("Vice-présidente", "Rakotomalala", "Soa"), ("Secrétaire générale", "Rabemananjara", "Miora"),
               ("Secrétaire adjoint", "Ravelonarivo", "Lalaina"), ("Trésorière", "Rasoanaivo", "Fanja"), ("Trésorier adjoint", "Rajaonarison", "Mamy"),
               ("Responsable communication", "Ratsimbazafy", "Nirina"), ("Responsable événementiel", "Andriamanana", "Faly"),
               ("Commissaire aux comptes", "Raharimalala", "Voahangy")]
        for fn, last, first in cur:
            Officer.objects.create(last_name=last, first_name=first, function=fn, mandate_start=date(self.year, 1, 15),
                                   description=f"{fn} de l'AESM, étudiant(e) en sociologie, engagé(e) pour la vie associative et l'entraide pédagogique.")
        old = [("Président", "Rakotonirina", "Tojo"), ("Secrétaire générale", "Rasamoelina", "Ony"), ("Trésorier", "Razafimahefa", "Ando"), ("Vice-président", "Andrianasolo", "Njaka")]
        for fn, last, first in old:
            Officer.objects.create(last_name=last, first_name=first, function=fn, mandate_start=date(self.year - 3, 2, 1),
                                   mandate_end=date(self.year - 1, 12, 31), is_archived=True, description="Ancien membre du bureau.")

    def contributions(self):
        from apps.payments.models import ContributionType
        y = self.year
        spec = [
            ("Adhésion annuelle", "Frais d'adhésion à l'AESM pour les nouveaux membres.", 2000, str(y), date(y, 1, 1), date(y, 12, 31), "adhesion", "new_members", True),
            ("Cotisation annuelle", "Cotisation de fonctionnement de l'association.", 5000, str(y), date(y, 1, 1), date(y, 12, 31), "adhesion", "all_members", True),
            ("Cotisation sortie pédagogique", "Participation aux frais de la sortie pédagogique annuelle.", 10000, f"Sortie {y}", self.today - timedelta(days=20),
             self.today + timedelta(days=25), "speciale", "all_members", False),
            ("Fonds de solidarité", "Contribution exceptionnelle pour le fonds de solidarité étudiante.", 3000, f"Solidarité {y}", self.today - timedelta(days=60),
             self.today + timedelta(days=40), "exceptionnelle", "selected", False),
        ]
        self.contribs = {}
        for name, desc, amount, period, start, end, cat, aud, quitus in spec:
            self.contribs[name], _ = ContributionType.objects.get_or_create(name=name, defaults=dict(
                description=desc, amount=amount, period_label=period, start_date=start, end_date=end, category=cat, audience=aud,
                issue_quitus=quitus, created_by=self.treas))
        self.c2025, _ = ContributionType.objects.get_or_create(name=f"Cotisation annuelle {y - 1}", defaults=dict(
            description="Cotisation de l'année précédente.", amount=4000, period_label=str(y - 1), start_date=date(y - 1, 1, 1),
            end_date=date(y - 1, 12, 31), category="adhesion", audience="all_members", is_active=False, created_by=self.treas))

    def members(self):
        from apps.accounts.models import User
        from apps.memberships import services as ms
        from apps.memberships.models import Membership
        n = self.n_members
        start = User.objects.filter(matricule__startswith="SOC26-").count()
        plan = (["active"] * int(n * 0.74) + ["pending"] * int(n * 0.09) + ["verifying"] * int(n * 0.03) + ["refused"] * int(n * 0.05)
                + ["suspended"] * int(n * 0.04))
        plan += ["none"] * (n - len(plan))
        self.rnd.shuffle(plan)
        self.active, self.suspended, self.others = [], [], []
        self.had2025 = set()
        refusals = ["Dossier incomplet : justificatif d'inscription manquant.", "Matricule non reconnu par la faculté.", "Doublon avec un compte existant."]
        jan1 = date(self.year, 1, 1)
        for i, kind in enumerate(plan, start=start + 1):
            last, first = self.rnd.choice(LAST), self.rnd.choice(FIRST)
            status = {"active": "pending", "suspended": "pending", "pending": "pending", "verifying": "pending", "refused": "pending", "none": "pending"}[kind]
            u = self.user(f"SOC26-{i:04d}", last, first, status)
            created = aware(rand_day(self.rnd, jan1, self.today - timedelta(days=3)), self.rnd)
            User.objects.filter(pk=u.pk).update(date_joined=created)
            if kind == "none":
                self.others.append(u)
                continue
            m = ms.submit_application(u, "Étudiant(e) en sociologie, je souhaite rejoindre l'association.")
            if kind in ("active", "suspended"):
                ms.accept(m, self.rnd.choice([self.sec, self.sec2]))
                if kind == "suspended":
                    m.refresh_from_db()
                    ms.suspend(m, self.sec, "Comportement contraire au règlement intérieur.")
                    self.suspended.append(u)
                else:
                    self.active.append(u)
                m.refresh_from_db()
                ends = created.date() + timedelta(days=365)
                Membership.objects.filter(pk=m.pk).update(starts_on=created.date(), ends_on=ends, submitted_at=created, reviewed_at=created + timedelta(days=2),
                                                         created_at=created)
                if self.rnd.random() < 0.3:  # adhésion de l'année précédente (expirée)
                    Membership.objects.create(user=u, year=self.year - 1, status="expired", submitted_at=created - timedelta(days=365),
                                              starts_on=created.date() - timedelta(days=365), ends_on=created.date() - timedelta(days=1), reviewed_by=self.sec)
                    self.had2025.add(u.pk)
            elif kind == "verifying":
                ms.set_verifying(m, self.sec, "Merci de joindre une copie de votre carte d'étudiant.")
                self.others.append(u)
            elif kind == "refused":
                ms.refuse(m, self.sec, self.rnd.choice(refusals))
                self.others.append(u)
            else:
                self.others.append(u)
            Membership.objects.filter(pk=m.pk).update(submitted_at=created, created_at=created)
        self.active = [User.objects.get(pk=u.pk) for u in self.active]
        self.suspended = [User.objects.get(pk=u.pk) for u in self.suspended]
        self.stdout.write(f"    {len(self.active)} membres actifs, {len(self.suspended)} suspendus, {len(self.others)} autres")

    def dues_and_payments(self):
        from apps.payments import services as pay
        from apps.payments.models import ContributionDue
        solidarity = self.contribs["Fonds de solidarité"]
        solidarity.target_users.set(self.rnd.sample(self.active, min(len(self.active), max(10, len(self.active) // 2))))
        for c in self.contribs.values():
            pay.generate_dues_for_contribution(c)
        for u in self.active:
            if u.pk in self.had2025:
                pay._create_due(u, self.c2025)
        dues = list(ContributionDue.objects.filter(user__in=self.active).select_related("contribution", "user"))
        self.rnd.shuffle(dues)
        stats = {}
        for due in dues:
            c = due.contribution
            r = self.rnd.random()
            last_day = min(self.today, c.end_date)
            day = rand_day(self.rnd, max(c.start_date, self.today - timedelta(days=300)), last_day)
            if c.pk == self.c2025.pk:
                outcome = "paid" if r < 0.65 else "unpaid"
                day = rand_day(self.rnd, date(self.year - 1, 2, 1), date(self.year - 1, 12, 15))
            elif r < 0.60:
                outcome = "paid"
            elif r < 0.68:
                outcome = "pending"
            elif r < 0.72:
                outcome = "failed"
            elif r < 0.76:
                outcome = "cancelled"
            elif r < 0.79:
                outcome = "verifying"
            elif r < 0.83:
                outcome = "waived"
            else:
                outcome = "unpaid"
            stats[outcome] = stats.get(outcome, 0) + 1
            try:
                if outcome == "waived":
                    pay.waive_due(due, self.treas, self.rnd.choice(["Étudiant boursier", "Difficultés financières attestées", "Membre du bureau"]))
                elif outcome != "unpaid":
                    self.pay(due.user, due=due, outcome=outcome, day=day)
            except pay.PaymentError as exc:
                self.stdout.write(f"    ignoré : {exc}")
        # quelques remboursements et une révocation de quitus
        from apps.certificates.models import Quitus
        from apps.certificates.services import revoke_quitus
        from apps.payments.models import Payment
        confirmed = list(Payment.objects.filter(status="confirmed", due__isnull=False)[:60])
        for p in self.rnd.sample(confirmed, min(4, len(confirmed))):
            pay.refund_payment(p.pk, self.treas, "Paiement en double signalé par le membre")
        q = Quitus.objects.filter(status="valid").first()
        if q:
            revoke_quitus(q, self.treas, "Erreur de délivrance corrigée")
        self.stdout.write(f"    cotisations : {stats}")

    def _event_images(self, e, idx):
        """Affiche + galerie de démonstration (copie d'images déjà présentes dans media/publications)."""
        import shutil
        from django.conf import settings
        from apps.events.models import EventImage
        src = sorted((settings.MEDIA_ROOT / "publications").glob("demo-*.jpg")) if hasattr(settings.MEDIA_ROOT, "glob") else []
        if not src:
            return
        dest = settings.MEDIA_ROOT / "events"
        dest.mkdir(parents=True, exist_ok=True)
        n = 1 + idx % 3  # 1 à 3 images
        for k in range(n):
            f = src[(idx * 3 + k) % len(src)]
            name = f"demo-ev-{idx}-{k}.jpg"
            shutil.copyfile(f, dest / name)
            if k == 0:
                e.image = f"events/{name}"
                e.save(update_fields=["image"])
            else:
                EventImage.objects.create(event=e, image=f"events/{name}", position=k)

    def events(self):
        from apps.events import services as ev
        from apps.events.models import Event, Reservation
        from apps.payments.models import Payment
        now = timezone.now()
        D = timedelta
        specs = [  # titre, décalage jours, prix, capacité, membres seulement, statut, visibilité, catégorie, taux de remplissage, taux payé
            ("Conférence : Sociologie et transformations sociales à Madagascar", -75, 0, 120, False, "closed", "public", "Conférence", 0.6, 1),
            ("Sortie de terrain à Ambohimanga", -40, 15000, 40, True, "closed", "members", "Sortie", 0.9, 0.95),
            ("Atelier de méthodologie d'enquête", -20, 5000, 30, True, "closed", "members", "Atelier", 0.8, 0.95),
            ("Table ronde : jeunesse et emploi", -5, 0, 70, False, "closed", "public", "Débat", 0.7, 1),
            ("Journée d'intégration des nouveaux membres", 12, 0, 80, True, "open", "members", "Vie associative", 0.5, 1),
            ("Voyage pédagogique à Antsirabe", 35, 45000, 25, True, "open", "members", "Sortie", 1.3, 1),
            ("Soirée culturelle de l'AESM", 50, 10000, 150, False, "open", "public", "Culture", 0.3, 0.8),
            ("Séminaire sur les rites funéraires malgaches", 20, 0, 60, False, "open", "public", "Séminaire", 0.55, 1),
            ("Formation SPSS et traitement de données", 8, 8000, 20, True, "open", "members", "Formation", 0.8, 0.85),
            ("Assemblée générale ordinaire", 70, 0, 200, True, "draft", "members", "Vie associative", 0, 1),
            ("Tournoi inter-niveaux de football", 25, 0, 50, False, "cancelled", "public", "Sport", 0.2, 1),
        ]
        counts = {"reservations": 0, "tickets_used": 0}
        for title, off, price, cap, mem_only, status, vis, cat, fill, paid_rate in specs:
            if Event.objects.filter(title=title).exists():
                continue
            starts = now + D(days=off)
            deadline = starts - D(days=2) if off > 2 else starts - D(days=2)
            if title.startswith("Formation SPSS"):
                deadline = now + D(days=2)
            e = Event.objects.create(
                title=title, category=cat, starts_at=starts, location=self.rnd.choice(["Amphi A, Ankatso", "Salle des conférences, DEGS", "Centre culturel d'Antananarivo", "Ambohimanga", "Antsirabe"]),
                description=f"{title}. Une activité de l'AESM ouverte aux étudiants en sociologie. " + self.rnd.choice(PUB_TEXT), capacity=cap, price=price,
                registration_deadline=deadline, members_only=mem_only, visibility=vis, status=status,
                conditions="Être à jour de ses cotisations." if mem_only else "")
            self._event_images(e, specs.index((title, off, price, cap, mem_only, status, vis, cat, fill, paid_rate)))
            if status in ("draft", "cancelled") or not self.active:
                continue
            target = min(len(self.active), int(cap * fill)) if fill <= 1 else len(self.active)
            for u in self.rnd.sample(self.active, target):
                try:
                    res = ev.reserve(e.pk, u, by_admin=True)
                except (ev.CapacityError, ev.ReservationError):
                    continue
                counts["reservations"] += 1
                created = aware((starts - D(days=self.rnd.randint(3, 25))).date(), self.rnd)
                if res.status == Reservation.PENDING:
                    r = self.rnd.random()
                    if r < paid_rate:
                        p = self.pay(u, reservation=res, outcome="paid")
                        self.backdate_payment(p, created.date())
                    elif r < paid_rate + 0.07:
                        Reservation.objects.filter(pk=res.pk).update(expires_at=now - D(hours=2))  # sera expirée
                Reservation.objects.filter(pk=res.pk).update(created_at=created)
            # annulations
            confirmed = list(e.reservations.filter(status="confirmed"))
            for res in self.rnd.sample(confirmed, int(len(confirmed) * 0.07)):
                ev.cancel_reservation(res.pk, self.evt, "Annulation à la demande du membre", enforce_deadline=False)
                pay_obj = Payment.objects.filter(reservation=res, status="confirmed").first()
                if pay_obj and self.rnd.random() < 0.5:
                    from apps.payments import services as pay
                    pay.refund_payment(pay_obj.pk, self.treas, "Annulation de la réservation")
            # présence pour les événements passés
            if off < 0:
                for res in e.reservations.filter(status="confirmed").select_related("ticket"):
                    if hasattr(res, "ticket") and self.rnd.random() < 0.78:
                        try:
                            ev.check_in(res.ticket.token, self.evt)
                            counts["tickets_used"] += 1
                        except ev.TicketError:
                            pass
        print_ = ev.expire_reservations()
        self.stdout.write(f"    {counts}, {print_} réservation(s) expirée(s)")

    def publications(self):
        from apps.publications.models import Comment, CommentReport, Like, Publication, PublicationCategory
        if Publication.objects.exists():
            return
        cats = {c.name: c for c in PublicationCategory.objects.all()}
        now = timezone.now()
        D = timedelta
        # titre, type, catégorie, visibilité, statut, décalage (jours), épinglée
        specs = [
            ("Bienvenue sur la nouvelle plateforme de l'AESM", "annonce", "Vie associative", "public", "published", -90, True),
            ("Ouverture des adhésions pour l'année universitaire", "annonce", "Administration", "public", "published", -80, True),
            ("Calendrier des examens du premier semestre", "pedagogique", "Pédagogie", "members", "published", -60, False),
            ("Compte rendu de l'assemblée générale", "communique", "Vie associative", "members", "published", -55, False),
            ("Appel à bénévoles pour la sortie de terrain", "appel", "Événements", "members", "published", -45, False),
            ("Avis important : modification des horaires de la bibliothèque", "avis", "Administration", "public", "published", -30, False),
            ("Retour sur la conférence « Sociologie et transformations sociales »", "actualite", "Événements", "public", "published", -28, False),
            ("Nouveaux supports de cours disponibles", "pedagogique", "Pédagogie", "members", "published", -21, False),
            ("Résultats du concours d'éloquence", "actualite", "Vie associative", "public", "published", -14, False),
            ("Rappel : cotisation annuelle à régler avant la fin de l'année", "annonce", "Administration", "members", "published", -10, True),
            ("Inscriptions ouvertes : voyage pédagogique à Antsirabe", "evenement", "Événements", "members", "published", -7, False),
            ("Atelier SPSS : dernières places", "evenement", "Pédagogie", "members", "published", -3, False),
            ("Publication du rapport financier du semestre", "communique", "Administration", "members", "published", -2, False),
            ("Soirée culturelle : programme complet", "evenement", "Événements", "public", "scheduled", 5, False),
            ("Brouillon : règlement intérieur révisé", "administrative", "Administration", "members", "draft", 0, False),
            ("Ancienne annonce : inscriptions 2025", "annonce", "Administration", "public", "archived", -400, False),
        ]
        live = []
        for title, kind, cat, vis, status, off, pinned in specs:
            p = Publication.objects.create(
                title=title, kind=kind, category=cats.get(cat), visibility=vis, status=status, pinned=pinned, author=self.rnd.choice([self.sec, self.sec2]),
                summary=self.rnd.choice(PUB_TEXT)[:150], body="\n\n".join(self.rnd.sample(PUB_TEXT, 3)), publish_at=None if status == "draft" else now + D(days=off),
                comments_enabled=self.rnd.random() < 0.9)
            Publication.objects.filter(pk=p.pk).update(created_at=now + D(days=off - 1))
            if status == "published":
                live.append(p)
        pool = self.active or []
        for p in live:
            for u in self.rnd.sample(pool, min(len(pool), self.rnd.randint(3, 40))):
                Like.objects.get_or_create(publication=p, user=u)
            if p.comments_enabled:
                for u in self.rnd.sample(pool, min(len(pool), self.rnd.randint(0, 7))):
                    c = Comment.objects.create(publication=p, user=u, body=self.rnd.choice(COMMENTS), is_hidden=self.rnd.random() < 0.03,
                                               edited=self.rnd.random() < 0.1)
                    if self.rnd.random() < 0.08 and pool:
                        reporter = self.rnd.choice(pool)
                        if reporter.pk != u.pk:
                            CommentReport.objects.get_or_create(comment=c, user=reporter)

    def documents(self):
        from apps.documents.models import Document, DocumentCategory
        if Document.objects.exists():
            return
        cats = {c.name: c for c in DocumentCategory.objects.all()}
        courses = [("Introduction à la sociologie", "L1"), ("Histoire de la pensée sociologique", "L1"), ("Sociologie de la famille", "L2"),
                   ("Sociologie rurale et développement", "L2"), ("Anthropologie sociale de Madagascar", "L2"), ("Sociologie politique", "L3"),
                   ("Sociologie du travail et des organisations", "L3"), ("Démographie sociale", "L3"), ("Sociologie urbaine", "M1"),
                   ("Sociologie des religions", "M1"), ("Théories sociologiques contemporaines", "M1"), ("Sociologie du développement durable", "M2"),
                   ("Séminaire de recherche", "M2"), ("Méthodes qualitatives d'enquête", "L3"), ("Méthodes quantitatives et statistiques", "L3")]
        kinds = [("cours", "Cours", "Cours complet"), ("td", "Travaux dirigés", "Fiche de TD"), ("examen", "Examens", "Sujet d'examen"),
                 ("corrige", "Examens", "Corrigé")]
        n = 0
        for name, level in courses:
            for dtype, cat, label in self.rnd.sample(kinds, 2):
                title = f"{label} - {name}"
                pdf = make_pdf(title, [f"Niveau : {level}", f"Type : {label}", "", "Plan :", "1. Introduction et définitions", "2. Auteurs et courants", "3. Études de cas à Madagascar",
                                       "4. Conclusion et bibliographie"])
                d = Document(title=title, description=f"{label} de {name} ({level}). Support de démonstration.", doc_type=dtype, category=cats.get(cat), level=level,
                             visibility="public" if self.rnd.random() < 0.25 else "members", download_count=self.rnd.randint(0, 400),
                             status="archived" if self.rnd.random() < 0.07 else "published", uploaded_by=self.rnd.choice([self.sec, self.sec2]))
                d.file.save(f"d{n}.pdf", ContentFile(pdf), save=False)
                d.save()
                n += 1
        for title, dtype, cat in [("Guide de l'étudiant en sociologie", "formation", "Méthodologie"), ("Rapport d'activités de l'AESM", "rapport", "Administratif"),
                                  ("Statuts de l'AESM", "administratif", "Administratif"), ("Règlement intérieur", "administratif", "Administratif"),
                                  ("Formulaire d'adhésion", "administratif", "Administratif"), ("Modèle de rapport de stage", "formation", "Méthodologie")]:
            d = Document(title=title, description=f"{title} - document de démonstration.", doc_type=dtype, category=cats.get(cat), level="all",
                         visibility="public", download_count=self.rnd.randint(20, 600), uploaded_by=self.sec)
            d.file.save(f"d{n}.pdf", ContentFile(make_pdf(title, ["Document de démonstration."])), save=False)
            d.save()
            n += 1

    def finance(self):
        from apps.finance import services as fin
        from apps.finance.models import BudgetEntry
        incomes = [("dons", "Don d'un ancien étudiant"), ("dons", "Don de la promotion L3"), ("dons", "Don d'un partenaire associatif"),
                   ("contributions", "Contribution exceptionnelle - vente de T-shirts"), ("contributions", "Contribution - tombola"),
                   ("autres_recettes", "Vente de photocopies de cours"), ("autres_recettes", "Recettes de la buvette")]
        expenses = [("organisation", "Collation conférence"), ("organisation", "Location de matériel de sonorisation"), ("organisation", "Banderole et affiches"),
                    ("organisation", "Rafraîchissements table ronde"), ("transport", "Location de bus sortie Ambohimanga"), ("transport", "Carburant mission terrain"),
                    ("transport", "Taxi-brousse - repérage Antsirabe"), ("fournitures", "Papeterie et cahiers"), ("fournitures", "Cartouches d'encre"),
                    ("fournitures", "Badges et lanyards"), ("communication", "Impression d'affiches"), ("communication", "Crédit internet et téléphone"),
                    ("communication", "Frais d'hébergement du site"), ("location", "Location de salle - assemblée générale"), ("location", "Location de salle - atelier"),
                    ("autres_depenses", "Frais bancaires et mobile money"), ("autres_depenses", "Fournitures de nettoyage")]
        jan1 = date(self.year, 1, 1)
        entries = []
        for kind, pool in (("income", incomes), ("expense", expenses)):
            for _ in range(3 if kind == "income" else 3):
                for cat, desc in pool:
                    amount = self.rnd.randrange(5000, 120000 if kind == "expense" else 80000, 500)
                    day = rand_day(self.rnd, jan1, self.today)
                    e = BudgetEntry.objects.create(reference=fin.new_reference(), kind=kind, category=cat, description=desc, amount=amount, date=day,
                                                   responsible=self.treas, status="pending")
                    entries.append(e)
        self.rnd.shuffle(entries)
        validated = []
        for e in entries:
            r = self.rnd.random()
            if r < 0.72:
                fin.validate_entry(e, self.pres)
                validated.append(e)
            elif r < 0.80:
                fin.reject_entry(e, self.pres, "Justificatif manquant")
        for e in self.rnd.sample(validated, min(4, len(validated))):
            fin.reverse_entry(e, self.treas, "Erreur de saisie du montant")
        y = self.year
        h1 = fin.create_report(f"Rapport financier - 1er semestre {y}", date(y, 1, 1), date(y, 6, 30), self.treas)
        fin.validate_report(h1, self.pres)
        fin.publish_report(h1, self.treas)
        fin.create_report(f"Rapport financier - 1er semestre {y} (révisé)", date(y, 1, 1), date(y, 6, 30), self.treas)  # v2 brouillon
        q3 = fin.create_report(f"Rapport financier - 3e trimestre {y}", date(y, 7, 1), date(y, 9, 30), self.treas)
        fin.validate_report(q3, self.pres)
        oct_ = fin.create_report(f"Rapport financier - octobre {y}", date(y, 10, 1), date(y, 10, 31), self.treas)
        fin.validate_report(oct_, self.pres)
        fin.publish_report(oct_, self.treas)
        fin.create_report(f"Rapport annuel {y} (provisoire)", date(y, 1, 1), date(y, 12, 31), self.treas)

    def support(self):
        from apps.support.models import SupportMessage, SupportTicket
        if SupportTicket.objects.exists() or not self.active:
            return
        spec = [("paiement", "Mon paiement n'apparaît pas", "J'ai payé ma cotisation mais le statut est toujours en attente."),
                ("infos", "Erreur sur mon numéro de téléphone", "Mon numéro a été mal saisi lors de l'inscription, pouvez-vous le corriger ?"),
                ("quitus", "Quitus introuvable", "Je n'arrive pas à télécharger mon quitus après paiement."),
                ("reservation", "Place confirmée mais pas de billet", "Ma réservation est confirmée mais je ne vois pas le billet PDF."),
                ("connexion", "Impossible de me connecter", "Mon compte est verrouillé après plusieurs essais."),
                ("autre", "Demande d'attestation d'adhésion", "J'aurais besoin d'une attestation pour mon dossier de bourse."),
                ("paiement", "Remboursement demandé", "J'ai payé deux fois la même cotisation."),
                ("reservation", "Annulation de réservation", "Je ne peux plus venir à la sortie, comment annuler ?")]
        statuses = ["pending", "in_progress", "resolved", "resolved", "rejected", "closed", "pending", "in_progress"]
        now = timezone.now()
        for i in range(16):
            reason, subject, desc = spec[i % len(spec)]
            u = self.rnd.choice(self.active)
            status = statuses[i % len(statuses)]
            t = SupportTicket.objects.create(user=u, reason=reason, subject=subject, description=desc, status=status,
                                             assigned_to=None if status == "pending" else self.rnd.choice([self.sec, self.sec2]))
            created = now - timedelta(days=self.rnd.randint(1, 60))
            SupportTicket.objects.filter(pk=t.pk).update(created_at=created)
            if status != "pending":
                SupportMessage.objects.create(ticket=t, author=t.assigned_to, from_staff=True, body="Bonjour, nous examinons votre demande et revenons vers vous rapidement.")
            if status in ("resolved", "closed"):
                SupportMessage.objects.create(ticket=t, author=u, from_staff=False, body="Merci, c'est bien résolu de mon côté.")
            if status == "rejected":
                SupportMessage.objects.create(ticket=t, author=t.assigned_to, from_staff=True, body="Après vérification, aucune anomalie n'a été constatée.")

    def misc(self):
        from apps.accounts.models import User
        from apps.core.models import ContactMessage
        from apps.notifications.models import Notification
        from apps.notifications.services import notify_many
        members = User.objects.filter(account_status="active")
        for title, msg in [("Rappel : cotisation annuelle", "N'oubliez pas de régler votre cotisation annuelle avant le 31 décembre."),
                           ("Nouveau : rapports financiers en ligne", "Les rapports financiers publiés sont consultables depuis votre espace."),
                           ("Réunion d'information", "Une réunion d'information aura lieu prochainement, restez attentifs aux annonces.")]:
            notify_many(members, "annonce", title, msg)
        ids = list(Notification.objects.values_list("pk", flat=True))
        self.rnd.shuffle(ids)
        for i in range(0, int(len(ids) * 0.55), 500):
            Notification.objects.filter(pk__in=ids[i:i + 500]).update(is_read=True)
        subjects = ["Demande d'information sur l'adhésion", "Partenariat avec une association", "Invitation à un colloque", "Problème d'accès au site",
                    "Demande de supports de cours", "Candidature pour rejoindre le bureau"]
        for i in range(12):
            first, last = self.rnd.choice(FIRST), self.rnd.choice(LAST)
            ContactMessage.objects.create(name=f"{first} {last}", email=f"{first.lower()}.{last.lower()}@exemple.mg", subject=self.rnd.choice(subjects),
                                          message="Bonjour, je souhaite obtenir plus d'informations. Merci de me répondre dès que possible.",
                                          is_handled=self.rnd.random() < 0.5)

    # ------------------------------------------------------------------
    def report(self):
        from django.apps import apps
        self.stdout.write(self.style.SUCCESS("\nDonnées de démonstration créées. Effectifs par table :"))
        for model in sorted(apps.get_models(), key=lambda m: (m._meta.app_label, m.__name__)):
            if model._meta.app_label in ("accounts", "audit", "certificates", "core", "documents", "events", "finance", "memberships", "notifications",
                                         "payments", "publications", "support"):
                self.stdout.write(f"  {model._meta.app_label}.{model.__name__:<24}{model.objects.count():>6}")
        self.stdout.write(self.style.WARNING(f"\nMot de passe de tous les comptes : {PASSWORD}\nResponsables : ADMIN01, PRES01, TRES01, SECR01, SECR02, EVEN01 · Membres : SOC26-0001 …"))
