# CAHIER DES CHARGES FONCTIONNEL ET TECHNIQUE
# Plateforme numérique de gestion de l'AESM

**Projet :** Développement d'une plateforme web de gestion de l'Association des Étudiants en Sociologie de Madagascar (AESM)

**Version :** 1.0  
**Date :** Novembre 2026  
**Technologies principales :** Python, Django, JavaScript, HTML5, CSS3, MySql (change en Mysql tous les autres en bas)
**Type de projet :** Application web responsive  
**Commanditaire :** Association des Étudiants en Sociologie de Madagascar (AESM)  
**Statut du document :** Proposition de cahier des charges à valider avec les responsables de l'AESM.

---

# 1. PRÉSENTATION GÉNÉRALE DU PROJET

## 1.1. Contexte

L'Association des Étudiants en Sociologie de Madagascar (AESM) souhaite moderniser la gestion de ses activités et faciliter les interactions avec ses membres.

Actuellement, certaines opérations administratives, notamment le paiement des frais d'adhésion, peuvent entraîner des files d'attente et nécessiter des déplacements physiques.

La gestion des informations, des documents pédagogiques, des annonces, des événements et des rapports financiers peut également être améliorée grâce à une plateforme numérique centralisée.

Le projet consiste donc à concevoir et développer une application web permettant de dématérialiser une partie des opérations administratives et de faciliter l'accès aux informations de l'association.

## 1.2. Problématique

Les principales difficultés identifiées sont :

- Les files d'attente lors du paiement des adhésions.
- La gestion manuelle ou dispersée des informations des membres.
- Le suivi des cotisations et des paiements.
- La difficulté de vérifier rapidement la situation financière d'un membre.
- La distribution des documents pédagogiques.
- La communication des annonces et informations importantes.
- Le manque de centralisation des inscriptions aux événements.
- La nécessité de rendre les activités financières plus transparentes auprès des membres.

## 1.3. Solution proposée

Développer une plateforme web centralisée permettant :

- L'inscription et la gestion des membres.
- Le paiement des cotisations par Mobile Money.
- Le suivi des paiements et la génération de quitus numériques.
- La vérification des quitus à l'aide de QR Codes.
- La publication des actualités et annonces.
- La consultation et le téléchargement de documents pédagogiques.
- L'organisation des événements et la réservation des places.
- La consultation des rapports financiers.
- L'administration générale de l'association.

## 1.4. Objectifs généraux

1. Réduire les déplacements et les files d'attente liés aux adhésions.
2. Faciliter les paiements et le suivi des cotisations.
3. Centraliser les informations relatives aux membres.
4. Améliorer la communication entre l'association et ses membres.
5. Faciliter la distribution des ressources pédagogiques.
6. Simplifier l'organisation des événements.
7. Renforcer la transparence de la gestion financière.
8. Garantir la sécurité et la confidentialité des informations.

## 1.5. Objectifs spécifiques

À la fin du projet, un étudiant devra pouvoir créer un compte, soumettre une demande d'adhésion, payer ses cotisations, consulter son historique et obtenir ses justificatifs sans devoir systématiquement se rendre au bureau de l'association.

De son côté, l'administration devra pouvoir gérer les membres, les paiements, les publications, les documents, les événements et les informations financières depuis un espace sécurisé.

---

# 2. PÉRIMÈTRE DU PROJET

## 2.1. Fonctionnalités incluses

La plateforme comprendra les modules suivants :

1. Site public de présentation.
2. Gestion des comptes et des membres.
3. Gestion des adhésions.
4. Gestion des cotisations.
5. Paiements Mobile Money.
6. Gestion des reçus et quitus.
7. Vérification par QR Code.
8. Gestion des publications et actualités.
9. Gestion des commentaires et réactions.
10. Bibliothèque documentaire.
11. Gestion des événements.
12. Réservation et billetterie.
13. Gestion financière et rapports budgétaires.
14. Système de notifications.
15. Gestion des réclamations.
16. Gestion des rôles et permissions.
17. Tableau de bord administratif.
18. Journalisation des opérations sensibles.

## 2.3. Public cible

- Étudiants souhaitant adhérer à l'AESM.
- Membres actifs de l'association.
- Responsables administratifs.
- Trésorier et responsables financiers.
- Responsables événementiels.
- Visiteurs souhaitant consulter les informations publiques.

---

# 3. ACTEURS ET GESTION DES AUTORISATIONS

La plateforme devra distinguer les utilisateurs selon leurs responsabilités.

## 3.1. Visiteur

Utilisateur non connecté.

Autorisations :
- Consulter la page d'accueil.
- Consulter les informations de l'association.
- Consulter les publications publiques.
- Consulter les événements publics.
- Consulter les documents publics.
- Consulter les informations publiques du bureau.
- Créer un compte.
- Accéder à la page publique de vérification d'un quitus ou billet QR.

Restrictions :
- Aucun accès aux informations privées des membres.
- Aucun accès aux rapports financiers réservés.
- Aucun accès aux documents privés.
- Aucune interaction nécessitant un compte.

## 3.2. Membre

Utilisateur possédant un compte et dont l'adhésion a été validée.

Autorisations :
- Gérer son profil.
- Consulter son statut d'adhésion.
- Consulter ses cotisations.
- Effectuer des paiements.
- Consulter son historique de transactions.
- Télécharger ses reçus et quitus.
- Consulter sa carte numérique.
- Réserver des événements.
- Consulter les documents réservés aux membres.
- Aimer et commenter les publications.
- Modifier ou supprimer ses propres commentaires.
- Consulter les rapports financiers réservés aux membres.
- Recevoir des notifications.
- Soumettre des réclamations.

Restrictions :
- Ne peut pas modifier les informations financières.
- Ne peut pas consulter les données privées d'autres membres.
- Ne peut pas modifier les publications officielles.
- Ne peut pas accéder aux fonctionnalités administratives.

## 3.3. Super administrateur

Responsable technique et fonctionnel de la plateforme.

Autorisations :
- Gestion complète des utilisateurs.
- Gestion des rôles et permissions.
- Configuration générale.
- Gestion des cotisations.
- Gestion des paiements et validations.
- Gestion des documents.
- Gestion des publications.
- Gestion des événements.
- Gestion financière.
- Consultation des journaux d'activité.
- Gestion des paramètres de sécurité.

## 3.4. Président

Autorisations à définir avec l'association :

- Consultation du tableau de bord général.
- Supervision des membres.
- Consultation des rapports financiers.
- Validation de certaines décisions.
- Supervision des publications et événements.
- Consultation des activités administratives.

## 3.5. Trésorier

Autorisations :
- Consultation des transactions.
- Vérification des paiements.
- Gestion des recettes.
- Gestion des dépenses.
- Création des rapports financiers.
- Publication des rapports après validation.
- Exportation des données financières.

Il ne doit pas pouvoir modifier librement les paramètres de sécurité ou les comptes administrateurs.

## 3.6. Secrétaire

Autorisations :
- Gestion des demandes d'inscription.
- Consultation des membres.
- Mise à jour des informations autorisées.
- Gestion des publications.
- Gestion des documents.
- Gestion des annonces officielles.

## 3.7. Responsable événementiel

Autorisations :
- Création des événements.
- Modification des événements.
- Gestion des réservations.
- Consultation des participants.
- Vérification des billets QR.
- Exportation des listes de participants.

## 3.8. Principe de gestion des permissions

