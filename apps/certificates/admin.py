from django.contrib import admin
from .models import MemberCard, Quitus, Receipt

for m in (MemberCard, Quitus, Receipt):
    admin.site.register(m)
