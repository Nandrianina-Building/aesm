from django.urls import path

from . import views

app_name = "events_member"
urlpatterns = [
    path("", views.my_reservations, name="list"),
    path("<int:pk>/annuler/", views.cancel, name="cancel"),
    path("<int:pk>/billet/", views.ticket_pdf, name="ticket"),
]
