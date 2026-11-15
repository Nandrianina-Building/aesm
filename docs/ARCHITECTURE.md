# Architecture

Monolithe Django modulaire : une application par domaine métier, logique métier dans `services.py` (transactions atomiques),
vues fines, contrôle d'accès dans `core/permissions.py`.

## Modèle conceptuel (simplifié)
```mermaid
erDiagram
  USER ||--o{ MEMBERSHIP : soumet
  USER }o--o{ ROLE : possede
  USER ||--o| MEMBER_PROFILE : a
  USER ||--o| MEMBER_CARD : detient
  USER ||--o{ CONTRIBUTION_DUE : doit
  CONTRIBUTION_TYPE ||--o{ CONTRIBUTION_DUE : genere
  CONTRIBUTION_DUE ||--o{ PAYMENT : regle
  EVENT ||--o{ RESERVATION : recoit
  USER ||--o{ RESERVATION : effectue
  RESERVATION ||--o{ PAYMENT : regle
  RESERVATION ||--o| TICKET : emet
  TICKET ||--o| ATTENDANCE : valide
  PAYMENT ||--o| RECEIPT : produit
  PAYMENT ||--o{ QUITUS : justifie
  PAYMENT ||--o{ BUDGET_ENTRY : alimente
  PAYMENT ||--o{ PAYMENT_ATTEMPT : tente
  BUDGET_ENTRY ||--o| BUDGET_ENTRY : annule
  FINANCIAL_REPORT }o--|| USER : cree
  PUBLICATION ||--o{ COMMENT : recoit
  PUBLICATION ||--o{ LIKE : recoit
  USER ||--o{ SUPPORT_TICKET : ouvre
  SUPPORT_TICKET ||--o{ SUPPORT_MESSAGE : contient
  USER ||--o{ NOTIFICATION : recoit
  USER ||--o{ AUDIT_LOG : genere
```

## Machines d'états
- **Adhésion** : brouillon → en attente → vérification → acceptée / refusée ; acceptée ↔ suspendue ; → expirée (refusée → nouvelle soumission).
- **Paiement** : créé → en attente → en cours / vérification → confirmé / échoué / annulé ; confirmé → remboursé. Transitions codées dans `Payment.TRANSITIONS`.
- **Réservation** : en attente de paiement → confirmée / expirée / annulée ; gratuite : confirmée directement.
- **Billet** : valide → utilisé (une seule fois) / révoqué.
- **Opération financière** : en attente → validée (immuable) / rejetée ; correction = écriture inverse.
- **Rapport** : brouillon → validé (président) → publié (trésorier) ; nouvelle version par période.

## Choix techniques notables
- **MySQL** : pas d'index unique partiel (non supporté) → unicités métier garanties par verrous applicatifs + contraintes simples.
- Montants en `DecimalField(decimal_places=0)` (Ariary sans décimales) ; monnaie `MGA`.
- Numérotation sans trous ni doublons via `core.Sequence` (verrou `FOR UPDATE`).
- Fichiers privés : `private/` hors racine publique, accès par vues contrôlées ; seules les images publiques vont dans `media/`.
- Abstraction `payments/providers.py` : brancher l'API réelle = implémenter `initiate()` d'une sous-classe.
- Jobs : `expire_reservations` (toutes les 10 min) et `housekeeping` (quotidien) via cron.
