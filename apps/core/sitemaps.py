from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Event
from apps.publications.models import Publication


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    protocol = None

    def items(self):
        return ["core:home", "core:about", "core:bureau", "core:contact", "publications:list", "events:list",
                "documents:list", "core:terms", "core:privacy"]

    def location(self, name):
        return reverse(name)

    def priority(self, name):
        return 1.0 if name == "core:home" else 0.6


class PublicationSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        now = timezone.now()
        return [p for p in Publication.objects.filter(visibility="public", status__in=["published", "scheduled"])
                if p.is_live and (p.publish_at is None or p.publish_at <= now)]

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("publications:detail", args=[obj.slug])


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Event.objects.filter(visibility="public").exclude(status="draft")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("events:detail", args=[obj.pk])


SITEMAPS = {"pages": StaticSitemap, "actualites": PublicationSitemap, "evenements": EventSitemap}
