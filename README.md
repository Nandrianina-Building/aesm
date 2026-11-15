> **Mise en ligne de test (V1) sur PythonAnywhere : voir `docs/DEPLOIEMENT_PYTHONANYWHERE.md`.**

# Plateforme AESM

Plateforme web de l'**Association des Étudiants en Sociologie de Madagascar** : adhésion, cotisations (paiements **simulés** pour l'instant, prêts pour **Tokipay**),
reçus / quitus / carte de membre avec QR code, documents pédagogiques, actualités, événements avec billets QR,
suivi financier transparent, notifications, réclamations et journal d'audit.

**Pile technique** : Python 3.11+ · Django 5 · **MySQL 8 (ou MariaDB 10.6+)** · Bootstrap 5 · ReportLab · qrcode · openpyxl.

## Démo immédiate (données déjà chargées)
Le zip contient une base SQLite remplie (126 comptes, 357 cotisations, 387 paiements, 340 réservations, 418 opérations financières…) :
```bash
pip install -r requirements.txt
./run_demo.sh          # Windows : run_demo.bat   → http://127.0.0.1:8000
```
Connexion : `ADMIN01` (super admin), `PRES01`, `TRES01`, `SECR01`, `SECR02`, `EVEN01`, ou un membre `SOC26-0001`… ; mot de passe commun **DemoAESM-2026!x**.
Détails et volumes : `docs/DONNEES_DEMO.md`. Pour charger les mêmes données dans MySQL : `python manage.py seed_demo`.

## Démarrage rapide (développement)

```bash
python -m venv .venv && source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # puis renseigner les accès MySQL
# MySQL : voir docs/INSTALLATION.md pour créer la base et l'utilisateur
python manage.py migrate
python manage.py init_aesm            # rôles, paramètres, catégories (ajouter --demo pour des comptes d'essai)
python manage.py createsuperuser      # matricule + mot de passe (reçoit le rôle super_admin)
python manage.py runserver
```

Test sans MySQL : `DB_ENGINE=sqlite` dans `.env` (jamais en production).
Tests : `DB_ENGINE=sqlite python manage.py test tests` (53 tests : paiements, droits, IDOR, billets, finances…).

## Structure

| Dossier | Contenu |
|---|---|
| `apps/accounts` | utilisateur (matricule), rôles, inscription, connexion protégée, profil |
| `apps/memberships` | demandes d'adhésion et machine d'états |
| `apps/payments` | cotisations, paiements, prestataires (simulation / Tokipay), webhook signé |
| `apps/certificates` | reçus, quitus, cartes, billets PDF, vérification publique QR |
| `apps/events` | événements, réservations atomiques, billets, présence |
| `apps/finance` | opérations immuables, rapports versionnés, exports PDF/Excel |
| `apps/publications`, `apps/documents` | actualités (commentaires, likes) et bibliothèque PDF privée |
| `apps/notifications`, `apps/support`, `apps/audit` | notifications, réclamations, journal d'audit |
| `apps/core` | RBAC (`permissions.py`), paramètres, bureau, espace de gestion (`/gestion/`) |
| `docs/` | architecture, sécurité, installation, sauvegarde, guides, plan de tests, points ouverts |
| `deploy/` | gunicorn, nginx, cron, script de sauvegarde |

## Adresses utiles
`/` public · `/espace/` espace membre · `/gestion/` espace des responsables · `/admin-aesm/` admin Django (super admin) ·
`/verification/<code>/` vérification QR publique.

**Lire d'abord `docs/POINTS_OUVERTS.md`** : décisions prises sur les questions ouvertes du cahier des charges et limites connues
(notamment : paiements simulés, branchement Tokipay à finaliser : voir `docs/PAIEMENTS_TOKIPAY.md`).
