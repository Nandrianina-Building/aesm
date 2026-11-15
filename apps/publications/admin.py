from django.contrib import admin
from .models import Comment, Publication, PublicationCategory, PublicationImage


class PublicationImageInline(admin.TabularInline):
    model = PublicationImage
    extra = 1


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    inlines = [PublicationImageInline]


admin.site.register(PublicationCategory)
admin.site.register(Comment)
