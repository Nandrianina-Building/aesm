# Installation (MySQL)

## 1. Base MySQL
```sql
CREATE DATABASE aesm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aesm_user'@'localhost' IDENTIFIED BY 'mot-de-passe-long-et-unique';
GRANT ALL PRIVILEGES ON aesm.* TO 'aesm_user'@'localhost';
FLUSH PRIVILEGES;
```
Les tests Django créent une base `test_aesm` : donner aussi `GRANT ALL ON test_aesm.*` si vous testez sur MySQL.
Moteur InnoDB requis (transactions, verrous `SELECT ... FOR UPDATE`).

## 2. Pilote Python
`mysqlclient` nécessite les bibliothèques de développement MySQL :
- Debian/Ubuntu : `sudo apt install default-libmysqlclient-dev build-essential pkg-config`
- Windows : `pip install mysqlclient` fournit normalement une roue précompilée.
Alternative sans compilation : `pip install pymysql` puis ajouter en tête de `config/__init__.py` :
`import pymysql; pymysql.install_as_MySQLdb()`.

## 3. Application
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # renseigner DJANGO_SECRET_KEY, DB_*, SITE_URL
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py createcachetable      # cache partagé (limitation de débit, verrouillage de connexion)
python manage.py init_aesm
python manage.py createsuperuser
python manage.py collectstatic --noinput
```
Générer une clé : `python -c "import secrets; print(secrets.token_urlsafe(60))"`.

## 4. Production
- Gunicorn : `gunicorn config.wsgi -c deploy/gunicorn.conf.py` (service systemd conseillé).
- Nginx + HTTPS : `deploy/nginx.conf` (Certbot). **Ne jamais exposer le dossier `private/`.**
- Cron : `deploy/crontab.example` (expiration des réservations, des adhésions, sauvegardes).
- Vérifier : `python manage.py check --deploy`.
- Paiements : `PAYMENT_PROVIDER=simulation` par défaut (voir `docs/PAIEMENTS_TOKIPAY.md`).
- Premier paramétrage dans `/gestion/parametres/` : solde initial, durée d'adhésion, coordonnées.
- Attribuer les rôles dans `/gestion/utilisateurs/`.
