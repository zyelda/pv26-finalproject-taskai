import os
import pandas as pd
from database.db_manager import get_connection
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

_LOGO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "icons", "taskai.png",
)

_QUERY = """
SELECT
    p.nama_proyek  AS "Nama Proyek",
    t.nama_tugas   AS "Nama Tugas",
    t.prioritas    AS "Prioritas",
    t.status       AS "Status",
    t.deskripsi    AS "Deskripsi"
FROM tugas t
JOIN proyek p ON p.id = t.proyek_id
ORDER BY p.nama_proyek, t.id
"""


def _draw_watermark(canvas, doc):
    if not os.path.exists(_LOGO_PATH):
        return
    canvas.saveState()
    canvas.setFillAlpha(0.07)
    page_w, page_h = doc.pagesize
    size = 350
    canvas.drawImage(
        _LOGO_PATH,
        (page_w - size) / 2, (page_h - size) / 2,
        width=size, height=size,
        mask="auto", preserveAspectRatio=True,
    )
    canvas.restoreState()


class DataExporter:

    @staticmethod
    def export_csv(file_path: str):
        """Ekspor semua data tugas+proyek ke CSV."""
        conn = get_connection()
        try:
            df = pd.read_sql_query(_QUERY, conn)
        finally:
            conn.close()

        # FIX: Tangani jika tidak ada data
        if df.empty:
            df = pd.DataFrame(columns=["Nama Proyek", "Nama Tugas", "Prioritas", "Status", "Deskripsi"])

        df.to_csv(file_path, index=False, encoding="utf-8-sig")

    @staticmethod
    def export_pdf(file_path: str):
        """Ekspor semua data tugas+proyek ke PDF ber-watermark."""
        conn = get_connection()
        try:
            df = pd.read_sql_query(_QUERY, conn)
        finally:
            conn.close()

        doc = SimpleDocTemplate(file_path, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        # Judul
        elements.append(Paragraph("Laporan Kinerja TaskAI", styles["Title"]))
        elements.append(Spacer(1, 12))

        # Info ringkasan
        total_tugas = len(df)
        done_count  = len(df[df["Status"] == "Done"]) if not df.empty else 0
        pct = f"{done_count/total_tugas*100:.0f}%" if total_tugas > 0 else "0%"
        info_style = styles["Normal"]
        elements.append(Paragraph(
            f"Total Tugas: {total_tugas}  |  Selesai (Done): {done_count}  |  Progress: {pct}",
            info_style
        ))
        elements.append(Spacer(1, 16))

        if df.empty:
            elements.append(Paragraph("Belum ada data tugas.", styles["Normal"]))
        else:
            # FIX: Hilangkan kolom deskripsi panjang agar muat di PDF
            df_display = df[["Nama Proyek", "Nama Tugas", "Prioritas", "Status"]].copy()
            table_data = [df_display.columns.tolist()] + df_display.values.tolist()

            # Lebar kolom proporsional
            col_widths = [4.5*cm, 6*cm, 3*cm, 3*cm]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#1e293b")),
                ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
                ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, 0),  10),
                ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
                ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
                ("GRID",        (0, 0), (-1, -1),  0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.HexColor("#f8fafc"), colors.HexColor("#f1f5f9")]),
                ("FONTSIZE",    (0, 1), (-1, -1),  9),
                ("TOPPADDING",  (0, 0), (-1, -1),  6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(table)

        doc.build(elements, onFirstPage=_draw_watermark, onLaterPages=_draw_watermark)
