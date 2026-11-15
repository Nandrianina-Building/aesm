from django.urls import path

from . import views_dashboard

app_name = "dashboard"
urlpatterns = [path("", views_dashboard.member_dashboard, name="home")]
