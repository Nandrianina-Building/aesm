from django.urls import path

from . import views

app_name = "finance_member"
urlpatterns = [
    path("", views.report_list, name="list"),
    path("<int:pk>/", views.report_detail, name="detail"),
    path("<int:pk>/excel/", views.report_xlsx, name="report_xlsx"),
    path("<int:pk>/pdf/", views.report_pdf, name="report_pdf"),
]
