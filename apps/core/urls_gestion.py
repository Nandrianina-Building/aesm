from django.urls import path

from apps.accounts import admin_views as users
from apps.certificates import views as certs
from apps.documents import admin_views as docs
from apps.events import admin_views as events
from apps.finance import views as fin
from apps.memberships import admin_views as memberships
from apps.notifications import views as notifs
from apps.payments import admin_views as pay
from apps.publications import admin_views as pubs
from apps.support import admin_views as support

from . import views_gestion as core

app_name = "gestion"
urlpatterns = [
    path("", core.home, name="home"),
    # utilisateurs / adhésions
    path("utilisateurs/", users.user_list, name="users"),
    path("utilisateurs/<int:pk>/", users.user_edit, name="user_edit"),
    path("adhesions/", memberships.membership_list, name="memberships"),
    path("adhesions/<int:pk>/accepter/", memberships.membership_accept, name="membership_accept"),
    path("adhesions/<int:pk>/refuser/", memberships.membership_refuse, name="membership_refuse"),
    path("adhesions/<int:pk>/verifier/", memberships.membership_verify, name="membership_verify"),
    path("adhesions/<int:pk>/suspendre/", memberships.membership_suspend, name="membership_suspend"),
    path("adhesions/<int:pk>/reactiver/", memberships.membership_reactivate, name="membership_reactivate"),
    # cotisations / paiements
    path("cotisations/", pay.contribution_list, name="contributions"),
    path("cotisations/nouvelle/", pay.contribution_edit, name="contribution_create"),
    path("cotisations/<int:pk>/modifier/", pay.contribution_edit, name="contribution_edit"),
    path("cotisations/<int:pk>/facturer/", pay.contribution_generate, name="contribution_generate"),
    path("cotisations/membres/", pay.due_list, name="dues"),
    path("cotisations/membres/<int:pk>/exonerer/", pay.due_waive, name="due_waive"),
    path("paiements/", pay.payment_list, name="payments"),
    path("paiements/<str:reference>/", pay.payment_detail, name="payment_detail"),
    path("paiements/<str:reference>/confirmer/", pay.payment_confirm, name="payment_confirm"),
    path("paiements/<str:reference>/rejeter/", pay.payment_reject, name="payment_reject"),
    path("paiements/<str:reference>/rembourser/", pay.payment_refund, name="payment_refund"),
    # quitus / cartes
    path("quitus/", certs.quitus_admin_list, name="quitus"),
    path("quitus/<int:pk>/revoquer/", certs.quitus_revoke, name="quitus_revoke"),
    path("cartes/", certs.cards_admin_list, name="cards"),
    path("cartes/<int:pk>/basculer/", certs.card_toggle, name="card_toggle"),
    # publications / documents
    path("publications/", pubs.publication_list, name="publications"),
    path("publications/nouvelle/", pubs.publication_edit, name="publication_create"),
    path("publications/<int:pk>/modifier/", pubs.publication_edit, name="publication_edit"),
    path("publications/<int:pk>/archiver/", pubs.publication_archive, name="publication_archive"),
    path("publications/categories/", pubs.category_list, name="categories"),
    path("publications/categories/nouvelle/", pubs.category_edit, name="category_create"),
    path("publications/categories/<int:pk>/", pubs.category_edit, name="category_edit"),
    path("commentaires/", pubs.comment_moderation, name="comments"),
    path("commentaires/<int:pk>/masquer/", pubs.comment_hide, name="comment_hide"),
    path("commentaires/<int:pk>/supprimer/", pubs.comment_remove, name="comment_remove"),
    path("documents/", docs.document_list, name="documents"),
    path("documents/nouveau/", docs.document_edit, name="document_create"),
    path("documents/<int:pk>/modifier/", docs.document_edit, name="document_edit"),
    path("documents/<int:pk>/archiver/", docs.document_archive, name="document_archive"),
    # événements
    path("evenements/", events.event_list, name="events"),
    path("evenements/nouveau/", events.event_edit, name="event_create"),
    path("evenements/scanner/", events.scan, name="scan"),
    path("evenements/billet/<str:token>/valider/", events.scan_ticket, name="scan_ticket"),
    path("evenements/<int:pk>/modifier/", events.event_edit, name="event_edit"),
    path("evenements/<int:pk>/reservations/", events.event_reservations, name="event_reservations"),
    path("evenements/<int:pk>/export/", events.event_export, name="event_export"),
    path("reservations/<int:pk>/annuler/", events.reservation_cancel, name="reservation_cancel"),
    # finances
    path("finances/", fin.finance_home, name="finance"),
    path("finances/operations/", fin.entry_list, name="entries"),
    path("finances/operations/nouvelle/", fin.entry_create, name="entry_create"),
    path("finances/operations/<int:pk>/valider/", fin.entry_validate, name="entry_validate"),
    path("finances/operations/<int:pk>/rejeter/", fin.entry_reject, name="entry_reject"),
    path("finances/operations/<int:pk>/annuler/", fin.entry_reverse, name="entry_reverse"),
    path("finances/rapports/", fin.report_admin_list, name="reports"),
    path("finances/rapports/nouveau/", fin.report_create, name="report_create"),
    path("finances/rapports/<int:pk>/actualiser/", fin.report_refresh, name="report_refresh"),
    path("finances/rapports/<int:pk>/valider/", fin.report_validate, name="report_validate"),
    path("finances/rapports/<int:pk>/publier/", fin.report_publish, name="report_publish"),
    # notifications / réclamations / divers
    path("notifications/annonce/", notifs.broadcast, name="broadcast"),
    path("reclamations/", support.ticket_list, name="support"),
    path("reclamations/<int:pk>/", support.ticket_detail, name="support_detail"),
    path("responsables/", core.officer_list, name="officers"),
    path("responsables/nouveau/", core.officer_edit, name="officer_create"),
    path("responsables/<int:pk>/", core.officer_edit, name="officer_edit"),
    path("journal/", core.audit_list, name="audit"),
    path("parametres/", core.settings_list, name="settings"),
    path("parametres/<int:pk>/", core.setting_edit, name="setting_edit"),
    path("contacts/", core.contact_list, name="contacts"),
    path("contacts/<int:pk>/traite/", core.contact_handled, name="contact_handled"),
]
