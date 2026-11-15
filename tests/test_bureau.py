import io
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User
from apps.core.forms import OfficerForm
from apps.core.models import Officer
from apps.core.views import about, bureau, bureau_photo


class PublicOfficerPhotoTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            "OFFICER1", "secure-password-123", first_name="Faly", last_name="Andriamanana", phone="0341234567",
        )
        image_buffer = io.BytesIO()
        Image.new("RGB", (20, 20), (120, 90, 200)).save(image_buffer, "JPEG")
        self.image_data = image_buffer.getvalue()
        self.member.photo.save(
            "portrait.jpg", SimpleUploadedFile("portrait.jpg", self.image_data, content_type="image/jpeg"),
        )
        self.addCleanup(self.member.photo.delete, save=False)

    def test_profile_photo_is_public_only_for_an_active_linked_officer(self):
        photo_url = reverse("core:bureau_photo", args=[self.member.public_id])
        with self.assertRaises(Http404):
            bureau_photo(None, self.member.public_id)

        officer = Officer.objects.create(
            user=self.member, first_name=self.member.first_name, last_name=self.member.last_name,
            function="Responsable événementiel", mandate_start=date.today(), is_archived=True,
        )
        with self.assertRaises(Http404):
            bureau_photo(None, self.member.public_id)

        officer.is_archived = False
        officer.save(update_fields=["is_archived"])
        bureau_response = bureau(RequestFactory().get(reverse("core:bureau")))
        self.assertIn(self.member.first_name.encode(), bureau_response.content)
        self.assertNotIn(photo_url.encode(), bureau_response.content)
        about_response = about(RequestFactory().get(reverse("core:about")))
        self.assertIn(photo_url.encode(), about_response.content)

        photo = self.client.get(photo_url)
        self.assertEqual(photo.status_code, 200)
        self.assertEqual(photo["Content-Type"], "image/jpeg")
        self.assertEqual(b"".join(photo.streaming_content), self.image_data)

    def test_associated_profile_photo_satisfies_officer_photo_requirement(self):
        form = OfficerForm(data={
            "last_name": self.member.last_name,
            "first_name": self.member.first_name,
            "user": self.member.pk,
            "function": "Responsable événementiel",
            "mandate_start": date.today().isoformat(),
            "mandate_end": "",
            "photo": "",
            "description": "",
            "is_archived": "",
        })

        self.assertTrue(form.is_valid(), form.errors)
        officer = form.save()
        self.assertEqual(officer.user, self.member)
        self.assertFalse(officer.photo)