Les permissions devront être définies selon le principe du moindre privilège.

Chaque utilisateur ne doit disposer que des autorisations nécessaires à ses responsabilités.

Les rôles proposés ne sont pas nécessairement cumulables. L'administration pourra attribuer plusieurs rôles à une même personne si les règles de l'association le permettent.

---

# 4. SPÉCIFICATIONS FONCTIONNELLES

# 4.1. Module de présentation publique

### Objectif

Présenter l'AESM et permettre aux visiteurs de découvrir l'association.

### Pages nécessaires

**A. Page d'accueil**

Contenu :
- Logo de l'AESM.
- Barre de navigation.
- Présentation de l'association.
- Message de bienvenue.
- Présentation des missions.
- Actualités récentes.
- Événements à venir.
- Documents publics récents.
- Bouton d'inscription.
- Pied de page avec contacts et réseaux sociaux.

**B. Page À propos**

Contenu :
- Présentation de l'AESM.
- Historique.
- Missions.
- Objectifs.
- Valeurs.
- Organisation.
- Présentation des responsables.

**C. Page Actualités**

Liste des publications publiques avec :
- Titre.
- Image éventuelle.
- Résumé.
- Date de publication.
- Catégorie.
- Lien vers le détail.

**D. Page Événements**

Présentation des événements accessibles aux visiteurs.

**E. Page Documents**

Liste des documents autorisés au téléchargement public.

**F. Page Contact**

Informations de contact de l'association et formulaire de contact facultatif.

### Exigences

- Interface responsive.
- Navigation simple.
- Chargement optimisé.
- Contenus administrables.
- Accessibilité sur ordinateur, tablette et smartphone.

---

# 4.2. Module d'inscription et d'authentification

### Objectif

Permettre aux étudiants de créer un compte personnel.

### Formulaire d'inscription

Champs proposés :

| Champ | Type | Obligatoire |
|---|---|---|
| Nom | Texte | Oui |
| Prénom | Texte | Oui |
| Matricule | Texte | Oui |
| Adresse e-mail | E-mail | À confirmer |
| Numéro de téléphone | Téléphone | Oui |
| Sexe | Choix | À confirmer |
| Photo d'identité | Image | À justifier |
| Mot de passe | Mot de passe | Oui |
| Confirmation du mot de passe | Mot de passe | Oui |

L'adresse e-mail devra être vérifiée si elle est retenue comme moyen de contact et de récupération du compte.

### Fonctionnalités

- Création de compte.
- Connexion.
- Déconnexion.
- Vérification de l'adresse e-mail.
- Réinitialisation du mot de passe.
- Modification du profil.
- Changement du mot de passe.
- Consultation du statut du compte.

### Règles de gestion

- Un matricule ne peut être associé à plusieurs membres actifs.
- Les doublons de comptes devront être détectés.
- Les mots de passe ne seront jamais stockés en clair.
- Un compte nouvellement créé ne devient pas automatiquement un membre actif.
- L'inscription devra être soumise aux règles de validation de l'association.

### Statuts du compte

- En attente de validation.
- Actif.
- Refusé.
- Suspendu.
- Désactivé.

La suspension du compte ne devra pas supprimer son historique financier.

---

# 4.3. Module de gestion des adhésions

### Objectif

Gérer les demandes d'adhésion et les périodes d'appartenance à l'association.

### Fonctionnalités

Pour les membres :
- Soumettre une demande d'adhésion.
- Consulter l'état de la demande.
- Consulter les conditions d'adhésion.
- Consulter la période d'adhésion.
- Consulter les éventuelles pièces manquantes.

Pour l'administration :
- Consulter les demandes.
- Vérifier les informations.
- Accepter ou refuser une demande.
- Ajouter un motif de refus.
- Consulter l'historique des adhésions.
- Suspendre ou réactiver une adhésion selon les règles autorisées.

### Statuts

- Brouillon.
- En attente.
- En cours de vérification.
- Acceptée.
- Refusée.
- Expirée.
- Suspendue.

### Règles

Une demande acceptée ne signifie pas nécessairement que toutes les cotisations sont payées.

Il faut distinguer :
- Le statut du compte.
- Le statut de la demande d'adhésion.
- Le statut de l'adhésion.
- La situation financière du membre.

Ces informations ne doivent pas être fusionnées dans un seul champ de statut.

---

# 4.4. Module de gestion des cotisations

### Objectif

Permettre à l'administration de définir les cotisations exigibles.

### Fonctionnalités administratives

L'administrateur autorisé pourra :

- Créer une cotisation.
- Modifier une cotisation non encore facturée.
- Définir le montant.
- Définir la période.
- Définir les membres concernés.
- Définir une date limite.
- Activer ou désactiver une cotisation.
- Consulter les paiements associés.
- Consulter les montants collectés.

### Informations d'une cotisation

- Nom.
- Description.
- Montant en ariary.
- Date de début.
- Date de fin.
- Année ou période concernée.
- Catégorie.
- Statut.
- Public concerné.

### Exemple

| Cotisation | Montant | Période |
|---|---:|---|
| Adhésion annuelle | 2 000 Ar | 2026 |
| Cotisation spéciale | 5 000 Ar | À définir |
| Participation exceptionnelle | Variable | Ponctuelle |

Les montants sont des exemples et doivent être configurables.

### Règles de gestion

- Un montant facturé doit être conservé dans l'historique même si le tarif général change ultérieurement.
- Une modification de tarif ne doit pas modifier rétroactivement les paiements.
- Une cotisation déjà payée ne doit pas pouvoir être facturée une seconde fois par erreur.
- Les exonérations et réductions, si elles existent, doivent être enregistrées avec un motif et un responsable autorisé.

---

# 4.5. Module de paiement Mobile Money

### Objectif

Permettre le règlement des cotisations sans déplacement physique.

### Moyens de paiement envisagés

- MVola.
- Orange Money.
- Autres moyens autorisés ultérieurement.

### Parcours utilisateur

1. Le membre se connecte.
2. Il consulte les cotisations exigibles.
3. Il sélectionne une cotisation.
4. Il choisit un moyen de paiement.
5. Le serveur crée une transaction.
6. Le prestataire de paiement traite l'opération.
7. L'application reçoit ou récupère la confirmation.
8. Le serveur vérifie la transaction.
9. Le statut est mis à jour.
10. Le reçu et, si les conditions sont réunies, le quitus sont générés.

### Informations d'une transaction

- Identifiant interne.
- Identifiant de cotisation ou d'événement.
- Membre concerné.
- Montant.
- Devise.
- Moyen de paiement.
- Référence externe.
- Date de création.
- Date de confirmation.
- Statut.
- Motif d'échec éventuel.

### Statuts

- Créée.
- En attente.
- En cours.
- Confirmée.
- Échouée.
- Annulée.
- Remboursée.
- En cours de vérification.

### Gestion des paiements manuels

Si l'intégration API n'est pas immédiatement possible, un mode de paiement manuel pourra être proposé.

Dans ce cas :
- L'application affiche les instructions de paiement.
- Le membre effectue le paiement.
- Il fournit la référence de transaction.
- Il peut transmettre une preuve si nécessaire.
- Le trésorier vérifie la transaction.
- Le paiement reste en attente jusqu'à sa validation.

La capture d'écran d'un paiement ne constitue pas une preuve suffisante à elle seule.

### Sécurité et fiabilité

