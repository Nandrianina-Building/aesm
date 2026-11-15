from django.contrib import admin
from .models import ContactMessage, Officer, SiteSetting

admin.site.register(SiteSetting)
admin.site.register(Officer)
admin.site.register(ContactMessage)
