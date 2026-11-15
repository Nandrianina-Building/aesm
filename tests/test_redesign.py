import io
import re

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from PIL import Image

from apps.core.antispam import make_token

from apps.accounts.models import User
from apps.publications.models import Publication

PWD = "Tr3s-Longue-Phrase-2026"


def jpeg(name, color=(120, 90, 200)):
    buf = io.BytesIO()
    Image.new("RGB", (300, 200), color).save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


class RegistrationTests(TestCase):
    def test_registration_makes_member_and_sends_confirmation_email(self):
        r = self.client.post("/compte/inscription/", {
            "last_name": "Rakoto", "first_name": "Naly", "matricule": "tst01", "email": "naly@example.com",
            "phone": "0341234500", "password1": PWD, "password2": PWD, "accept_terms": "on", "accept_privacy": "on",
            "website": "", "form_token": make_token(10)}, follow=True)
        u = User.objects.get(matricule="TST01")
        self.assertTrue(u.is_active_member)                      # membre immédiatement, sans admin
        self.assertEqual(u.memberships.get().status, "accepted")
        self.assertEqual(r.redirect_chain[-1][0], "/espace/")
        self.assertEqual(len(mail.outbox), 1)                    # e-mail de confirmation
        self.assertEqual(mail.outbox[0].to, ["naly@example.com"])
        link = re.search(r"(/compte/verification-email/\S+)", mail.outbox[0].body).group(1)
        self.client.get(link)                                    # le lien reste valable même après connexion
        u.refresh_from_db()
        self.assertTrue(u.email_verified)

    def test_email_is_required(self):
        r = self.client.post("/compte/inscription/", {
            "last_name": "A", "first_name": "B", "matricule": "tst02", "phone": "0341234501",
            "password1": PWD, "password2": PWD, "accept_terms": "on", "accept_privacy": "on", "website": "", "form_token": make_token(10)})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(matricule="TST02").exists())


class UiBehaviourTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("init_aesm", verbosity=0)
        cls.admin = User.objects.create_superuser("ADM01", PWD, first_name="Ad", last_name="Min", phone="0340000001")

    def test_home_cta_changes_when_logged_in(self):
        self.assertContains(self.client.get("/"), "Créer mon compte")
        self.client.login(matricule="ADM01", password=PWD)
        r = self.client.get("/")
        self.assertContains(r, "Accéder à mon espace")
        self.assertNotContains(r, "Créer mon compte")

    def test_demo_banner_only_on_payment_pages(self):
        self.client.login(matricule="ADM01", password=PWD)
        self.assertNotContains(self.client.get("/"), "Mode démonstration")
        self.assertNotContains(self.client.get("/espace/"), "Mode démonstration")

    def test_publication_with_several_images(self):
        self.client.login(matricule="ADM01", password=PWD)
        r = self.client.post("/gestion/publications/nouvelle/", {
            "title": "Galerie", "kind": "actualite", "summary": "s", "body": "b", "visibility": "public",
            "status": "published", "image": jpeg("a.jpg"), "gallery": [jpeg("b.jpg"), jpeg("c.jpg")]})
        self.assertEqual(r.status_code, 302)
        p = Publication.objects.get(title="Galerie")
        self.assertEqual(len(p.all_images), 3)
        self.assertContains(self.client.get(f"/actualites/{p.slug}/"), "ig-car")


class SeoSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("init_aesm", verbosity=0)

    def test_legal_pages_and_footer_links(self):
        for url in ("/confidentialite/", "/conditions-utilisation/"):
            r = self.client.get(url)
            self.assertContains(r, "<title>")
            self.assertContains(r, 'name="description"')
        self.assertContains(self.client.get("/"), "/confidentialite/")

    def test_robots_and_sitemap(self):
        r = self.client.get("/robots.txt")
        self.assertContains(r, "Sitemap:")
        self.assertContains(r, "Disallow: /gestion/")
        s = self.client.get("/sitemap.xml")
        self.assertEqual(s.status_code, 200)
        self.assertContains(s, "/actualites/")

    def test_private_areas_are_noindex(self):
        self.assertEqual(self.client.get("/compte/connexion/")["X-Robots-Tag"], "noindex, nofollow")

    def test_custom_404(self):
        from django.test import override_settings
        with override_settings(DEBUG=False):
            r = self.client.get("/page-qui-n-existe-pas/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "Page introuvable", status_code=404)
        self.assertContains(r, "Retour à l'accueil", status_code=404)

    def test_antispam_honeypot_and_speed(self):
        data = {"name": "Bot", "email": "b@example.com", "subject": "Hello", "message": "Un message assez long pour passer."}
        r = self.client.post("/contact/", {**data, "website": "http://spam", "form_token": make_token(10)})
        self.assertEqual(r.status_code, 200)                       # honeypot rempli : refusé
        r = self.client.post("/contact/", {**data, "website": "", "form_token": make_token(0)})
        self.assertEqual(r.status_code, 200)                       # trop rapide : refusé
        r = self.client.post("/contact/", {**data, "website": "", "form_token": make_token(10)})
        self.assertEqual(r.status_code, 302)                       # humain : accepté

    def test_terms_checkbox_required(self):
        r = self.client.post("/compte/inscription/", {
            "last_name": "A", "first_name": "B", "matricule": "tst03", "email": "c@example.com", "phone": "0341234502",
            "password1": PWD, "password2": PWD, "website": "", "form_token": make_token(10)})
        self.assertFalse(User.objects.filter(matricule="TST03").exists())

    def test_image_is_compressed(self):
        from apps.core.images import optimize_image
        buf = io.BytesIO()
        Image.new("RGB", (4000, 3000), (10, 120, 200)).save(buf, "PNG")
        out = optimize_image(SimpleUploadedFile("big.png", buf.getvalue()), 1600)
        self.assertLess(len(out.read()), 200_000)
        out.seek(0)
        self.assertEqual(max(Image.open(out).size), 1600)

    def test_single_cta_on_home(self):
        html = self.client.get("/").content.decode()
        self.assertEqual(html.count("btn-lg"), 1)
        self.assertNotIn('class="pill-btn" href="/compte/inscription/"', html)


class V4UiTests(TestCase):
    """Toasts d'erreur de connexion, avatars, galerie d'événement, menu d'espace."""

    def test_login_error_is_a_toast(self):
        User.objects.create_user("LOG01", PWD, first_name="A", last_name="B", phone="0341111111", account_status="active")
        r = self.client.post("/compte/connexion/", {"username": "log01", "password": "faux"})
        self.assertContains(r, 'data-toast="error"')
        self.assertContains(r, "Matricule ou mot de passe incorrect.")

    def test_login_success_toast(self):
        User.objects.create_user("LOG02", PWD, first_name="A", last_name="B", phone="0341111112", account_status="active")
        r = self.client.post("/compte/connexion/", {"username": "log02", "password": PWD}, follow=True)
        self.assertContains(r, "Connexion réussie")

    def test_avatar_shows_own_photo_and_hides_others(self):
        a = User.objects.create_user("AV01", PWD, first_name="Al", last_name="Ba", phone="0341111113", account_status="active",
                                     photo=jpeg("p.jpg"))
        b = User.objects.create_user("AV02", PWD, first_name="Cy", last_name="Di", phone="0341111114", account_status="active")
        self.client.force_login(a)
        self.assertContains(self.client.get("/espace/"), f"/compte/photo/{a.public_id}/")
        photo_response = self.client.get(f"/compte/photo/{a.public_id}/")
        self.assertEqual(photo_response.status_code, 200)
        photo_response.close()
        a.photo.delete(save=False)
        self.client.force_login(b)
        self.assertEqual(self.client.get(f"/compte/photo/{a.public_id}/").status_code, 404)

    def test_event_gallery_and_menu(self):
        from datetime import timedelta
        from django.utils import timezone
        from apps.events.models import Event, EventImage
        now = timezone.now()
        e = Event.objects.create(title="Expo", description="d", starts_at=now + timedelta(days=5), location="Salle", capacity=10,
                                 registration_deadline=now + timedelta(days=3), status="open", visibility="public")
        EventImage.objects.create(event=e, image=jpeg("1.jpg"))
        EventImage.objects.create(event=e, image=jpeg("2.jpg"))
        r = self.client.get(f"/evenements/{e.pk}/")
        self.assertContains(r, "ig-car")
        self.assertEqual(len(e.all_images), 2)
        self.assertContains(self.client.get("/evenements/"), "date-chip")
        u = User.objects.create_user("MN01", PWD, first_name="A", last_name="B", phone="0341111115", account_status="active")
        self.client.force_login(u)
        self.assertContains(self.client.get("/espace/paiements/cotisations/"), "sm-ico")


class ConsentAndErrorPagesTests(TestCase):
    """Cases RGPD à l'inscription, pages d'erreur et boutons épingle/cadenas."""

    def test_register_requires_both_consents(self):
        from apps.core.antispam import make_token
        base = {"last_name": "Rakoto", "first_name": "Jean", "matricule": "ZZ900", "email": "zz900@example.com",
                "phone": "0341234599", "password1": "Tr0ub4dor&3-long", "password2": "Tr0ub4dor&3-long",
                "website": "", "form_token": make_token(10)}
        for missing in ("accept_terms", "accept_privacy"):
            data = dict(base, accept_terms="on", accept_privacy="on")
            del data[missing]
            r = self.client.post("/compte/inscription/", data)
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, "Vous devez accepter")

    def test_pin_and_lock_require_manager(self):
        from apps.publications.models import Publication
        p = Publication.objects.create(title="Test pin", summary="s", body="b", status="published")
        r = self.client.post(f"/actualites/{p.slug}/epingler/")
        self.assertNotEqual(r.status_code, 200)  # anonyme : redirigé vers la connexion
        p.refresh_from_db()
        self.assertFalse(p.pinned)