- Aucune validation par simple redirection du navigateur.
- Vérification serveur auprès du prestataire.
- Vérification de la signature des notifications lorsque le prestataire le permet.
- Protection contre les notifications répétées.
- Protection contre les doubles paiements.
- Journalisation des opérations.
- Conservation des références de transaction.
- Vérification du montant et du destinataire.

Les intégrations MVola et Orange Money devront être conditionnées à l'obtention des accès marchands et des documentations techniques officielles.

---

# 4.6. Module de reçus, quitus et QR Codes

### Objectif

Fournir une preuve numérique vérifiable du paiement et de la situation du membre.

### A. Reçu de paiement

Contenu :
- Numéro du reçu.
- Nom du membre.
- Matricule.
- Cotisation concernée.
- Montant.
- Moyen de paiement.
- Référence de transaction.
- Date de confirmation.
- Identité de l'association.

### B. Quitus numérique

Contenu :
- Logo AESM.
- Numéro unique du quitus.
- Nom et prénom.
- Matricule.
- Cotisation concernée.
- Période concernée.
- Montant validé.
- Date de délivrance.
- Date de validité, si applicable.
- QR Code.

### C. Vérification du QR Code

Le QR Code redirige vers une page de vérification publique.

La page affiche :
- Authenticité du document.
- Numéro du quitus.
- Statut : valide, expiré ou révoqué.
- Date de délivrance.
- Informations minimales permettant de confirmer le titulaire.

Les données personnelles non nécessaires ne seront pas exposées.

### D. Gestion administrative

- Génération automatique.
- Consultation.
- Téléchargement PDF.
- Révocation en cas d'erreur ou de fraude.
- Historique des émissions.
- Vérification des documents.

Un quitus révoqué ne doit jamais redevenir valide simplement parce qu'un ancien PDF est encore disponible.

---

# 4.7. Module de carte numérique du membre

### Objectif

Identifier rapidement un membre de l'AESM.

### Contenu

- Logo.
- Photo du membre.
- Nom et prénom.
- Matricule.
- Numéro de membre.
- Année d'adhésion.
- Statut du membre.
- QR Code.

### Fonctionnalités

- Affichage dans l'espace personnel.
- Téléchargement PDF.
- Vérification de l'authenticité.
- Mise à jour contrôlée des informations.

La carte de membre et le quitus sont deux documents distincts.

---

# 4.8. Module de publications et actualités

### Objectif

Centraliser la communication officielle de l'association.

### Types de publications

- Actualité.
- Annonce officielle.
- Communiqué.
- Information pédagogique.
- Avis important.
- Annonce d'événement.
- Appel à participation.
- Information administrative.

### Fonctionnalités administratives

- Créer une publication.
- Modifier une publication.
- Supprimer ou archiver une publication.
- Ajouter une image.
- Choisir une catégorie.
- Définir la visibilité.
- Planifier la publication.
- Épingler une annonce.
- Désactiver les commentaires.

### Visibilité

- Publique.
- Membres uniquement.
- Éventuellement réservée à un groupe particulier.

### Interactions des membres

- Aimer une publication.
- Retirer son appréciation.
- Commenter.
- Modifier son commentaire.
- Supprimer son commentaire.

### Modération

Les responsables autorisés pourront :
- Masquer un commentaire.
- Supprimer un commentaire inapproprié.
- Consulter les signalements.
- Désactiver les commentaires d'une publication.

### Statuts

- Brouillon.
- Programmée.
- Publiée.
- Archivée.

---

# 4.9. Module de documents pédagogiques

### Objectif

Mettre à disposition une bibliothèque documentaire centralisée.

### Types de documents

- Cours.
- Travaux dirigés.
- Travaux pratiques.
- Exercices.
- Examens.
- Corrigés.
- Supports de formation.
- Rapports.
- Documents administratifs.

### Fonctionnalités administratives

- Ajouter un document.
- Modifier ses informations.
- Supprimer ou archiver un document.
- Définir sa catégorie.
- Définir son niveau.
- Ajouter une description.
- Définir sa visibilité.
- Consulter les statistiques de téléchargement.

### Fonctionnalités utilisateur

- Parcourir les documents.
- Rechercher un document.
- Filtrer par catégorie.
- Consulter les informations.
- Télécharger les documents autorisés.

### Paramètres initiaux proposés

- Formats autorisés : PDF uniquement.
- Taille maximale : 10 Mo par fichier.
- Nom du document.
- Description.
- Catégorie.
- Date de publication.
- Niveau concerné.
- Visibilité publique ou membres uniquement.

La limite pourra être modifiée depuis la configuration administrative.

Les fichiers privés seront stockés dans un emplacement non directement accessible publiquement.

---

# 4.10. Module d'événements et réservations

### Objectif

Permettre à l'association d'organiser des activités et de gérer les participations.

### Création d'un événement

Champs :
- Titre.
- Description.
- Image.
- Catégorie.
- Date.
- Heure.
- Lieu.
- Nombre de places.
- Date limite d'inscription.
- Prix.
- Type de participation.
- Visibilité.
- Conditions de participation.
- Statut.

### Types d'événements

- Gratuit.
- Payant.
- Réservé aux membres.
- Ouvert aux visiteurs.
- Sur invitation.

### Exemple

Une sortie organisée par l'AESM :

- Nombre de places : 50.
- Prix : 20 000 Ar.
- Inscription : ouverte.
- Date limite : définie par l'administration.

### Fonctionnalités pour les participants

- Consulter les événements.
- Réserver une place.
- Payer si nécessaire.
- Consulter sa réservation.
- Annuler selon les conditions.
- Télécharger son billet.
- Présenter son QR Code à l'entrée.

### Fonctionnalités administratives

- Créer un événement.
- Modifier un événement.
- Ouvrir ou fermer les inscriptions.
- Consulter les réservations.
- Vérifier les paiements.
- Gérer les annulations.
- Exporter la liste des participants.
- Scanner les billets QR.
- Marquer les participants présents.

### Gestion des places

Le système devra :
- Empêcher les dépassements de capacité.
- Gérer les réservations simultanées.
- Prévoir une expiration des réservations non payées.
- Libérer les places après expiration.
- Éviter la double réservation d'un même membre.
- Conserver l'historique des annulations.

### Billet numérique

Chaque réservation confirmée pourra générer un billet PDF avec un QR Code unique.

Le QR Code devra être vérifié côté serveur et ne pourra être utilisé qu'une seule fois pour l'enregistrement de présence.

---

# 4.11. Module de gestion financière

### Objectif

Permettre aux membres de consulter des rapports financiers détaillés.

### Types de mouvements

**Recettes :**
- Cotisations.
- Participations aux événements.
- Dons.
- Contributions exceptionnelles.
- Autres recettes.

**Dépenses :**
- Organisation d'événements.
- Transport.
- Fournitures.
- Communication.
- Location.
- Autres dépenses.

### Informations d'une opération

- Numéro de référence.
- Type : recette ou dépense.
- Catégorie.
- Description.
- Montant.
- Date.
- Responsable.
- Justificatif éventuel.
- Statut de validation.
- Date de validation.

### Tableau financier

Le tableau de bord pourra afficher :

- Solde initial.
- Total des recettes.
- Total des dépenses.
- Solde final.
- Répartition des recettes.
- Répartition des dépenses.
- Évolution financière.
- Historique des opérations.

### Exemple

