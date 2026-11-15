@echo off
set DB_ENGINE=sqlite
set DJANGO_SETTINGS_MODULE=config.settings.dev
python manage.py runserver
