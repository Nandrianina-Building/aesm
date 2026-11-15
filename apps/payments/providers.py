"""Abstraction des prestataires de paiement.

* ``simulation`` (actif par défaut) : aucun argent réel. Le membre est envoyé vers une page de
  paiement fictive où il choisit « réussi / échoué / annulé ». Le reste du circuit (reçu, quitus,
  écriture comptable, billet...) est exactement celui de la production.
* ``tokipay`` : squelette prêt à compléter. Tokipay (https://tokipay.app) propose des liens de
  paiement MVola / Orange Money et une API REST avec webhooks (offre Pro). Sa documentation d'API
  n'étant pas publique, seuls les points d'accroche sont fournis : voir docs/PAIEMENTS_TOKIPAY.md.

Pour changer de prestataire : variable d'environnement ``PAYMENT_PROVIDER`` (aucun autre changement
de code métier n'est nécessaire).
"""
from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse


class ProviderNotConfigured(Exception):
    pass


@dataclass
class ProviderResult:
    status: str                     # "pending" | "processing" | "failed"
    external_reference: str = ""
    redirect_url: str = ""          # page de paiement vers laquelle envoyer le membre
    message: str = ""


class BaseProvider:
    code = ""
    label = ""
    manual = False                  # True : un humain vérifie (trésorier) ; False : confirmation automatique

    def initiate(self, payment):
        raise NotImplementedError


class SimulationProvider(BaseProvider):
    code, label = "simulation", "Paiement simulé"

    def initiate(self, payment):
        if not settings.PAYMENT_SIMULATION_ENABLED:
            raise ProviderNotConfigured("La simulation de paiement est désactivée.")
        return ProviderResult(status="pending", redirect_url=reverse("payments:simulate", args=[payment.reference]),
                              message="Paiement simulé : aucune somme réelle n'est débitée.")


class TokipayProvider(BaseProvider):
    """À COMPLÉTER avec la documentation Tokipay (compte Pro requis).

    initiate() doit : 1) appeler l'API Tokipay pour créer un lien de paiement du montant
    ``payment.amount`` avec ``payment.reference`` comme référence marchande, 2) renvoyer
    ProviderResult(status="pending", external_reference=<id Tokipay>, redirect_url=<lien de paiement>).
    La confirmation arrive ensuite par le webhook ``/espace/paiements/webhook/tokipay/`` (signé), ou
    à défaut par vérification manuelle du trésorier (cas « Vous vérifiez et confirmez » de Tokipay).
    """
    code, label = "tokipay", "Tokipay (MVola / Orange Money)"

    def initiate(self, payment):
        raise ProviderNotConfigured(
            "Tokipay n'est pas encore branché : implémentez TokipayProvider.initiate() (voir docs/PAIEMENTS_TOKIPAY.md).")


PROVIDERS = {"simulation": SimulationProvider(), "tokipay": TokipayProvider()}


def get_provider(method=None):
    return PROVIDERS[method or settings.PAYMENT_PROVIDER]