| Indicateur | Montant |
|---|---:|
| Solde initial | 500 000 Ar |
| Recettes | 250 000 Ar |
| Dépenses | 120 000 Ar |
| Solde final | 630 000 Ar |

### Fonctionnalités

- Filtrage par période.
- Filtrage par catégorie.
- Consultation détaillée.
- Graphiques.
- Export PDF.
- Export Excel.
- Publication des rapports.
- Historique des rapports publiés.

### Gestion des validations

Les opérations financières devront suivre un circuit de validation.

Une opération validée ne pourra pas être supprimée silencieusement. Une correction devra produire une nouvelle écriture d'annulation ou de régularisation, avec justification et traçabilité.

Les rapports publiés devront conserver une version historique.

### Accès

Les informations financières détaillées seront réservées aux membres authentifiés et aux responsables autorisés, selon les permissions définies.

Les données bancaires ou personnelles confidentielles ne seront pas affichées dans les rapports publics ou réservés aux membres.

---

# 4.12. Module de notifications

### Objectif

Informer les utilisateurs des événements importants.

### Notifications possibles

- Inscription reçue.
- Inscription acceptée.
- Inscription refusée.
- Cotisation créée.
- Cotisation bientôt exigible.
- Paiement confirmé.
- Paiement échoué.
- Quitus disponible.
- Nouvelle publication.
- Nouvel événement.
- Réservation confirmée.
- Réservation annulée.
- Réclamation traitée.

### Fonctionnalités

- Liste des notifications.
- Marquage comme lue.
- Marquage comme non lue.
- Suppression de notifications selon les règles de conservation.
- Compteur de notifications non lues.

### Évolutions

- Notifications par e-mail.
- Notifications SMS.
- Rappels automatiques.

---

# 4.13. Module de réclamations et assistance

### Objectif

Permettre aux membres de signaler les problèmes rencontrés.

### Motifs possibles

- Paiement non confirmé.
- Erreur sur les informations personnelles.
- Problème de quitus.
- Problème de réservation.
- Problème de connexion.
- Autre demande.

### Fonctionnalités

- Création d'une réclamation.
- Description du problème.
- Ajout éventuel d'une pièce justificative.
- Attribution à un responsable.
- Réponse administrative.
- Consultation de l'historique.
- Fermeture de la demande.

### Statuts

- En attente.
- En cours.
- Résolu.
- Rejeté.
- Fermé.

Les pièces jointes devront être contrôlées avant stockage.

---

# 4.14. Module de gestion des responsables

### Objectif

Présenter les membres du bureau et organiser leurs responsabilités.

### Fonctionnalités

- Ajouter un responsable.
- Définir sa fonction.
- Ajouter une photo facultative.
- Définir son mandat.
- Modifier les informations.
- Archiver les anciens mandats.

### Informations

- Nom.
- Prénom.
- Fonction.
- Date de début du mandat.
- Date de fin du mandat.
- Photo facultative.
- Description.

Cette section pourra être publique.

---

# 4.15. Tableau de bord du membre

Le membre disposera d'un espace personnel comprenant :

1. Vue d'ensemble.
2. Mon profil.
3. Ma carte de membre.
4. Mes adhésions.
5. Mes cotisations.
6. Mes paiements.
7. Mes reçus.
8. Mes quitus.
9. Mes réservations.
10. Documents pédagogiques.
11. Publications.
12. Notifications.
13. Mes réclamations.
14. Paramètres du compte.
15. Déconnexion.

La page d'accueil du tableau de bord affichera notamment :
- Statut de l'adhésion.
- Cotisations à régler.
- Derniers paiements.
- Prochains événements.
- Dernières annonces.
- Notifications non lues.

---

# 4.16. Tableau de bord administratif

### Objectif

Centraliser la gestion de l'association.

### Modules administratifs

| Module | Fonction |
|---|---|
| Vue d'ensemble | Statistiques générales |
| Membres | Gestion des membres |
| Adhésions | Demandes et validation |
| Cotisations | Configuration des tarifs |
| Paiements | Transactions et vérifications |
| Quitus | Génération et révocation |
| Cartes | Gestion des cartes |
| Publications | Actualités et annonces |
| Commentaires | Modération |
| Documents | Bibliothèque documentaire |
| Événements | Création et gestion |
| Réservations | Participants et billets |
| Finances | Recettes et dépenses |
| Rapports | Publication financière |
| Notifications | Gestion des annonces ciblées |
| Réclamations | Traitement des demandes |
| Responsables | Gestion des rôles |
| Journal d'audit | Historique des actions |
| Paramètres | Configuration générale |

### Indicateurs

- Nombre total de comptes.
- Nombre de membres actifs.
- Demandes en attente.
- Cotisations exigibles.
- Paiements confirmés.
- Paiements en attente.
- Montant total des recettes.
- Montant total des dépenses.
- Événements à venir.
- Réservations.
- Réclamations ouvertes.

Les indicateurs financiers devront être calculés à partir des écritures validées, et non de simples demandes de paiement.

---

# 5. RÈGLES MÉTIER GÉNÉRALES

Les règles suivantes doivent être appliquées dans toute l'application.

**RG-01 :** Chaque compte utilisateur possède un identifiant unique.

**RG-02 :** Un membre doit être validé selon les règles de l'association avant d'obtenir le statut de membre actif.

**RG-03 :** Un paiement n'est considéré comme confirmé qu'après vérification fiable.

**RG-04 :** Un paiement confirmé ne peut pas être modifié directement.

**RG-05 :** Chaque transaction possède une référence unique.

**RG-06 :** Les changements de tarifs ne modifient pas les transactions historiques.

**RG-07 :** Un quitus est délivré uniquement lorsque les conditions financières correspondantes sont satisfaites.

**RG-08 :** Un QR Code doit être vérifié côté serveur.

**RG-09 :** Un membre ne peut modifier que les informations et contenus qui lui appartiennent et pour lesquels il dispose d'une autorisation.

**RG-10 :** Les documents réservés aux membres nécessitent une authentification et une vérification des permissions.

**RG-11 :** Les événements payants nécessitent une confirmation du paiement avant validation définitive de la réservation.

**RG-12 :** Le nombre de réservations confirmées ne doit jamais dépasser la capacité de l'événement.

**RG-13 :** Les opérations financières validées doivent être traçables.

**RG-14 :** Les utilisateurs suspendus ne peuvent plus effectuer les opérations interdites par leur statut.

**RG-15 :** Les informations privées des membres ne doivent jamais être accessibles publiquement.

**RG-16 :** Les actions sensibles doivent être journalisées.

**RG-17 :** Les visiteurs peuvent uniquement consulter les contenus publics.

**RG-18 :** Les suppressions de données sensibles doivent respecter une politique de conservation et les obligations applicables.

---

# 6. EXIGENCES NON FONCTIONNELLES

## 6.1. Ergonomie et expérience utilisateur

- Interface simple et intuitive.
- Navigation cohérente.
- Formulaires compréhensibles.
- Messages d'erreur explicites.
- Confirmation des actions importantes.
- Affichage adapté aux différents écrans.
- Respect des principes d'accessibilité.
- Interface en français dans la première version.

## 6.2. Compatibilité

La plateforme devra être compatible avec les navigateurs récents :

- Google Chrome.
- Microsoft Edge.
- Mozilla Firefox.
- Safari.

Elle devra fonctionner sur :
- Ordinateurs.
- Tablettes.
- Smartphones Android.
- Smartphones iOS.

