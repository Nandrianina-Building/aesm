# Guide des responsables (`/gestion/`)
| Rôle | Principales tâches |
|---|---|
| Super administrateur | tout ; utilisateurs et rôles, paramètres, journal d'audit |
| Secrétaire | traiter les adhésions, publier actualités, déposer documents, modérer commentaires, réclamations, annonces ciblées, bureau |
| Trésorier | créer les cotisations et les facturer, vérifier/rejeter/rembourser les paiements, saisir recettes/dépenses, créer et publier les rapports, révoquer un quitus |
| Président | validation des opérations financières et des rapports, consultation des membres, paiements, journal d'audit |
| Responsable événementiel | créer les événements, voir/exporter les réservations, valider les billets à l'entrée |

**Routines** : facturer une cotisation (Cotisations → *Facturer aux membres*, idempotent) · suivre les paiements (Paiements ; les paiements simulés se confirment tout seuls, ceux « en vérification » se traitent via Ouvrir → montant reçu → Confirmer) ·
corriger une opération validée (Opérations → *Annuler (écriture inverse)*) · publier un rapport (créer → valider (président) → publier (trésorier)) ·
contrôle d'entrée (Événements → *Valider un billet*, ou scanner le QR : la page de vérification propose « Enregistrer la présence » aux responsables autorisés).

Premier démarrage : renseigner `/gestion/parametres/` puis attribuer les rôles. Les droits de chaque rôle se modifient dans `apps/core/permissions.py`.

**Photo du bureau** : dans Gestion → Responsables, associer le compte membre concerné pour afficher sa photo de profil sur la page publique « À propos ». Cette photo est alors publique pendant le mandat actif. Sans compte associé, utiliser la photo publique du responsable.
