from django.contrib import admin
from .models import BudgetEntry, FinancialReport


@admin.register(BudgetEntry)
class BudgetEntryAdmin(admin.ModelAdmin):
    list_display = ("reference", "kind", "category", "amount", "date", "status")
    list_filter = ("kind", "status")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(FinancialReport)
