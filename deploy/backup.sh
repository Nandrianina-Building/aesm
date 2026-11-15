#!/usr/bin/env bash
# Sauvegarde quotidienne : base MySQL + fichiers privés + médias. À lancer par cron (voir docs/SAUVEGARDE.md).
set -euo pipefail
cd "$(dirname "$0")/.."
# On NE « source » PAS le .env (une valeur avec espaces ou < > le fait échouer) : lecture ciblée des seules clés utiles.
umask 077   # sauvegardes lisibles uniquement par l'utilisateur de l'application
env_get() { { grep -E "^$1=" .env || true; } | tail -n1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"; }
DB_HOST="$(env_get DB_HOST)"; DB_PORT="$(env_get DB_PORT)"; DB_USER="$(env_get DB_USER)"
DB_PASSWORD="$(env_get DB_PASSWORD)"; DB_NAME="$(env_get DB_NAME)"; BACKUP_DIR="${BACKUP_DIR:-$(env_get BACKUP_DIR)}"
DEST="${BACKUP_DIR:-./backups}/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DEST"
# MYSQL_PWD évite d'exposer le mot de passe dans la liste des processus (ps)
MYSQL_PWD="$DB_PASSWORD" mysqldump --single-transaction --routines --default-character-set=utf8mb4 \
  -h "$DB_HOST" -P "${DB_PORT:-3306}" -u "$DB_USER" "$DB_NAME" | gzip > "$DEST/db.sql.gz"
tar czf "$DEST/files.tar.gz" private media
# Conserver 30 jours
find "${BACKUP_DIR:-./backups}" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +
echo "Sauvegarde terminée : $DEST"
