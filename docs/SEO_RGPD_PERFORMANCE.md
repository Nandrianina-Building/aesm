# SEO, RGPD, sécurité web et performance

| Sujet | Où / comment |
|---|---|
| Pages légales | `/confidentialite/` (RGPD) et `/conditions-utilisation/` (CGU), liées dans le pied de page et cochées à l'inscription (consentement tracé dans le journal d'audit). **À faire relire par un juriste avant mise en ligne.** |
| HTTPS | Forcé en production (`config/settings/prod.py` : redirection, HSTS, cookies sécurisés) + `deploy/nginx.conf`. |
| Cookies / analytics | Google Analytics désactivé par défaut. Saisir l'identifiant `G-XXXXXXX` dans Gestion > Paramètres (`analytics_id`) : la bannière apparaît alors, et GA n'est chargé qu'après « Accepter ». Vide = aucun suivi, aucune bannière (seuls des cookies indispensables sont utilisés). |
| Titres / meta | `<title>`, description, canonical, Open Graph sur chaque page ; `noindex` sur les zones privées (espace, gestion, compte). |
| Sitemap / robots | `/sitemap.xml` (pages, actualités et événements publics) et `/robots.txt`. |
| Images | Textes alternatifs ; compression automatique à l'envoi (max 1600 px, JPEG progressif, métadonnées retirées) via `apps/core/images.py`. |
| Vitesse | Bootstrap et polices hébergés localement (`static/vendor`), scripts `defer`, polices préchargées, images `lazy`, CSS/JS versionnés (`?v=`), gzip + cache longue durée dans Nginx. |
| Anti-spam | Champ piège + délai minimal de remplissage (formulaires de contact et d'inscription), limitation de débit à l'inscription et au contact. |
| Erreurs | Pages 403/404/500 personnalisées. |
| API | Aucune API publique : site rendu côté serveur. Seul le webhook de paiement (`/espace/paiements/webhook/<prestataire>/`) est exposé. |
