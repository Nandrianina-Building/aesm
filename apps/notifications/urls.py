from django.urls import path

from . import views

app_name = "notifications"
urlpatterns = [
    path("", views.notification_list, name="list"),
    path("tout-lire/", views.mark_all_read, name="mark_all"),
    path("<int:pk>/basculer/", views.toggle_read, name="toggle"),
    path("<int:pk>/supprimer/", views.delete, name="delete"),
    path("<int:pk>/ouvrir/", views.open_notification, name="open"),
]
