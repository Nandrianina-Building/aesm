"""Tests de non-régression ajoutés suite à l'audit pré-production (voir 01_RAPPORT_AUDIT_AESM.md)."""
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings

from apps.core.utils import client_ip
from apps.documents.models import Document, DocumentCategory
from apps.accounts.models import User

from .test_flows import Base, make_user, PWD


class DocumentEditTests(Base):
    """C-06 : modifier un document existant provoquait une erreur 500 (widget de fichier sur stockage privé)."""

    def test_secretary_can_open_edit_form_of_existing_document(self):
        cat, _ = DocumentCategory.objects.get_or_create(name="Cours")
        pdf = SimpleUploadedFile("t.pdf", b"%PDF-1.4\n%test\n", content_type="application/pdf")
        doc = Document.objects.create(title="TD 1", category=cat, file=pdf, status="published", visibility="public")
        self.client.force_login(self.secretary)
        r = self.client.get(f"/gestion/documents/{doc.pk}/modifier/")
        self.assertEqual(r.status_code, 200)


class ClientIpTests(TestCase):
    """H-03 : derrière nginx, REMOTE_ADDR vaut 127.0.0.1 pour tous les visiteurs."""

    def _req(self, **meta):
        return RequestFactory().get("/", **meta)

    @override_settings(TRUST_X_FORWARDED_FOR=False)
    def test_header_ignored_when_not_trusted(self):
        r = self._req(REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="6.6.6.6")
        self.assertEqual(client_ip(r), "127.0.0.1")

    @override_settings(TRUST_X_FORWARDED_FOR=True)
    def test_last_forwarded_value_used_and_spoofing_ignored(self):
        r = self._req(REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="6.6.6.6, 41.204.1.2")
        self.assertEqual(client_ip(r), "41.204.1.2")
        r = self._req(REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="pas une ip")
        self.assertEqual(client_ip(r), "127.0.0.1")


class PasswordResetThrottleTests(TestCase):
    """M-02 : 8 demandes = 8 e-mails (e-mail bombing)."""

    def test_reset_is_rate_limited_per_address(self):
        cache.clear()
        u = User.objects.create_user("RST1", PWD, first_name="A", last_name="B", phone="0341234567", email="rst1@exemple.mg")
        for _ in range(8):
            self.client.post("/compte/mot-de-passe-oublie/", {"email": u.email})
        self.assertLessEqual(len(mail.outbox), 3)
