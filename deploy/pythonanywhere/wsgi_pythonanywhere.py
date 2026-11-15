# À COLLER dans le fichier WSGI de l'onglet Web de PythonAnywhere (remplace tout son contenu).
# Remplacez VOTRE_NOM par votre nom d'utilisateur PythonAnywhere (2 endroits sont signalés par VOTRE_NOM).
import os
import sys

path = "/home/VOTRE_NOM/aesm"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.prod"

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
