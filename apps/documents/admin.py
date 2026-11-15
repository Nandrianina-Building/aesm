from django.contrib import admin
from .models import Document, DocumentCategory

admin.site.register(DocumentCategory)
admin.site.register(Document)
