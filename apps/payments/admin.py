from django.contrib import admin
from .models import ContributionDue, ContributionType, Payment, PaymentAttempt, PaymentProviderEvent

admin.site.register(ContributionType)
admin.site.register(ContributionDue)
admin.site.register(PaymentAttempt)
admin.site.register(PaymentProviderEvent)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "amount", "method", "status", "created_at")
    list_filter = ("status", "method")
    search_fields = ("reference", "external_reference", "user__matricule")
    readonly_fields = [f.name for f in Payment._meta.fields]  # un paiement ne se modifie pas à la main (RG-04)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
