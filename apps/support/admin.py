from django.contrib import admin
from .models import SupportMessage, SupportTicket

admin.site.register(SupportTicket)
admin.site.register(SupportMessage)
