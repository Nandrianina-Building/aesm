from django.contrib import admin

from .models import Attendance, Event, EventImage, Reservation, Ticket


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [EventImageInline]


for m in (Reservation, Ticket, Attendance):
    admin.site.register(m)
