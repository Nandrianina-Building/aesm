# Plan de tests

**Automatisés** (`python manage.py test tests`, 53 tests) : adhésion (acceptation, refus, nouvelle soumission, doublons), paiement simulé (réussi, échoué, annulé, nouvel essai, propriétaire seul, désactivation) et confirmation manuelle
(reçu + quitus + écriture comptable), mauvais montant, double paiement, référence réutilisée, idempotence, webhook Tokipay (signature, rejeu), Tokipay non configuré,
remboursement, IDOR (paiement, reçu, quitus), droits par rôle, verrouillage de connexion, documents (visibilité, faux PDF, .exe, stockage privé),
événements (capacité, doublon, non-membre, clôture, billet à usage unique, événement payant, expiration, annulation), finances
(immuabilité, annulation, rapports versionnés, circuit de validation), vérification QR, journal d'audit en ajout seul, pages publiques / membre / gestion, jeu de données de démonstration (cohérence et idempotence).

**Manuels à exécuter avant mise en service** :
1. Parcours complet sur MySQL réel : inscription → adhésion → paiement simulé → reçu/quitus PDF → scan du QR depuis un téléphone.
2. Navigateurs : Chrome, Firefox, Edge ; mobile Android ; connexion lente (3G).
3. Concurrence : 2 membres réservant la dernière place simultanément (deux navigateurs).
4. Sauvegarde puis restauration complète sur une machine de test.
5. Revue des droits : se connecter avec chaque rôle et vérifier menus et accès directs par URL.
6. Accessibilité : navigation clavier, contrastes, lecteur d'écran sur les formulaires.
7. Test de charge léger (ex. Locust) sur l'accueil, la connexion et la réservation.

8. Au passage à Tokipay : recette sur petits montants réels, test du webhook (signature valide/invalide, rejeu), simulation désactivée.