## 6.3. Performance

Objectifs initiaux :

- Temps de réponse courant inférieur à 2 secondes dans des conditions normales.
- Pagination des listes volumineuses.
- Optimisation des images.
- Compression des ressources statiques.
- Chargement différé des images lorsque pertinent.
- Optimisation des requêtes SQL.
- Mise en cache des contenus publics lorsque possible.

Les opérations de paiement et de génération de documents pourront nécessiter davantage de temps et devront afficher un état de traitement.

## 6.4. Disponibilité

- Objectif de disponibilité : 99 % mensuel, hors maintenance planifiée.
- Surveillance des erreurs.
- Sauvegardes régulières.
- Procédure de restauration.
- Documentation des opérations de maintenance.

## 6.5. Évolutivité

L'architecture devra permettre :
- L'ajout de nouveaux moyens de paiement.
- L'ajout de nouveaux types de cotisations.
- L'ajout de nouveaux rôles.
- L'ajout de nouvelles fonctionnalités.
- L'augmentation du nombre de membres.
- L'évolution vers une application mobile.

## 6.6. Maintenabilité

- Code organisé en applications Django.
- Respect des conventions Python.
- Séparation des responsabilités.
- Réutilisation des composants.
- Documentation technique.
- Tests automatisés.
- Gestion des versions avec Git.

---

# 7. CAHIER DES CHARGES DE SÉCURITÉ

La sécurité est une exigence centrale du projet, notamment parce que l'application manipulera des données personnelles et financières.

Les mesures suivantes devront être prises dès la conception.

## 7.1. Sécurité de l'authentification

### Exigences

- Utiliser le système d'authentification sécurisé de Django.
- Hacher les mots de passe avec un algorithme adapté, sans jamais les stocker en clair.
- Imposer une politique de mots de passe robuste.
- Prévoir la réinitialisation sécurisée des mots de passe.
- Vérifier les adresses e-mail si elles sont utilisées pour l'authentification ou la récupération.
- Protéger les sessions.
- Prévoir une limitation des tentatives de connexion.
- Journaliser les connexions et échecs suspects.

### Politique de mots de passe proposée

- Minimum de 12 caractères.
- Vérification contre les mots de passe trop courants.
- Refus des mots de passe compromis connus si un mécanisme adapté est disponible.
- Pas de stockage des mots de passe en clair.
- Pas d'envoi du mot de passe par e-mail.

La politique devra rester compatible avec les mécanismes de récupération de compte.

### Sessions

- Cookies de session `HttpOnly`.
- Cookies `Secure` en production avec HTTPS.
- Attribut `SameSite` adapté.
- Expiration après inactivité.
- Déconnexion après une période définie pour les comptes administratifs.
- Invalidation des sessions après un changement de mot de passe lorsque nécessaire.

## 7.2. Gestion des rôles et autorisations

La plateforme devra appliquer un contrôle d'accès basé sur les rôles (RBAC).

Chaque requête sensible devra vérifier les autorisations côté serveur.

Exemples :

- Un membre ne peut pas consulter les informations privées d'un autre membre.
- Un trésorier ne peut pas modifier les rôles des administrateurs.
- Un responsable événementiel ne peut pas modifier les rapports financiers.
- Un visiteur ne peut pas télécharger un document réservé.
- Un membre ne peut pas modifier une transaction.
- Un utilisateur ne peut pas accéder à une page administrative en modifiant simplement son URL.

Les contrôles doivent être appliqués dans les vues, services et endpoints concernés, et pas uniquement dans les templates.

## 7.3. Protection contre les injections SQL

Utiliser exclusivement l'ORM Django pour les opérations courantes.

Lorsqu'une requête SQL brute est indispensable :
- Utiliser des requêtes paramétrées.
- Ne jamais concaténer directement les entrées utilisateur dans une requête SQL.
- Valider les paramètres.
- Limiter les privilèges du compte de base de données.

## 7.4. Protection contre les attaques XSS

Une attaque XSS peut permettre l'exécution de scripts malveillants dans le navigateur d'un utilisateur.

Mesures :
- Utiliser l'échappement automatique des templates Django.
- Éviter `safe` sur des contenus utilisateur.
- Nettoyer les contenus HTML si du HTML est autorisé.
- Valider les données reçues.
- Mettre en place une politique CSP adaptée.
- Éviter l'insertion directe de contenu non fiable avec `innerHTML`.

Les commentaires et publications ne doivent jamais permettre l'exécution de scripts arbitraires.

## 7.5. Protection contre les attaques CSRF

- Activer la protection CSRF Django.
- Utiliser les jetons CSRF dans les formulaires.
- Protéger les requêtes AJAX utilisant les méthodes de modification.
- Ne jamais utiliser GET pour effectuer une opération sensible.
- Vérifier les origines lorsque nécessaire.

## 7.6. Protection contre les attaques IDOR

Une attaque IDOR permet à un utilisateur d'accéder aux données d'un autre utilisateur en modifiant un identifiant dans une URL ou une requête.

Exemple :

Un membre modifie l'URL de son reçu pour essayer de consulter le reçu d'un autre membre.

Mesures :
- Vérification systématique de la propriété de la ressource.
- Vérification des permissions.
- Utilisation d'identifiants non prévisibles lorsque pertinent.
- Contrôle côté serveur pour chaque accès.
- Tests spécifiques sur les accès entre utilisateurs.

Un identifiant difficile à deviner ne remplace jamais un contrôle d'autorisation.

## 7.7. Sécurité des paiements

Les paiements constituent l'une des parties les plus sensibles.

Exigences :

1. Les montants sont calculés et contrôlés côté serveur.
2. Le client ne peut pas imposer un montant arbitraire.
3. Les références de transaction doivent être uniques.
4. Les notifications de paiement doivent être authentifiées lorsque le prestataire le permet.
5. Les signatures doivent être vérifiées.
6. Les confirmations répétées ne doivent pas créer plusieurs paiements.
7. Les paiements échoués ne doivent pas générer de quitus.
8. Les transactions doivent être journalisées.
9. Les clés API ne doivent jamais apparaître dans le JavaScript.
10. Les secrets doivent être conservés dans des variables d'environnement ou un gestionnaire de secrets.
11. Les opérations de remboursement doivent être contrôlées et tracées.

### Protection contre les doubles paiements

Prévoir :
- Une clé d'idempotence.
- Un identifiant interne unique.
- Une contrainte d'unicité sur les références pertinentes.
- Une vérification du statut avant toute transition.
- Des transactions atomiques en base de données.

L'application ne doit jamais faire confiance au seul message envoyé par le navigateur après un paiement.

## 7.8. Sécurité des QR Codes

Les QR Codes ne doivent pas exposer directement les données personnelles.

Mesures :
- Utiliser des identifiants aléatoires.
- Ne pas intégrer le numéro de téléphone ou le matricule dans l'URL.
- Vérifier les documents en base de données.
- Prévoir la révocation.
- Prévoir l'expiration si nécessaire.
- Limiter les tentatives abusives de vérification.
- Ne pas considérer le QR Code comme une preuve autonome.

Pour les billets d'événement, une vérification atomique devra empêcher qu'un même billet soit utilisé plusieurs fois.

## 7.9. Sécurité des fichiers

Les fichiers déposés par les utilisateurs ou les administrateurs peuvent présenter des risques.

