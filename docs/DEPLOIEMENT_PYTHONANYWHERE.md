# Guide : mettre AESM en ligne sur PythonAnywhere (V1 de TEST, paiement SIMULÉ)

Pour qui : quelqu'un qui n'a jamais déployé de site. Durée : environ 1 h 30. Coût : 0 (compte gratuit).
Résultat : un site `https://VOTRE_NOM.pythonanywhere.com` avec vrais e-mails (confirmation d'adresse, mot de passe oublié) et paiement **simulé**.

**Règle d'or : ne mettez JAMAIS un mot de passe, une clé ou le fichier `.env` dans GitHub.** Ce projet est prévu pour ça (`.gitignore`).

Mots à connaître : **GitHub** = un coffre-fort en ligne pour votre code. **Dépôt (repo)** = un dossier dans ce coffre. **Console Bash** = une fenêtre où on tape des commandes. **Virtualenv** = une boîte qui contient les outils Python du projet. **Reload** = le bouton qui redémarre le site.

À remplacer partout dans ce guide (écrivez-les sur un papier) :
- `GH` = votre nom d'utilisateur GitHub
- `PA` = votre nom d'utilisateur PythonAnywhere
- `TOKEN` = le jeton GitHub de l'étape A6

---
## PARTIE A : mettre le code sur GitHub (sur votre PC)

**A1. Décompresser.** Faites un clic droit sur `AESM_V1_PythonAnywhere.zip` > « Extraire tout ». Vous obtenez un dossier `aesm`. Ouvrez-le : vous devez voir `manage.py`, `apps`, `config`, `templates`... Si vous voyez seulement un autre dossier `aesm` à l'intérieur, entrez dedans.

**A2. Compte GitHub.** Allez sur https://github.com > « Sign up ». Choisissez un nom d'utilisateur simple (c'est `GH`). Confirmez votre e-mail.

**A3. Installer Git.** Allez sur https://git-scm.com/download/win, téléchargez, lancez l'installateur et cliquez « Next » jusqu'à la fin (réglages par défaut).

**A4. Créer le dépôt.** Sur GitHub, cliquez le « + » en haut à droite > « New repository ».
- Repository name : `aesm`
- Choisissez **Private**
- **Ne cochez rien d'autre** (pas de README)
- « Create repository ». Laissez la page ouverte.

**A5. Envoyer le code.** Dans le dossier `aesm` (celui qui contient `manage.py`), clic droit sur une zone vide > « Open Git Bash here » (sous Windows 11 : « Afficher plus d'options » d'abord). Tapez ces commandes **une par une** (Entrée après chaque) :

```
git init
git add .
git status
```
Lisez la liste : vous ne devez PAS voir `.env` ni `db.sqlite3`. Puis :
```
git config user.name "Votre Nom"
git config user.email "votre.email@exemple.com"
git commit -m "AESM V1 test"
git branch -M main
git remote add origin https://github.com/GH/aesm.git
git push -u origin main
```
Une fenêtre du navigateur s'ouvre pour vous connecter à GitHub : acceptez. Rechargez la page GitHub : vos fichiers apparaissent. Vérifiez qu'il n'y a **pas** de fichier `.env`.

**A6. Créer le jeton (TOKEN) pour que PythonAnywhere puisse lire votre dépôt privé.**
GitHub > votre photo (en haut à droite) > Settings > tout en bas « Developer settings » > Personal access tokens > **Fine-grained tokens** > « Generate new token ».
- Token name : `pythonanywhere`
- Expiration : 90 days
- Repository access : « Only select repositories » > choisissez `aesm`
- Permissions > Repository permissions > **Contents : Read-only**
- « Generate token ». **Copiez le texte** qui commence par `github_pat_` dans le Bloc-notes. Il ne sera plus jamais affiché. C'est votre `TOKEN`. Ne le partagez avec personne.

---
## PARTIE B : préparer l'envoi d'e-mails avec Gmail

Les e-mails du site (confirmation d'adresse, mot de passe oublié) partent depuis un compte Gmail.

**B1.** Créez un compte Gmail **dédié** (ex. `aesm.test@gmail.com`), pas votre adresse personnelle.
**B2.** Connectez-vous > https://myaccount.google.com > « Sécurité » > activez la « Validation en deux étapes » (téléphone requis).
**B3.** Allez sur https://myaccount.google.com/apppasswords > nom de l'application : `aesm` > « Créer ». Google affiche **16 lettres** : copiez-les **sans espaces** dans le Bloc-notes. C'est le « mot de passe d'application » (différent de votre vrai mot de passe Gmail).

---
## PARTIE C : installer sur PythonAnywhere

**C1. Compte.** https://www.pythonanywhere.com > « Pricing & signup » > « Create a Beginner account ». Votre nom d'utilisateur (`PA`) devient l'adresse du site : `https://PA.pythonanywhere.com`. Choisissez-le avec soin (il ne se change pas). Confirmez votre e-mail.

**C2. Ouvrir une console.** Onglet **Consoles** > sous « Start a new console », cliquez **Bash**. Une fenêtre noire s'ouvre.

**C3. Télécharger le code depuis GitHub.** Tapez (en remplaçant GH et TOKEN ; tout sur une ligne) :
```
git clone https://GH:TOKEN@github.com/GH/aesm.git
cd aesm
```

**C4. Créer la boîte à outils Python et l'installer.**
```
mkvirtualenv aesm-venv --python=python3.12
pip install -r requirements-pythonanywhere.txt
```
Le début de la ligne doit afficher `(aesm-venv)`. L'installation dure 2 à 4 minutes. Si « python3.12 » est refusé, essayez `python3.11` ou `python3.13` (retenez la version choisie : il faudra la même à l'étape C10).

**C5. Dire à toutes vos consoles d'utiliser la configuration « production ».**
```
echo 'export DJANGO_SETTINGS_MODULE=config.settings.prod' >> ~/.bashrc
export DJANGO_SETTINGS_MODULE=config.settings.prod
```

**C6. Premier lancement de l'installateur** (il crée le fichier de réglages `.env` avec une clé secrète et un mot de passe de démo aléatoires) :
```
bash deploy/pythonanywhere/setup.sh
```
Il affiche « Le fichier .env vient d'être créé » et s'arrête : c'est normal.

**C7. Remplir vos réglages d'e-mail.** Onglet **Files** > cliquez `aesm` > cliquez le fichier `.env` (il est caché dans certains affichages : sinon tapez `nano .env` dans la console ; sauvegarde = Ctrl+O puis Entrée, sortie = Ctrl+X). Modifiez **3 lignes** :
```
EMAIL_HOST_USER=aesm.test@gmail.com
EMAIL_HOST_PASSWORD=les16lettresSansEspaces
DEFAULT_FROM_EMAIL="AESM <aesm.test@gmail.com>"
```
Ne touchez à rien d'autre. Sauvegardez (« Save »).

**C8. Deuxième lancement : la vraie installation.**
```
bash deploy/pythonanywhere/setup.sh
```
Environ 20 secondes. À la fin il affiche le **mot de passe des comptes de démo** (ex. `Aesm-xxxxxxxxxxx`) : notez-le. Il est aussi dans `.env` (ligne `DEMO_PASSWORD`).

**C9. Tester l'envoi d'e-mail** (remplacez par votre adresse perso) :
```
python manage.py test_email votre.adresse@exemple.com
```
Attendu : « OK : 1 e-mail envoyé ». Vérifiez votre boîte (et les spams). **Si vous voyez ÉCHEC**, ne continuez pas : allez à la partie F (E-mail).

**C10. Créer l'application web.** Onglet **Web** > « Add a new web app » > Next > choisissez **Manual configuration** (pas « Django ») > choisissez la **même version Python** qu'à l'étape C4 > Next.

**C11. Régler la page Web.** Remplissez ces champs :
1. **Source code** et **Working directory** : `/home/PA/aesm`
2. **Virtualenv** : `/home/PA/.virtualenvs/aesm-venv` (cliquez sur le texte rouge « Enter path », tapez, validez par la coche)
3. **WSGI configuration file** : cliquez sur le lien (ex. `/var/www/PA_pythonanywhere_com_wsgi.py`). **Supprimez tout** son contenu et collez le contenu du fichier `deploy/pythonanywhere/wsgi_pythonanywhere.py` (vous pouvez l'ouvrir dans l'onglet Files). Dans ce texte remplacez `VOTRE_NOM` par `PA`. Cliquez « Save ».

**C12. Fichiers statiques** (images, styles : sans cela le site s'affiche tout nu). Sur la page Web, section « Static files », cliquez « Enter URL » et ajoutez **2 lignes** :
| URL | Directory |
|---|---|
| `/static/` | `/home/PA/aesm/staticfiles` |
| `/media/` | `/home/PA/aesm/media` |

**C13. HTTPS.** Section « Security » : mettez **Force HTTPS** sur « Enabled ».

**C14. Démarrer.** En haut de la page Web, gros bouton vert **Reload PA.pythonanywhere.com**. Attendez 10 secondes puis cliquez le lien `PA.pythonanywhere.com` : votre site s'affiche.

---
## PARTIE D : vérifier que tout marche (cochez)

- [ ] La page d'accueil s'affiche avec images et couleurs.
- [ ] Connexion : `ADMIN01` + mot de passe de démo (C8) > vous arrivez dans l'espace. (Le mot de passe du README ne marche plus : c'est voulu.)
- [ ] Déconnexion, puis **Adhérer** avec une vraie adresse e-mail à vous : vous recevez l'e-mail « Bienvenue : confirmez votre adresse » (vérifiez les spams). Cliquez le lien : adresse confirmée.
- [ ] « Mot de passe oublié » avec cette adresse : e-mail reçu, le lien permet de choisir un nouveau mot de passe.
- [ ] Connecté en membre actif : Cotisations > Payer > page **simulée** > « réussi » > reçu PDF téléchargeable.
- [ ] Connecté en `TRES01` : espace Gestion > Paiements : le paiement apparaît.
- [ ] Documents : un PDF se télécharge. Gestion > Documents > Modifier : s'ouvre sans erreur.

---
## PARTIE E : mettre à jour plus tard

Sur votre PC, après modification : Git Bash dans le dossier `aesm` :
```
git add .
git commit -m "Description du changement"
git push
```
Sur PythonAnywhere, console Bash :
```
cd ~/aesm
git pull
bash deploy/pythonanywhere/setup.sh
```
puis onglet Web > **Reload**. (Vos données, `.env`, base et fichiers ne sont pas touchés.)

**Tâche quotidienne de nettoyage** (expiration des adhésions, etc.) : onglet **Tasks** > heure au choix > commande :
```
cd /home/PA/aesm && DJANGO_SETTINGS_MODULE=config.settings.prod /home/PA/.virtualenvs/aesm-venv/bin/python manage.py housekeeping
```
**Sauvegarde simple** : `cp ~/aesm/db.sqlite3 ~/sauvegarde-$(date +%F).db`, puis téléchargez-la depuis l'onglet Files.

**Compte gratuit : prolongation.** PythonAnywhere désactive l'application si vous ne cliquez pas régulièrement le bouton « Run until … / Extend » de l'onglet Web (un e-mail de rappel est envoyé). Pensez-y.

---
## PARTIE F : en cas de problème

D'abord, regardez l'onglet **Web > Log files > Error log** : la dernière ligne dit presque toujours la cause.

| Symptôme | Cause probable | Solution |
|---|---|---|
| « Something went wrong :( » | Erreur de démarrage | Error log. Cas courant : `RuntimeError` sur `.env` (clé trop courte, `EMAIL_HOST` vide) : corrigez `.env`, Reload. |
| « Bad Request (400) » | Adresse non autorisée | Dans `.env`, `DJANGO_ALLOWED_HOSTS=PA.pythonanywhere.com` exact. Reload. |
| « 403 CSRF » à la connexion | `SITE_URL` incorrect | `.env` : `SITE_URL=https://PA.pythonanywhere.com` (https, sans `/` final). Reload. |
| « Too many redirects » | Double redirection HTTPS | `.env` : `SECURE_SSL_REDIRECT=0` (laissez Force HTTPS activé sur la page Web). Reload. |
| Site sans images ni styles | Fichiers statiques | Vérifier C12 (chemins exacts) ; relancer `setup.sh` ; Reload. |
| Images des actualités absentes | Dossier media | Vérifier la ligne `/media/` de C12 et que `~/aesm/media` existe. |
| `test_email` affiche ÉCHEC « Authentication » | Mauvais mot de passe d'application | Refaire B3, recopier **sans espaces**, enregistrer `.env`. |
| `test_email` affiche ÉCHEC « Network unreachable / not allowed » | Le compte gratuit limite l'accès internet sortant | Vérifier que `EMAIL_HOST=smtp.gmail.com` et `EMAIL_PORT=587` ; sinon consulter l'aide « whitelist » de PythonAnywhere ou passer au compte payant (le plus simple). |
| Inscription réussie mais **aucun e-mail** | Le site **cache volontairement** les erreurs d'envoi pour ne pas bloquer l'inscription | Lancer `python manage.py test_email …` ; lire l'Error log ; regarder les spams. |
| « Trop de tentatives » (429) | Limites anti-abus | Attendre 15 minutes. Les limites sont par adresse IP. |
| Quota CPU dépassé | Compte gratuit (CPU limité par jour) | Éviter de relancer `seed_demo --force` ; patienter jusqu'au lendemain. |
| Mot de passe de démo oublié | | `grep DEMO_PASSWORD ~/aesm/.env` |

---
## PARTIE G : à savoir avant d'inviter des testeurs

- **Le paiement est SIMULÉ** : n'importe quel membre peut se déclarer « payé ». C'est normal pour une V1 de test, **inacceptable en vrai**. Les pages de paiement affichent un bandeau « simulé ».
- Les comptes de démonstration (dont `ADMIN01`, super administrateur) existent : gardez le mot de passe privé et ne publiez pas l'adresse largement.
- **Ne saisissez pas de vraies données personnelles** dans ce site de test.
- Les seuls e-mails envoyés par l'application sont : e-mail de bienvenue/confirmation d'adresse et réinitialisation du mot de passe. Les autres notifications (paiement confirmé, quitus...) sont **dans le site** (cloche), pas par e-mail.
- Base SQLite : suffisante pour quelques testeurs, pas pour le site définitif (prévoir MySQL et un hébergement plus solide).
- Avant la vraie mise en production : reprendre la checklist de l'audit (vrai paiement, vérification des matricules, sauvegardes hors-site...).

## Ce qui a été testé, et ce qui ne l'a pas été
Testé automatiquement (dans un environnement vierge simulant `git clone` puis `setup.sh`, réglages production, vrai dialogue SMTP vers un serveur de test local) : installation, relance sans danger, HTTPS, connexion (mot de passe public refusé, privé accepté), inscription + e-mail + clic sur le lien, mot de passe oublié par e-mail, paiement simulé + reçu, 57 tests unitaires.
**Non testé** (impossible hors ligne) : l'interface réelle de PythonAnywhere (les noms de boutons peuvent légèrement varier), l'envoi réel vers Gmail depuis un compte gratuit PythonAnywhere, l'en-tête d'adresse IP fournie par PythonAnywhere (`TRUST_X_FORWARDED_FOR=1` est un choix à confirmer).
