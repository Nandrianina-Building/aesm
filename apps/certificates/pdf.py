"""Génération des PDF (ReportLab) : reçu, quitus, carte de membre, billet."""
import io

import qrcode
from django.conf import settings
from django.urls import reverse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from apps.core.utils import format_ariary, get_setting

PRIMARY = colors.HexColor("#1f5a46")
ACCENT = colors.HexColor("#b8432f")


def verification_url(token):
    return settings.SITE_URL + reverse("verify:check", args=[token])


def qr_image(token):
    img = qrcode.make(verification_url(token), box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _header(c, title, width, height):
    c.setFillColor(PRIMARY)
    c.rect(0, height - 3.2 * cm, width, 3.2 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(2 * cm, height - 1.7 * cm, get_setting("association_short", "AESM"))
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, height - 2.4 * cm, get_setting("association_name", ""))
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 2 * cm, height - 1.9 * cm, title)
    c.setFillColor(colors.black)


def _lines(c, rows, x, y, gap=0.9 * cm):
    for label, value in rows:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.grey)
        c.drawString(x, y, label)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 5.5 * cm, y, str(value))
        y -= gap
    return y


def _finish(c, buf):
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def receipt_pdf(receipt):
    p = receipt.payment
    buf = io.BytesIO()
    w, h = A4
    c = canvas.Canvas(buf, pagesize=A4)
    _header(c, "REÇU DE PAIEMENT", w, h)
    y = _lines(c, [
        ("Numéro du reçu", receipt.number), ("Membre", receipt.user.full_name), ("Matricule", receipt.user.matricule),
        ("Objet", p.object_label), ("Montant", format_ariary(p.amount)), ("Moyen de paiement", p.get_method_display()),
        ("Référence de transaction", p.external_reference or p.reference),
        ("Date de confirmation", p.confirmed_at.strftime("%d/%m/%Y %H:%M") if p.confirmed_at else "-"),
    ], 2 * cm, h - 5 * cm)
    if receipt.is_void:
        c.setFillColor(colors.red)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(2 * cm, y - 1 * cm, "ANNULÉ (REMBOURSÉ)")
    c.setFillColor(colors.grey)
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 1.5 * cm, f"{get_setting('association_name', '')} - {get_setting('contact_email', '')}")
    return _finish(c, buf)


def quitus_pdf(q):
    buf = io.BytesIO()
    w, h = A4
    c = canvas.Canvas(buf, pagesize=A4)
    _header(c, "QUITUS NUMÉRIQUE", w, h)
    y = _lines(c, [
        ("Numéro du quitus", q.number), ("Nom et prénom", q.user.full_name), ("Matricule", q.user.matricule),
        ("Cotisation concernée", q.contribution_name), ("Période concernée", q.period_label or "-"),
        ("Montant validé", format_ariary(q.amount)), ("Date de délivrance", q.issued_at.strftime("%d/%m/%Y")),
        ("Date de validité", q.valid_until.strftime("%d/%m/%Y") if q.valid_until else "Sans limite"),
        ("Statut au moment de l'édition", q.status_label),
    ], 2 * cm, h - 5 * cm)
    c.drawImage(qr_image(q.token), 2 * cm, y - 5 * cm, 4 * cm, 4 * cm)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawString(6.5 * cm, y - 2.5 * cm, "Scannez le QR code pour vérifier l'authenticité et le statut actuel.")
    c.drawString(6.5 * cm, y - 3.1 * cm, "Seule la vérification en ligne fait foi (un PDF peut être révoqué).")
    return _finish(c, buf)


def card_pdf(card):
    u = card.user
    buf = io.BytesIO()
    cw, ch = 85.6 * mm, 54 * mm
    c = canvas.Canvas(buf, pagesize=(cw, ch))
    c.setFillColor(PRIMARY)
    c.rect(0, ch - 12 * mm, cw, 12 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(4 * mm, ch - 8 * mm, get_setting("association_short", "AESM"))
    c.setFont("Helvetica", 7)
    c.drawRightString(cw - 4 * mm, ch - 8 * mm, "CARTE DE MEMBRE")
    c.setFillColor(colors.black)
    if u.photo:
        try:
            c.drawImage(ImageReader(u.photo.path), 4 * mm, 8 * mm, 22 * mm, 28 * mm, preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
    else:
        c.setStrokeColor(colors.grey)
        c.rect(4 * mm, 8 * mm, 22 * mm, 28 * mm)
    profile = getattr(u, "profile", None)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(29 * mm, ch - 19 * mm, u.full_name[:26])
    c.setFont("Helvetica", 7.5)
    c.drawString(29 * mm, ch - 24 * mm, f"Matricule : {u.matricule}")
    c.drawString(29 * mm, ch - 28 * mm, f"N° membre : {profile.member_number if profile else '-'}")
    c.drawString(29 * mm, ch - 32 * mm, f"Adhésion : {profile.joined_year if profile else '-'}")
    c.drawString(29 * mm, ch - 36 * mm, f"Statut : {card.status_label}")
    c.drawImage(qr_image(card.token), cw - 19 * mm, 3 * mm, 16 * mm, 16 * mm)
    return _finish(c, buf)


def ticket_pdf(ticket):
    r = ticket.reservation
    e = r.event
    buf = io.BytesIO()
    w, h = A4
    c = canvas.Canvas(buf, pagesize=A4)
    _header(c, "BILLET D'ENTRÉE", w, h)
    y = _lines(c, [
        ("Événement", e.title), ("Date", e.starts_at.astimezone().strftime("%d/%m/%Y %H:%M")), ("Lieu", e.location),
        ("Participant", r.user.full_name), ("N° de billet", ticket.number), ("Prix payé", format_ariary(r.price_snapshot)),
    ], 2 * cm, h - 5 * cm)
    c.drawImage(qr_image(ticket.token), 2 * cm, y - 5 * cm, 4 * cm, 4 * cm)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.grey)
    c.drawString(6.5 * cm, y - 2.5 * cm, "Présentez ce QR code à l'entrée. Il ne peut être utilisé qu'une seule fois.")
    return _finish(c, buf)
