import os

from django.core.exceptions import ValidationError

from .utils import get_int_setting

FORBIDDEN_EXT = {".exe", ".bat", ".cmd", ".sh", ".js", ".php", ".py", ".dll", ".msi", ".com", ".scr", ".html", ".htm", ".svg"}
SIGNATURES = {
    "pdf": (b"%PDF-",),
    "jpg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}


def _head(file, n=16):
    pos = file.tell() if hasattr(file, "tell") else 0
    file.seek(0)
    data = file.read(n)
    file.seek(pos if pos else 0)
    return data


def _check(file, allowed, max_mb):
    ext = os.path.splitext(file.name)[1].lower()
    if ext in FORBIDDEN_EXT:
        raise ValidationError("Type de fichier interdit.")
    ext_key = {".jpeg": "jpg", ".jpg": "jpg", ".png": "png", ".pdf": "pdf"}.get(ext)
    if ext_key not in allowed:
        raise ValidationError("Format non autorisé. Formats acceptés : " + ", ".join(a.upper() for a in allowed) + ".")
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Fichier trop volumineux (maximum {max_mb} Mo).")
    head = _head(file)
    if not any(head.startswith(sig) for sig in SIGNATURES[ext_key]):
        raise ValidationError("Le contenu du fichier ne correspond pas à son extension.")


def validate_pdf(file):
    _check(file, ["pdf"], get_int_setting("max_document_mb", 10))


def validate_image(file):
    _check(file, ["jpg", "png"], 3)


def validate_attachment(file):
    _check(file, ["pdf", "jpg", "png"], 5)
