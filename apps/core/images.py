"""Compression automatique des images envoyées (pages plus rapides, stockage réduit)."""
import io
import os

from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from PIL import Image, ImageOps


def optimize_image(file, max_side=1600, quality=82):
    """Retourne un ContentFile compressé (redimensionné, EXIF retiré, JPEG progressif)."""
    file.seek(0)
    img = Image.open(file)
    img = ImageOps.exif_transpose(img)  # respecte l'orientation, puis les métadonnées (GPS...) sont supprimées
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    buf = io.BytesIO()
    base = os.path.splitext(os.path.basename(file.name))[0]
    if has_alpha:  # PNG transparent : on garde le PNG, optimisé
        img.save(buf, "PNG", optimize=True)
        name = base + ".png"
    else:
        img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        name = base + ".jpg"
    return ContentFile(buf.getvalue(), name=name)


def connect_optimizer(model, fields):
    """fields = {"nom_du_champ": taille_max_en_px}. Ne traite que les fichiers nouvellement envoyés."""
    def handler(sender, instance, **kwargs):
        for name, max_side in fields.items():
            f = getattr(instance, name, None)
            if f and not getattr(f, "_committed", True):
                try:
                    small = optimize_image(f.file, max_side)
                except Exception:  # image illisible : la validation du formulaire s'en charge
                    continue
                f.save(small.name, small, save=False)
    pre_save.connect(handler, sender=model, weak=False, dispatch_uid=f"optimize-{model.__name__}")
