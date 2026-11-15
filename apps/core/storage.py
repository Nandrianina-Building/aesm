from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateStorage(FileSystemStorage):
    """Stockage hors du répertoire public : aucun accès direct par URL."""

    def __init__(self):
        super().__init__(location=str(settings.PRIVATE_ROOT), base_url=None)

    def url(self, name):
        raise ValueError("Les fichiers privés ne sont accessibles que via une vue contrôlée.")


private_storage = PrivateStorage()


def internal_name(prefix, filename):
    """Nom de fichier interne aléatoire (le nom fourni n'est jamais utilisé comme chemin)."""
    import os
    import uuid
    ext = os.path.splitext(filename)[1].lower()
    return f"{prefix}/{uuid.uuid4().hex}{ext}"
