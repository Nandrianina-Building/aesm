#!/usr/bin/env bash
# Installation / mise à jour de AESM sur PythonAnywhere. À lancer dans une console Bash, virtualenv activé :
#     cd ~/aesm && bash deploy/pythonanywhere/setup.sh
# Peut être relancé sans danger (ne recrée pas les données déjà présentes).
set -euo pipefail
cd "$(dirname "$0")/../.."
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"
PY="${PYTHON:-python}"

if [ ! -f .env ]; then
  USERNAME_PA="${USER:-VOTRE_NOM}"
  SECRET="$($PY -c 'import secrets; print(secrets.token_urlsafe(64))')"
  DEMOPWD="$($PY -c 'import secrets; print("Aesm-" + secrets.token_urlsafe(9))')"
  sed -e "s|__SECRET__|$SECRET|" -e "s|__USER__|$USERNAME_PA|g" -e "s|__DEMOPWD__|$DEMOPWD|" .env.pythonanywhere.example > .env
  chmod 600 .env
  echo
  echo "==> Le fichier .env vient d'être créé (clé secrète et mot de passe de démo générés automatiquement)."
  echo "==> ÉTAPE SUIVANTE : ouvrez .env et remplacez les 3 valeurs A_REMPLIR (votre Gmail et son mot de passe d'application),"
  echo "    puis relancez :  bash deploy/pythonanywhere/setup.sh"
  exit 0
fi

if grep -q "A_REMPLIR" .env; then
  echo "ERREUR : .env contient encore « A_REMPLIR ». Renseignez EMAIL_HOST_USER, EMAIL_HOST_PASSWORD et DEFAULT_FROM_EMAIL, puis relancez." >&2
  exit 1
fi

echo "==> 1/6 Dossiers et images de démonstration"
mkdir -p media private
cp -rn demo_media/. media/
echo "==> 2/6 Base de données (migrations)"
$PY manage.py migrate --noinput
echo "==> 3/6 Cache (table)"
$PY manage.py createcachetable
echo "==> 4/6 Fichiers statiques"
$PY manage.py collectstatic --noinput | tail -1
echo "==> 5/6 Rôles et paramètres de base"
$PY manage.py init_aesm
echo "==> 6/6 Données de démonstration + mot de passe privé"
MEMBERS="$(grep -E '^DEMO_MEMBERS=' .env | cut -d= -f2- || true)"
$PY manage.py seed_demo --members "${MEMBERS:-30}" > /tmp/aesm_seed.log 2>&1 || { cat /tmp/aesm_seed.log; exit 1; }
echo "    données de démonstration prêtes"
$PY manage.py set_demo_password
echo "==> Contrôle de configuration"
$PY manage.py check --deploy || true
echo
echo "TERMINÉ. Mot de passe des comptes de démo (ADMIN01, PRES01, TRES01, SECR01, EVEN01, SOC26-0001 ...) :"
grep -E '^DEMO_PASSWORD=' .env | cut -d= -f2-
echo "Prochaine étape : onglet Web de PythonAnywhere (guide, partie C)."
