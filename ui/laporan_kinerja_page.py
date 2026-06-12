from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox
)

from database.db_manager import get_connection
from utils.data_exporter import DataExporter


class LaporanKinerjaPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.load_statistik()

    def setup_ui(self):

        layout = QVBoxLayout()

        self.lbl_total_proyek = QLabel()
        self.lbl_total_tugas = QLabel()
        self.lbl_tugas_selesai = QLabel()

        self.btn_export_csv = QPushButton(
            "Export CSV"
        )

        self.btn_export_pdf = QPushButton(
            "Export PDF"
        )

        layout.addWidget(
            self.lbl_total_proyek
        )

        layout.addWidget(
            self.lbl_total_tugas
        )

        layout.addWidget(
            self.lbl_tugas_selesai
        )

        layout.addWidget(
            self.btn_export_csv
        )

        layout.addWidget(
            self.btn_export_pdf
        )

        layout.addStretch()

        self.setLayout(
            layout
        )

        self.btn_export_csv.clicked.connect(
            self.export_csv
        )

        self.btn_export_pdf.clicked.connect(
            self.export_pdf
        )

    def load_statistik(self):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM proyek"
        )

        total_proyek = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM tugas"
        )

        total_tugas = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM tugas
            WHERE status = 'Selesai'
            """
        )

        tugas_selesai = cursor.fetchone()[0]

        self.lbl_total_proyek.setText(
            f"Total Proyek : {total_proyek}"
        )

        self.lbl_total_tugas.setText(
            f"Total Tugas : {total_tugas}"
        )

        self.lbl_tugas_selesai.setText(
            f"Tugas Selesai : {tugas_selesai}"
        )

        conn.close()

    def export_csv(self):

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "",
            "CSV (*.csv)"
        )

        if file_path:

            DataExporter.export_csv(
                file_path
            )

            QMessageBox.information(
                self,
                "Berhasil",
                "CSV berhasil dibuat"
            )

    def export_pdf(self):

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            "",
            "PDF (*.pdf)"
        )

        if file_path:

            DataExporter.export_pdf(
                file_path
            )

            QMessageBox.information(
                self,
                "Berhasil",
                "PDF berhasil dibuat"
            )