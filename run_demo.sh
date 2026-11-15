#!/usr/bin/env bash
# Lance la démonstration avec la base SQLite fournie (données déjà chargées). Pas de MySQL requis.
cd "$(dirname "$0")"
export DB_ENGINE=sqlite DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py runserver
