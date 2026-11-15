# Données de démonstration

Commande : `python manage.py seed_demo [--members 120] [--force]` (ignorée si les données existent déjà ; `--force` ajoute un lot).
Les données sont créées **par les vrais services métier** (adhésions, paiements simulés, billets, écritures, rapports) : numéros, reçus, quitus,
soldes et journal d'audit sont donc cohérents. Les dates sont réparties sur les mois écoulés. **Ne jamais utiliser en production.**

Mot de passe de tous les comptes : `DemoAESM-2026!x`

## Comptes
| Matricule | Rôle |
|---|---|
| ADMIN01 | Super administrateur |
| PRES01 | Président |
| TRES01 | Trésorière |
| SECR01, SECR02 | Secrétaires |
| EVEN01 | Responsable événementiel |
| SOC26-0001 … | Membres (≈74 % actifs, 4 % suspendus, 9 % en attente, 3 % en vérification, 5 % refusés, quelques comptes sans demande) |

## Volumes par défaut (120 membres)
| Domaine | Contenu |
|---|---|
| Adhésions | 136 (dont adhésions 2025 expirées), toutes les étapes : en attente, vérification, acceptée, refusée, suspendue |
| Cotisations | 5 types (adhésion, annuelle, sortie pédagogique, fonds de solidarité ciblé, cotisation 2025 clôturée) ; ≈357 échéances : payées, à payer, en retard, exonérées |
| Paiements | ≈387 : confirmés, en attente, en vérification, échoués, annulés, quelques remboursés |
| Documents officiels | ≈331 reçus, ≈120 quitus (dont 1 révoqué), 92 cartes de membre |
| Événements | 11 (passés, ouverts, complet, brouillon, annulé, payants/gratuits) ; ≈340 réservations, ≈325 billets, ≈126 présences, annulations, expirations |
| Finances | ≈418 opérations (recettes auto + saisies manuelles : validées, rejetées, en attente, annulées par écriture inverse) ; 5 rapports (publiés, validé, brouillons, 2 versions) |
| Publications | 16 (publiques / membres, épinglées, programmée, brouillon, archivée), ≈350 j'aime, ≈40 commentaires, signalements |
| Documents pédagogiques | ≈36 PDF (L1 à M2, cours, TD, examens, corrigés, administratifs), téléchargements simulés |
| Autres | 13 responsables (dont anciens mandats), 16 réclamations avec échanges, 12 messages de contact, ≈1900 notifications, ≈1000 entrées d'audit |

## Repartir de zéro
SQLite : supprimer `db.sqlite3` et le contenu de `private/`, puis `migrate`, `init_aesm`. MySQL : recréer la base (`DROP DATABASE aesm; CREATE DATABASE …`).
