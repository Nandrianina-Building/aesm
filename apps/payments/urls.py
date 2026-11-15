from django.urls import path

from . import views

app_name = "payments"
urlpatterns = [
    path("cotisations/", views.dues, name="dues"),
    path("cotisations/<int:pk>/payer/", views.pay_due, name="pay_due"),
    path("reservation/<int:pk>/payer/", views.pay_reservation, name="pay_reservation"),
    path("", views.payment_list, name="list"),
    path("<str:reference>/simulation/", views.simulate, name="simulate"),
    path("<str:reference>/", views.payment_detail, name="detail"),
    path("<str:reference>/preuve/", views.proof_download, name="proof"),
    path("webhook/<str:provider>/", views.webhook, name="webhook"),
]
