import pandas as pd

from database.db_manager import get_connection

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class DataExporter:

    @staticmethod
    def export_csv(file_path):

        conn = get_connection()

        query = """
        SELECT
            p.nama_proyek,
            t.nama_tugas,
            t.prioritas,
            t.status
        FROM tugas t
        JOIN proyek p
        ON p.id = t.proyek_id
        """

        data_frame = pd.read_sql_query(
            query,
            conn
        )

        data_frame.to_csv(
            file_path,
            index=False
        )

        conn.close()

    @staticmethod
    def export_pdf(file_path):

        conn = get_connection()

        query = """
        SELECT
            p.nama_proyek,
            t.nama_tugas,
            t.prioritas,
            t.status
        FROM tugas t
        JOIN proyek p
        ON p.id = t.proyek_id
        """

        data_frame = pd.read_sql_query(
            query,
            conn
        )

        conn.close()

        document = SimpleDocTemplate(
            file_path
        )

        styles = getSampleStyleSheet()

        elements = []

        title = Paragraph(
            "Laporan Kinerja TaskAI",
            styles["Title"]
        )

        elements.append(title)
        elements.append(
            Spacer(1, 20)
        )

        table_data = [
            data_frame.columns.tolist()
        ]

        table_data.extend(
            data_frame.values.tolist()
        )

        table = Table(
            table_data
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER")
            ])
        )

        elements.append(
            table
        )

        document.build(
            elements
        )