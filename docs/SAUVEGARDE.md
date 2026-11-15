# Sauvegarde et restauration

**Quoi sauvegarder** : base MySQL, dossier `private/` (documents, preuves, photos, justificatifs), dossier `media/`, fichier `.env` (à part, chiffré).

**Sauvegarde** : `deploy/backup.sh` (mysqldump transactionnel + archive des fichiers, rétention 30 jours), planifiée à 2 h 30 par cron.
Copier régulièrement les sauvegardes **hors du serveur** (autre machine, stockage distant chiffré).

**Restauration**
```bash
gunzip < db.sql.gz | mysql -u aesm_user -p aesm
tar xzf files.tar.gz -C /srv/aesm
python manage.py migrate && python manage.py check
```
**Test de restauration** : à effectuer au moins une fois par trimestre sur une machine de test, puis noter la date.
Le journal d'audit étant dans la base, il est restauré avec elle.
