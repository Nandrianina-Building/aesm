from django.urls import path

from . import views

app_name = "verify"
urlpatterns = [path("<str:token>/", views.verify, name="check")]
