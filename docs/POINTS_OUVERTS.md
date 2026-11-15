# Points ouverts, décisions prises et limites

## Décisions prises sur les questions ouvertes (modifiables)
| Question du cahier des charges | Décision par défaut |
|---|---|
| Paiement automatique ou manuel ? | **Simulation** pour le moment (fausse page de paiement, circuit complet identique à la production), puis **Tokipay** : voir `docs/PAIEMENTS_TOKIPAY.md`. La vérification manuelle par le trésorier reste disponible (paiements en vérification, plan B Tokipay). |
| Montant de l'adhésion, périodicité | Configurable dans « Cotisations » ; durée d'adhésion = 12 mois (paramètre). |
| Qui valide les adhésions ? | Secrétaire (et super admin). |
| Qui valide les paiements ? | Trésorier (et super admin) ; remboursement : trésorier. |
| Qui valide les opérations financières / rapports ? | Opérations : président (et super admin). Rapports : validation président, publication trésorier. |
| Validité d'un quitus | Sans limite de date par défaut ; révocable par trésorier / super admin. |
| Visiteurs et événements | Réservation réservée aux comptes connectés ; « membres uniquement » par défaut, réglable par événement. |
| Annulation / remboursement d'une réservation | Annulation jusqu'à 24 h avant (paramètre) ; si payée, le trésorier est alerté pour décider du remboursement. |
| Réservation non payée | Place retenue 60 min, prolongée de 48 h lorsqu'un paiement est soumis, puis libérée. |
| E-mail / photo obligatoires | Facultatifs, activables dans les paramètres. Sans e-mail, pas de réinitialisation autonome du mot de passe. |
| Connexion | Par **matricule** + mot de passe. |
| Groupes d'accès (publications/documents) | Non implémentés : visibilité publique ou membres uniquement. |

## Non couvert par cette version
Branchement réel de Tokipay (squelette fourni), authentification à deux facteurs, antivirus des fichiers, SMS, application mobile native, sauvegarde automatique hors serveur,
validation d'un contenu par workflow multi-étapes (la publication est directe par le secrétaire), recherche plein texte avancée, graphiques interactifs
(barres CSS simples), pagination de certaines listes d'administration (limitées à 200-300 lignes), suppression/anonymisation RGPD à la demande
(désactivation du compte possible ; l'historique financier est conservé volontairement).

## À valider avec l'association avant ouverture
Textes juridiques (conditions d'adhésion, confidentialité), contenu de « À propos », logo officiel (logo provisoire fourni), montants réels,
liste des responsables et rôles, durée de conservation des données.
