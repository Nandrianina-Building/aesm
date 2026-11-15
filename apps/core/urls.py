from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("a-propos/", views.about, name="about"),
    path("bureau/", views.bureau, name="bureau"),
    path("bureau/photo/<uuid:public_id>/", views.bureau_photo, name="bureau_photo"),
    path("contact/", views.contact, name="contact"),
    path("conditions-utilisation/", views.terms, name="terms"),
    path("confidentialite/", views.privacy, name="privacy"),
    path("robots.txt", views.robots_txt, name="robots"),
]
