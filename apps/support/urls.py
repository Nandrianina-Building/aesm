from django.urls import path

from . import views

app_name = "support"
urlpatterns = [
    path("", views.ticket_list, name="list"),
    path("nouvelle/", views.ticket_create, name="create"),
    path("<int:pk>/", views.ticket_detail, name="detail"),
    path("<int:pk>/piece/", views.attachment, name="attachment"),
]