Mesures :
- Autoriser uniquement les extensions nécessaires.
- Vérifier le type réel du fichier.
- Vérifier la taille maximale.
- Générer des noms de fichiers internes.
- Ne pas utiliser directement le nom fourni par l'utilisateur comme chemin de stockage.
- Refuser les fichiers exécutables.
- Stocker les documents privés hors du répertoire public.
- Contrôler les autorisations de téléchargement.
- Prévoir une analyse antivirus si l'infrastructure le permet.
- Éviter de servir directement les fichiers uploadés comme du contenu exécutable.

Les documents publics et privés devront suivre des règles d'accès distinctes.

## 7.10. Sécurité des données personnelles

Les informations concernées comprennent notamment :
- Nom et prénom.
- Matricule.
- Adresse e-mail.
- Téléphone.
- Photo.
- Historique des adhésions.
- Historique des paiements.

Mesures :
- Collecter uniquement les informations nécessaires.
- Restreindre les accès.
- Ne pas exposer les profils publiquement.
- Chiffrer les communications avec HTTPS.
- Limiter les exports de données.
- Contrôler les téléchargements.
- Définir une durée de conservation.
- Prévoir une procédure de rectification des informations.
- Prévoir une procédure de traitement des demandes de suppression lorsque juridiquement possible.

Le projet devra être examiné au regard de la réglementation malgache applicable à la protection des données personnelles, notamment la loi n° 2014-038, et des éventuelles formalités ou obligations auprès des autorités compétentes.

## 7.11. Protection contre les attaques par force brute

- Limiter les tentatives de connexion.
- Ajouter un délai progressif après plusieurs échecs.
- Journaliser les tentatives suspectes.
- Prévoir un mécanisme anti-automatisation adapté.
- Protéger les formulaires sensibles.
- Surveiller les comportements anormaux.

## 7.12. Sécurité de l'administration

Les comptes administratifs devront bénéficier de protections renforcées :

- Authentification multifacteur (MFA) recommandée.
- Comptes individuels, jamais de compte administrateur partagé.
- Permissions limitées.
- Réauthentification pour certaines opérations critiques.
- Journalisation des modifications.
- Expiration des sessions administratives.
- Protection contre les connexions suspectes.

Opérations sensibles :
- Modification des montants.
- Validation manuelle d'un paiement.
- Révocation d'un quitus.
- Modification des rôles.
- Publication d'un rapport financier.
- Suppression ou archivage de données importantes.

## 7.13. Protection contre les erreurs de configuration

En production :
- `DEBUG = False`.
- `SECRET_KEY` conservée hors du dépôt Git.
- `ALLOWED_HOSTS` configuré précisément.
- HTTPS obligatoire.
- Redirection HTTP vers HTTPS.
- Configuration sécurisée des cookies.
- En-têtes de sécurité adaptés.
- Désactivation des pages d'erreur détaillées.
- Permissions système minimales.
- Base de données non exposée publiquement.

Utiliser les vérifications de déploiement de Django avant la mise en production.

## 7.14. Journalisation et audit

Un journal d'audit devra conserver les opérations sensibles.

Informations :
- Utilisateur responsable.
- Action effectuée.
- Date et heure.
- Ressource concernée.
- Ancienne valeur et nouvelle valeur lorsque nécessaire.
- Résultat de l'opération.
- Adresse IP lorsque cela est justifié et conforme aux règles de protection des données.

Actions à tracer :
- Connexion administrative.
- Modification d'un rôle.
- Validation d'un paiement.
- Révocation d'un quitus.
- Création ou modification d'une cotisation.
- Modification d'une opération financière.
- Publication d'un rapport.
- Suppression ou archivage d'un contenu.

Les journaux ne devront pas contenir de mots de passe, de secrets API ou de données de paiement sensibles.

Ils devront être protégés contre la modification non autorisée.

## 7.15. Sauvegarde et restauration

### Sauvegardes

Prévoir :
- Sauvegarde quotidienne de la base de données.
- Sauvegarde des fichiers importants.
- Sauvegardes chiffrées.
- Stockage séparé de la production.
- Conservation selon une politique définie.

### Politique initiale proposée

- Sauvegardes quotidiennes conservées pendant 30 jours.
- Sauvegarde hebdomadaire conservée pendant 3 mois.
- Sauvegarde mensuelle conservée pendant 12 mois, sous réserve des règles de conservation applicables.

### Restauration

Une procédure documentée devra permettre :
- De restaurer la base de données.
- De restaurer les documents.
- De vérifier l'intégrité des données.
- De remettre l'application en fonctionnement.

Les restaurations devront être testées régulièrement. Une sauvegarde qui n'a jamais été restaurée n'est pas une garantie suffisante.

## 7.16. Sécurité de l'infrastructure

- Serveur Linux maintenu à jour.
- Pare-feu configuré.
- SSH sécurisé.
- Accès serveur limité.
- Services inutiles désactivés.
- Base de données accessible uniquement depuis les services autorisés.
- Certificat TLS valide.
- Surveillance des ressources.
- Journalisation serveur.
- Mises à jour régulières des dépendances.
- Séparation des environnements de développement, test et production.

## 7.17. Référentiel de sécurité

Le développement devra s'appuyer notamment sur :
- OWASP Top 10.
- OWASP Application Security Verification Standard (ASVS).
- Recommandations de sécurité officielles de Django.
- Bonnes pratiques PostgreSQL.
- Documentation de sécurité des prestataires Mobile Money.

Une revue de sécurité devra être réalisée avant la mise en production.

---

# 8. ARCHITECTURE TECHNIQUE

## 8.1. Architecture générale

L'application adoptera une architecture web basée sur Django.

Le navigateur communiquera avec le serveur Django en HTTP sécurisé.

Django sera responsable :
- De l'authentification.
- Des règles métier.
- Des permissions.
- Des opérations financières.
- De l'accès à la base de données.
- De la génération des documents.
- De la gestion des notifications.

JavaScript sera principalement utilisé pour les interactions dynamiques côté navigateur.

## 8.2. Technologies retenues

| Technologie | Utilisation |
|---|---|
| Python | Langage backend |
| Django | Framework backend |
| PostgreSQL | Base de données |
| HTML5 | Structure |
| CSS3 | Présentation |
| JavaScript | Interactions |
| Bootstrap ou Tailwind CSS | Framework CSS |
| Django ORM | Accès aux données |
| ReportLab | Génération PDF |
| Bibliothèque QR Python | Génération QR Codes |
| Git | Gestion de versions |
| Gunicorn | Serveur d'application |
| Nginx | Reverse proxy et fichiers statiques |
| HTTPS/TLS | Chiffrement des communications |

Le choix final du framework CSS et des bibliothèques sera arrêté au début du développement.

## 8.3. Organisation des applications Django

```text
aesm/
│
├── manage.py
│
├── config/
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/
│   ├── memberships/
│   ├── payments/
│   ├── certificates/
│   ├── publications/
│   ├── documents/
│   ├── events/
│   ├── finance/
│   ├── notifications/
│   ├── support/
│   └── audit/
│
├── templates/
│
├── static/
│
├── media/
│
└── tests/
```

Chaque application devra posséder une responsabilité claire.

## 8.4. Architecture de la base de données

Les principales entités seront :

