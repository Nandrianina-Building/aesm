"""Composants d'interface : avatar (photo ou initiales), emplacement photo des publications."""
from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


def _initials(person):
    first = (getattr(person, "first_name", "") or "")[:1]
    last = (getattr(person, "last_name", "") or "")[:1]
    return (first + last).upper() or "?"


def _photo_url(context, person):
    """URL de la photo si elle existe et si le visiteur a le droit de la voir, sinon chaîne vide."""
    photo = getattr(person, "photo", None)
    if not photo:
        return ""
    if hasattr(person, "public_id"):  # compte utilisateur : photo privée (propriétaire ou responsable)
        viewer = context.get("user") or getattr(context.get("request"), "user", None)
        if viewer is None or not viewer.is_authenticated:
            return ""
        perms = context.get("perm") or {}
        if viewer.pk != person.pk and not perms.get("members.view"):
            return ""
        from zlib import crc32
        return reverse("accounts:photo", args=[person.public_id]) + f"?v={crc32(photo.name.encode()):x}"  # change si la photo change
    try:
        return photo.url  # responsable du bureau : photo publique
    except ValueError:
        return ""


@register.simple_tag(takes_context=True)
def avatar(context, person, size="md", extra=""):
    """Affiche la photo d'une personne (comme dans le bureau) ou, à défaut, ses initiales.

    size : xs (28) · sm (40) · md (56) · lg (96) · xl (128)
    """
    if person is None:
        return ""
    url = _photo_url(context, person)
    name = f"{getattr(person, 'first_name', '')} {getattr(person, 'last_name', '')}".strip()
    cls = f"avatar av-{size} {extra}".strip()
    if url:
        return format_html('<span class="{}"><img src="{}" alt="Photo de {}" loading="lazy" decoding="async"></span>', cls, url, name)
    return format_html('<span class="{}" aria-hidden="true"><span>{}</span></span>', cls, _initials(person))


@register.filter
def has_photo(person, context=None):
    return bool(getattr(person, "photo", None))
