import io

from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.core.utils import format_ariary


def _safe(v):
    v = str(v)
    return "'" + v if v[:1] in "=+-@" else v


def report_xlsx(report):
    s = report.snapshot
    wb = Workbook()
    ws = wb.active
    ws.title = "Synthèse"
    ws.append([f"{report.title} (version {report.version})"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Période", f"{report.period_start} au {report.period_end}"])
    for label, key in (("Solde initial", "opening"), ("Total des recettes", "income"), ("Total des dépenses", "expense"), ("Solde final", "closing")):
        ws.append([label, s[key]])
    ws.append([])
    ws.append(["Recettes par catégorie"])
    for k, v in s["income_by_category"]:
        ws.append([k, v])
    ws.append([])
    ws.append(["Dépenses par catégorie"])
    for k, v in s["expense_by_category"]:
        ws.append([k, v])
    ws.column_dimensions["A"].width = 38
    d = wb.create_sheet("Opérations")
    d.append(["Référence", "Date", "Type", "Catégorie", "Description", "Montant (Ar)"])
    for c in d[1]:
        c.font = Font(bold=True)
    for e in s["entries"]:
        d.append([e["reference"], e["date"], e["kind"], e["category"], _safe(e["description"]), e["amount"]])
    for col, w in zip("ABCDEF", (18, 12, 10, 28, 60, 14)):
        d.column_dimensions[col].width = w
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def report_pdf(report):
    s = report.snapshot
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    st = getSampleStyleSheet()
    els = [Paragraph(f"{report.title} - version {report.version}", st["Title"]),
           Paragraph(f"Période : {report.period_start:%d/%m/%Y} au {report.period_end:%d/%m/%Y}", st["Normal"]), Spacer(1, 12)]
    t = Table([["Solde initial", format_ariary(s["opening"])], ["Total des recettes", format_ariary(s["income"])],
               ["Total des dépenses", format_ariary(s["expense"])], ["Solde final", format_ariary(s["closing"])]], colWidths=[8 * cm, 6 * cm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold")]))
    els += [t, Spacer(1, 14), Paragraph("Opérations validées", st["Heading2"])]
    rows = [["Date", "Type", "Catégorie", "Description", "Montant"]]
    for e in s["entries"]:
        rows.append([e["date"], e["kind"], Paragraph(e["category"], st["BodyText"]), Paragraph(e["description"][:90].replace("&", "&amp;").replace("<", "&lt;"), st["BodyText"]), f"{e['amount']:,}".replace(",", " ")])
    tt = Table(rows, repeatRows=1, colWidths=[2.3 * cm, 1.8 * cm, 3.8 * cm, 6.3 * cm, 2.5 * cm])
    tt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f5a46")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey), ("FONTSIZE", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    els.append(tt)
    doc.build(els)
    buf.seek(0)
    return buf


def entries_xlsx(entries):
    wb = Workbook()
    ws = wb.active
    ws.title = "Opérations"
    ws.append(["Référence", "Date", "Type", "Catégorie", "Description", "Montant (Ar)", "Statut"])
    for e in entries:
        ws.append([e.reference, e.date.isoformat(), e.get_kind_display(), e.get_category_display(), _safe(e.description), int(e.amount), e.get_status_display()])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
