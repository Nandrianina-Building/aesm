# Sécurité - mesures mises en œuvre et limites

| Risque | Mesure | Où |
|---|---|---|
| Mots de passe | min. 12 caractères, validateurs Django, hachage Argon2 en production | `settings/base.py` |
| Force brute | verrouillage progressif après 5 échecs (par IP + matricule), journalisation dès 3 échecs | `accounts/views.py` |
| Sessions | cookies HttpOnly/SameSite, Secure + HSTS en prod, expiration 2 h (responsables : 30 min), déconnexion POST | `settings`, `core/middleware.py` |
| Contrôle d'accès | RBAC côté serveur sur chaque vue (`perm_required`, `member_required`), moindre privilège par rôle | `core/permissions.py` |
| IDOR | toute ressource personnelle filtrée par propriétaire (404 sinon) ; identifiants publics non devinables (UUID, jetons `token_urlsafe`) | vues payments / certificates / support / events |
| Montants falsifiés | le montant vient toujours de la base, jamais du formulaire ; contrôle du montant reçu par le trésorier | `payments/services.py` |
| Double paiement / rejeu | clé d'idempotence, unicité (moyen, référence transaction), verrous `select_for_update`, confirmation idempotente, événements webhook uniques | `payments/` |
| Webhook | signature HMAC-SHA256 obligatoire, secret en variable d'environnement, refus si non configuré (format à adapter à Tokipay) | `payments/views.py` |
| Simulation de paiement | réservée au propriétaire, un seul résultat, désactivable (`PAYMENT_SIMULATION_ENABLED=0`) ; **à désactiver avant tout encaissement réel** | `payments/services.py` |
| Surréservation | verrou sur l'événement, comptage des places retenues, billets à usage unique (mise à jour atomique) | `events/services.py` |
| Fichiers | PDF/JPG/PNG seulement, taille limitée, contrôle de la signature binaire, nom interne aléatoire, stockage privé hors `MEDIA_ROOT`, téléchargement via vue contrôlée | `core/validators.py`, `core/storage.py` |
| XSS / injection | auto-échappement des gabarits, ORM uniquement, CSP, `nosniff`, `X-Frame-Options: DENY` | middleware |
| CSRF | jeton sur tous les formulaires POST ; seul le webhook est exempté (signature) | Django |
| Injection CSV/Excel | préfixe `'` sur les cellules commençant par `= + - @` | `events/admin_views.py`, `finance/exports.py` |
| Intégrité financière | opérations validées immuables, correction par écriture inverse, rapports figés et versionnés | `finance/models.py` |
| Traçabilité | journal d'audit en ajout seul (ORM bloque modification/suppression), valeurs sensibles masquées | `audit/` |
| Vérification publique | limitation de débit, données minimales (prénom + initiale, matricule masqué) | `certificates/views.py` |

## Limites connues / à faire avant mise en production
1. **Authentification à deux facteurs** (recommandée pour les responsables) : non implémentée (piste : `django-otp`).
2. **Antivirus** sur les fichiers téléversés : non intégré (piste : ClamAV).
3. **Réauthentification** avant actions critiques : non implémentée.
4. Cache de limitation de débit : base de données en production ; Redis recommandé si trafic élevé.
5. Un audit de sécurité externe / test d'intrusion reste nécessaire avant l'ouverture au public.
6. Le webhook utilise un format générique à adapter à la documentation réelle de Tokipay ; la simulation de paiement doit être désactivée en exploitation réelle.
7. Conformité données personnelles : définir et publier la politique de confidentialité et de conservation.