| Entité | Description |
|---|---|
| User | Compte utilisateur |
| MemberProfile | Profil du membre |
| Role | Rôle utilisateur |
| Membership | Adhésion |
| ContributionType | Type de cotisation |
| ContributionDue | Cotisation exigible pour un membre |
| Payment | Transaction |
| PaymentAttempt | Tentative de paiement |
| PaymentProviderEvent | Notification reçue du prestataire |
| Receipt | Reçu |
| Quitus | Attestation de paiement |
| MemberCard | Carte numérique |
| Document | Document pédagogique |
| DocumentCategory | Catégorie de document |
| Publication | Publication |
| PublicationCategory | Catégorie de publication |
| Comment | Commentaire |
| Like | Réaction |
| Event | Événement |
| Reservation | Réservation |
| Ticket | Billet |
| Attendance | Présence |
| BudgetEntry | Opération financière |
| FinancialReport | Rapport financier |
| Notification | Notification |
| SupportTicket | Réclamation |
| AuditLog | Journal d'audit |

### Relations principales

- Un utilisateur possède un profil.
- Un utilisateur peut avoir plusieurs adhésions dans le temps.
- Une adhésion peut être liée à plusieurs cotisations exigibles.
- Une cotisation peut générer plusieurs obligations de paiement pour différents membres.
- Une transaction est associée à un membre et à une obligation ou réservation.
- Une transaction confirmée peut générer un reçu.
- Une ou plusieurs transactions peuvent contribuer à satisfaire une obligation selon les règles définies.
- Un membre peut posséder plusieurs quitus.
- Une publication possède plusieurs commentaires et réactions.
- Un événement possède plusieurs réservations.
- Une réservation confirmée peut générer un billet.
- Une opération financière appartient à une catégorie.
- Une notification appartient à un utilisateur.

Les contraintes d'intégrité devront être définies dans la base de données lorsque cela est possible.

---

# 9. INTERFACES À DÉVELOPPER

## 9.1. Interfaces publiques

- Accueil.
- À propos.
- Bureau de l'association.
- Actualités.
- Détail d'une publication.
- Événements.
- Détail d'un événement.
- Documents publics.
- Contact.
- Inscription.
- Connexion.
- Vérification QR Code.

## 9.2. Interfaces membres

- Tableau de bord.
- Profil.
- Adhésions.
- Cotisations.
- Paiements.
- Historique des transactions.
- Reçus.
- Quitus.
- Carte numérique.
- Publications.
- Documents.
- Réservations.
- Billets.
- Rapports financiers.
- Notifications.
- Réclamations.
- Paramètres.

## 9.3. Interfaces administratives

- Connexion administrative.
- Tableau de bord général.
- Gestion des utilisateurs.
- Gestion des adhésions.
- Gestion des cotisations.
- Gestion des paiements.
- Gestion des quitus.
- Gestion des cartes.
- Gestion des publications.
- Modération.
- Gestion des documents.
- Gestion des événements.
- Gestion des réservations.
- Gestion des finances.
- Gestion des rapports.
- Gestion des notifications.
- Gestion des réclamations.
- Gestion des rôles.
- Journal d'audit.
- Paramètres.

---

# 10. EXIGENCES DE TEST ET DE VALIDATION

Les tests seront effectués avant la mise en production.

## 10.1. Tests unitaires

Tester individuellement :
- Les fonctions de calcul.
- Les validations de formulaires.
- Les transitions de statuts.
- Les permissions.
- Les opérations financières.
- La génération des références.
- Les règles de réservation.

## 10.2. Tests d'intégration

Tester les interactions entre :
- Comptes et adhésions.
- Cotisations et paiements.
- Paiements et quitus.
- Événements et réservations.
- Réservations et billets QR.
- Documents et permissions.
- Finances et rapports.

## 10.3. Tests de sécurité

Tester notamment :
- Connexion avec mot de passe incorrect.
- Tentatives de force brute.
- Accès non autorisé aux pages administratives.
- Accès aux ressources d'autres membres.
- Injections SQL.
- XSS.
- CSRF.
- Upload de fichiers interdits.
- Téléchargement de documents privés.
- Falsification des montants.
- Réutilisation de notifications de paiement.
- Double validation d'une transaction.
- Utilisation multiple d'un billet.
- Accès aux QR Codes révoqués.

## 10.4. Tests de performance

- Chargement des pages.
- Recherche documentaire.
- Consultation des publications.
- Affichage des statistiques.
- Gestion des réservations simultanées.
- Traitement des paiements.
- Génération des PDF.

## 10.5. Tests d'acceptation

Les responsables AESM devront vérifier les parcours réels.

### Scénario 1 : Adhésion

Un étudiant crée son compte, soumet une demande, reçoit une validation et règle sa cotisation.

Résultat attendu : son statut est correctement mis à jour.

### Scénario 2 : Paiement

Un membre effectue un paiement.

Résultat attendu : la transaction est vérifiée et un reçu est généré.

### Scénario 3 : Quitus

Un membre consulte son quitus et le présente à un responsable.

Résultat attendu : le QR Code confirme l'authenticité et le statut du document.

### Scénario 4 : Document privé

Un visiteur essaie d'accéder à un document réservé aux membres.

Résultat attendu : accès refusé.

### Scénario 5 : Réservation

Un membre réserve une place pour un événement payant.

Résultat attendu : la réservation devient confirmée après paiement.

### Scénario 6 : Transparence financière

Un membre consulte le rapport financier.

Résultat attendu : les montants affichés correspondent aux écritures validées.

---

# 11. DÉPLOIEMENT ET MAINTENANCE

## 11.1. Environnements

Trois environnements sont recommandés :

**Développement**
- Travail local.
- SQLite éventuellement au démarrage.
- Tests et développement.

**Préproduction**
- Configuration proche de la production.
- PostgreSQL.
- Tests d'intégration.
- Validation par les responsables.

**Production**
- Serveur sécurisé.
- PostgreSQL.
- HTTPS.
- Sauvegardes.
- Surveillance.
- Accès contrôlés.

## 11.2. Déploiement

Architecture envisagée :

```text
Utilisateur
    |
    v
HTTPS
    |
    v
Nginx
    |
    v
Gunicorn
    |
    v
Django
    |
    +------ PostgreSQL
    |
    +------ Stockage fichiers
    |
    +------ Prestataires Mobile Money
```

## 11.3. Maintenance corrective

- Correction des bugs.
- Résolution des problèmes de connexion.
- Correction des erreurs de paiement.
- Correction des problèmes d'affichage.
- Restauration des données si nécessaire.

## 11.4. Maintenance évolutive

- Ajout de nouvelles fonctionnalités.
- Ajout de nouveaux moyens de paiement.
- Amélioration de l'interface.
- Ajout de nouveaux types de documents.
- Amélioration des statistiques.

## 11.5. Maintenance préventive

- Mise à jour de Django.
- Mise à jour des dépendances.
- Vérification des journaux.
- Vérification des sauvegardes.
- Tests de restauration.
- Contrôle des permissions.
- Surveillance de l'espace disque.
- Vérification des certificats HTTPS.

---

# 12. LIVRABLES ATTENDUS

À la fin du projet, les livrables devront comprendre :

| Livrable | Description |
|---|---|
| Cahier des charges | Document de référence |
| Maquettes UI/UX | Interfaces principales |
| Diagramme de cas d'utilisation | Acteurs et fonctionnalités |
| Diagramme de classes | Modélisation des entités |
| MCD/MLD | Modélisation de la base |
| Code source | Projet Django complet |
| Base de données | Schéma et migrations |
| Documentation technique | Installation et architecture |
| Documentation utilisateur | Guide membre |
| Documentation administrative | Guide responsables |
| Plan de tests | Tests et résultats |
| Rapport de sécurité | Contrôles réalisés |
| Application déployée | Version en production |
| Procédure de sauvegarde | Sauvegarde et restauration |

