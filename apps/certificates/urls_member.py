from django.urls import path

from . import views

app_name = "certificates"
urlpatterns = [
    path("recus/", views.receipt_list, name="receipt_list"),
    path("recus/<str:number>/pdf/", views.receipt_pdf, name="receipt_pdf"),
    path("quitus/", views.quitus_list, name="quitus_list"),
    path("quitus/<str:number>/pdf/", views.quitus_pdf, name="quitus_pdf"),
    path("carte/", views.card_view, name="card"),
    path("carte/pdf/", views.card_pdf, name="card_pdf"),
]
