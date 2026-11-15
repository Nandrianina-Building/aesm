# Paiements : simulation maintenant, Tokipay ensuite

## État actuel : simulation
`PAYMENT_PROVIDER=simulation` et `PAYMENT_SIMULATION_ENABLED=1` (valeurs par défaut).
1. Le membre clique « Payer » (cotisation ou événement payant) : le serveur crée la transaction avec le montant officiel.
2. Il arrive sur une **fausse page de paiement** (`/espace/paiements/<ref>/simulation/`) et choisit : réussi, échec ou annulé.
3. « Réussi » déclenche **exactement le circuit de production** : paiement confirmé, reçu, quitus, écriture comptable, billet d'événement, notifications, journal d'audit.
Aucun argent réel n'est impliqué. Un bandeau jaune « mode démonstration » s'affiche sur tout le site.
Sécurités : réservé au propriétaire du paiement, un seul résultat par transaction, désactivable par variable d'environnement.

> ⚠️ Tant que la simulation est active, **n'importe quel membre peut valider ses propres paiements** : à utiliser uniquement pour la démonstration et la recette,
> pas pour encaisser de vraies cotisations. Les reçus et quitus produits restent des documents authentiques dans la base : repartir d'une base propre au lancement réel.

## Passage à Tokipay (https://tokipay.app)
Tokipay propose, selon son site, des **liens de paiement** MVola / Orange Money, des notifications et, avec l'offre Pro, une **API REST avec webhooks**.
Sa documentation d'API n'étant pas publique, le code fournit les points d'accroche sans inventer de format : `apps/payments/providers.py` → `TokipayProvider`.

Étapes :
1. Ouvrir un compte Tokipay (offre Pro pour l'API) et obtenir la documentation, les clés d'API, le format et la méthode de signature des webhooks.
2. Implémenter `TokipayProvider.initiate(payment)` : appeler l'API pour créer un lien de paiement de `payment.amount` Ar avec `payment.reference` comme référence marchande ;
   retourner `ProviderResult(status="pending", external_reference=<id Tokipay>, redirect_url=<lien https>)`. Le membre est alors redirigé automatiquement.
3. Adapter `webhook()` dans `apps/payments/views.py` au format réel (champs, en-tête et algorithme de signature) ; le reste est déjà en place :
   signature obligatoire, secret `WEBHOOK_SECRET_TOKIPAY`, rejeu ignoré (`PaymentProviderEvent`), contrôle du montant et de la devise, confirmation idempotente.
4. Configurer l'URL du webhook côté Tokipay : `https://<votre-domaine>/espace/paiements/webhook/tokipay/`.
5. Passer `PAYMENT_PROVIDER=tokipay` et `PAYMENT_SIMULATION_ENABLED=0`, redémarrer.
6. Recette sur de petits montants réels, puis bascule.

**Plan B sans API** : si seuls les liens de paiement sont utilisés, faire retourner `ProviderResult(..., redirect_url=<lien>)` puis laisser le trésorier confirmer
(« Vous vérifiez et confirmez » chez Tokipay) depuis `/gestion/paiements/` : l'écran de vérification existe déjà (saisie du montant reçu, rejet, remboursement).
Pour activer l'alerte au trésorier et la rétention prolongée des places, mettre `manual = True` dans `TokipayProvider`.