Le code source devra être versionné avec Git et documenté.

---

# 13. PLANNING PRÉVISIONNEL

Le planning suivant constitue une estimation pour une réalisation progressive. Il devra être ajusté selon les ressources humaines, les validations de l'association et les accès aux services de paiement.

| Phase | Travaux | Durée estimée |
|---|---|---|
| 1 | Analyse et validation des besoins | 1 semaine |
| 2 | Conception UI/UX et base de données | 1 à 2 semaines |
| 3 | Authentification et membres | 1 à 2 semaines |
| 4 | Adhésions et cotisations | 1 semaine |
| 5 | Paiements et quitus | 2 à 3 semaines |
| 6 | Publications et documents | 1 à 2 semaines |
| 7 | Événements et réservations | 1 à 2 semaines |
| 8 | Gestion financière | 1 à 2 semaines |
| 9 | Sécurité et tests | 2 semaines |
| 10 | Déploiement et formation | 1 semaine |

**Estimation globale : 12 à 18 semaines**, pour une première réalisation avec un périmètre maîtrisé. Les délais dépendent notamment de l'intégration des prestataires Mobile Money et de la disponibilité des responsables AESM.

---

# 14. CRITÈRES DE RÉUSSITE DU PROJET

Le projet sera considéré comme fonctionnellement réussi lorsque :

1. Un étudiant peut créer un compte.
2. Une demande d'adhésion peut être validée par un responsable.
3. L'administration peut configurer les cotisations.
4. Un membre peut régler une cotisation.
5. Le paiement peut être vérifié de manière fiable.
6. Le membre peut consulter son historique.
7. Un reçu et un quitus peuvent être générés.
8. Le QR Code permet une vérification fiable.
9. Les publications sont accessibles selon leur visibilité.
10. Les membres peuvent interagir avec les publications.
11. Les documents privés sont protégés.
12. Les événements peuvent être créés et réservés.
13. Les capacités des événements sont respectées.
14. Les paiements et réservations sont correctement associés.
15. Les rapports financiers sont consultables par les personnes autorisées.
16. Les opérations administratives sensibles sont traçables.
17. Les données personnelles sont protégées.
18. Les sauvegardes et restaurations ont été testées.

---

# 15. RISQUES ET CONTRAINTES DU PROJET

| Risque | Conséquence | Mesure préventive |
|---|---|---|
| Absence d'accès API Mobile Money | Paiements automatiques impossibles | Prévoir un mode manuel temporaire |
| Erreurs de validation des paiements | Mauvaise situation financière | Vérification serveur |
| Perte de données | Interruption des activités | Sauvegardes régulières |
| Accès non autorisé | Fuite de données | RBAC et tests de sécurité |
| Faible adoption par les membres | Utilisation limitée | Interface simple et formation |
| Erreurs de réservation | Dépassement des capacités | Transactions atomiques |
| Mauvaise gestion financière | Rapports inexacts | Historique et validation |
| Documents malveillants | Compromission du serveur ou des utilisateurs | Contrôle et analyse des fichiers |
| Mauvaise définition des règles d'adhésion | Fonctionnalités inadaptées | Validation préalable avec AESM |
| Dépendance à un prestataire de paiement | Interruption des paiements | Architecture extensible |

---

# 16. POINTS À VALIDER AVEC LES RESPONSABLES DE L'AESM

Les informations suivantes ne sont pas encore suffisamment définies pour être considérées comme des règles métier définitives.

| N° | Question | Décision attendue |
|---|---|---|
| 1 | Quel est le montant officiel de l'adhésion ? | Montant |
| 2 | Quelle est la durée de validité de l'adhésion ? | Annuelle, semestrielle ou autre |
| 3 | Quels étudiants peuvent devenir membres ? | Conditions d'éligibilité |
| 4 | L'e-mail est-il obligatoire ? | Oui / Non |
| 5 | La photo d'identité est-elle obligatoire ? | Oui / Non |
| 6 | Qui valide les inscriptions ? | Responsable |
| 7 | Quels comptes Mobile Money possède l'AESM ? | Prestataires et statut marchand |
| 8 | L'association dispose-t-elle d'accès API ? | Disponibilité technique |
| 9 | Quels sont les différents types de cotisations ? | Liste officielle |
| 10 | Qui peut délivrer un quitus ? | Responsable |
| 11 | Les visiteurs peuvent-ils participer aux événements ? | Règles d'accès |
| 12 | Les remboursements sont-ils autorisés ? | Politique |
| 13 | Qui valide les rapports financiers ? | Circuit de validation |
| 14 | Quels documents sont réservés aux membres ? | Classification |
| 15 | Qui peut accéder aux données des membres ? | Permissions |
| 16 | Combien de responsables administreront la plateforme ? | Nombre et rôles |
| 17 | Quel est le volume estimé de membres ? | Dimensionnement |
| 18 | Qui sera propriétaire du domaine et de l'hébergement ? | Responsabilité |
| 19 | Quelle sera la politique de conservation des données ? | Durées et obligations |
| 20 | Qui assurera la maintenance après le lancement ? | Responsable technique |

---

# 17. CONCLUSION

Le projet AESM vise à mettre en place une plateforme numérique centralisée permettant de moderniser le fonctionnement de l'association.

La solution devra faciliter les adhésions, les paiements, la gestion des membres, la communication, la distribution des documents pédagogiques, l'organisation des événements et le suivi financier.

La sécurité, la fiabilité des transactions et la protection des données personnelles constituent des exigences fondamentales de la plateforme.

La réalisation devra être progressive, en commençant par les fonctionnalités essentielles liées à l'adhésion et au paiement, avant d'intégrer les autres modules.

L'objectif final est de fournir à l'AESM un outil durable, évolutif, sécurisé et adapté à ses besoins réels.

---

# ANNEXE A — PRINCIPES DE CONCEPTION À RESPECTER

1. Toutes les règles métier importantes doivent être exécutées côté serveur.
2. Aucun montant financier ne doit être considéré comme fiable lorsqu'il provient uniquement du navigateur.
3. Toutes les ressources privées doivent être protégées par des contrôles d'autorisation.
4. Les opérations financières doivent être traçables.
5. Les changements de statuts doivent respecter des transitions définies.
6. Les QR Codes doivent être vérifiables et révocables.
7. Les données historiques ne doivent pas être modifiées silencieusement.
8. Les sauvegardes doivent être testées.
9. Les fonctionnalités sensibles doivent faire l'objet de tests spécifiques.
10. La plateforme doit être conçue pour évoluer sans réécriture complète.

# ANNEXE B — RÉFÉRENCES TECHNIQUES

Documentation à consulter pendant le développement :

- Django : https://docs.djangoproject.com/
- Django Security : https://docs.djangoproject.com/en/stable/topics/security/
- PostgreSQL : https://www.postgresql.org/docs/
- OWASP Top 10 : https://owasp.org/www-project-top-ten/
- OWASP ASVS : https://owasp.org/www-project-application-security-verification-standard/
- MDN Web Docs : https://developer.mozilla.org/
- Python : https://docs.python.org/3/

**Fin du cahier des charges — AESM**