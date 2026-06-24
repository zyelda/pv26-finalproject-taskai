from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db_manager import get_connection
from utils.data_exporter import DataExporter
from assets import icon


class StatCard(QFrame):
    """Kartu statistik satu angka."""

    def __init__(self, emoji: str, label: str, value: str = "0", accent: str = "#3b82f6"):
        super().__init__()
        self.setObjectName("stat_card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        lbl_icon = QLabel(emoji)
        lbl_icon.setObjectName("stat_icon")
        lbl_icon.setStyleSheet(f"font-size: 22pt; background: transparent; color: {accent};")
        layout.addWidget(lbl_icon)

        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("stat_number")
        self.lbl_value.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.lbl_value.setStyleSheet(
            f"font-size: 28pt; font-weight: bold; color: {accent}; background: transparent;"
        )
        layout.addWidget(self.lbl_value)

        lbl_desc = QLabel(label)
        lbl_desc.setObjectName("stat_label")
        lbl_desc.setStyleSheet("font-size: 9pt; color: #64748b; background: transparent;")
        layout.addWidget(lbl_desc)

    def set_value(self, value: str):
        self.lbl_value.setText(value)


class LaporanKinerjaPage(QWidget):

    def __init__(self):
        super().__init__()
        self._pct = 0.0
        self._setup_ui()
        self.load_statistik()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────
        header_row = QHBoxLayout()
        hdr_text = QVBoxLayout(); hdr_text.setSpacing(2)

        lbl_title = QLabel("Laporan Kinerja")
        lbl_title.setObjectName("page_title")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        hdr_text.addWidget(lbl_title)

        lbl_sub = QLabel("Ringkasan statistik proyek dan tugas")
        lbl_sub.setObjectName("page_subtitle")
        hdr_text.addWidget(lbl_sub)

        header_row.addLayout(hdr_text)
        header_row.addStretch()

        btn_refresh = QPushButton("↻  Perbarui")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(36)
        btn_refresh.setObjectName("btn_refresh")
        btn_refresh.clicked.connect(self.load_statistik)
        header_row.addWidget(btn_refresh)

        root.addLayout(header_row)
        root.addSpacing(6)

        line = QFrame(); line.setFrameShape(QFrame.HLine)
        line.setObjectName("page_header_line")
        root.addWidget(line)
        root.addSpacing(24)

        # ── Stat Cards ─────────────────────────────────────────────
        cards_row = QHBoxLayout(); cards_row.setSpacing(16)
        self.card_proyek  = StatCard("📁", "Total Proyek",      "0", "#3b82f6")
        self.card_tugas   = StatCard("📋", "Total Tugas",        "0", "#8b5cf6")
        self.card_selesai = StatCard("✅", "Tugas Done",         "0", "#10b981")
        self.card_todo    = StatCard("🔲", "Tugas Todo",         "0", "#f59e0b")
        cards_row.addWidget(self.card_proyek)
        cards_row.addWidget(self.card_tugas)
        cards_row.addWidget(self.card_selesai)
        cards_row.addWidget(self.card_todo)
        root.addLayout(cards_row)
        root.addSpacing(28)

        # ── Progress bar ────────────────────────────────────────────
        self.frame_progress = QFrame()
        self.frame_progress.setObjectName("stat_card")
        prog_layout = QVBoxLayout(self.frame_progress)
        prog_layout.setContentsMargins(20, 16, 20, 16)
        prog_layout.setSpacing(8)

        lbl_prog_title = QLabel("Tingkat Penyelesaian Tugas (Done)")
        lbl_prog_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_prog_title.setObjectName("prog_title")
        prog_layout.addWidget(lbl_prog_title)

        self.lbl_pct = QLabel("0%")
        self.lbl_pct.setObjectName("page_subtitle")
        prog_layout.addWidget(self.lbl_pct)

        bar_bg = QFrame()
        bar_bg.setFixedHeight(10)
        bar_bg.setObjectName("bar_bg")
        bar_layout = QHBoxLayout(bar_bg)
        bar_layout.setContentsMargins(0, 0, 0, 0); bar_layout.setSpacing(0)

        self.bar_fill = QFrame()
        self.bar_fill.setFixedHeight(10)
        self.bar_fill.setObjectName("bar_fill")
        bar_layout.addWidget(self.bar_fill)
        bar_layout.addStretch()

        prog_layout.addWidget(bar_bg)
        self._bar_bg = bar_bg
        root.addWidget(self.frame_progress)
        root.addSpacing(28)

        # ── Export Section ──────────────────────────────────────────
        export_frame = QFrame()
        export_frame.setObjectName("export_frame")
        exp_layout = QVBoxLayout(export_frame)
        exp_layout.setContentsMargins(20, 18, 20, 18)
        exp_layout.setSpacing(12)

        lbl_export = QLabel("Ekspor Laporan")
        lbl_export.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_export.setObjectName("export_title")
        exp_layout.addWidget(lbl_export)

        lbl_exp_sub = QLabel("Unduh data proyek dan tugas dalam format CSV atau PDF.")
        lbl_exp_sub.setObjectName("page_subtitle")
        exp_layout.addWidget(lbl_exp_sub)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)

        self.btn_export_csv = QPushButton(icon("csv.png"), "  Ekspor CSV")
        self.btn_export_csv.setFixedHeight(40)
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)
        self.btn_export_csv.setObjectName("btn_csv")

        self.btn_export_pdf = QPushButton(icon("pdf.png"), "  Ekspor PDF")
        self.btn_export_pdf.setFixedHeight(40)
        self.btn_export_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_export_pdf.setObjectName("btn_pdf")

        btn_row.addWidget(self.btn_export_csv)
        btn_row.addWidget(self.btn_export_pdf)
        btn_row.addStretch()
        exp_layout.addLayout(btn_row)
        root.addWidget(export_frame)
        root.addStretch()

        self.btn_export_csv.clicked.connect(self._export_csv)
        self.btn_export_pdf.clicked.connect(self._export_pdf)

    def load_statistik(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM proyek")
        total_proyek = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tugas")
        total_tugas = c.fetchone()[0]
        # FIX: status "Done" (bukan "Selesai") sesuai nilai di Kanban Board
        c.execute("SELECT COUNT(*) FROM tugas WHERE status = 'Done'")
        tugas_done = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tugas WHERE status = 'Todo'")
        tugas_todo = c.fetchone()[0]
        conn.close()

        self.card_proyek.set_value(str(total_proyek))
        self.card_tugas.set_value(str(total_tugas))
        self.card_selesai.set_value(str(tugas_done))
        self.card_todo.set_value(str(tugas_todo))

        pct = (tugas_done / total_tugas * 100) if total_tugas > 0 else 0
        self._pct = pct
        self.lbl_pct.setText(
            f"{tugas_done} dari {total_tugas} tugas selesai  ({pct:.0f}%)"
        )
        self._update_bar()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_bar()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_bar()

    def _update_bar(self):
        total_w = self._bar_bg.width()
        if total_w > 0:
            fill_w = max(0, int(total_w * self._pct / 100))
            self.bar_fill.setFixedWidth(fill_w)

    def _export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Ekspor CSV", "laporan_taskai.csv", "CSV (*.csv)"
        )
        if not file_path:
            return
        try:
            DataExporter.export_csv(file_path)
            QMessageBox.information(self, "Berhasil", f"File CSV berhasil disimpan:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal mengekspor CSV:\n{e}")

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Ekspor PDF", "laporan_taskai.pdf", "PDF (*.pdf)"
        )
        if not file_path:
            return
        try:
            DataExporter.export_pdf(file_path)
            QMessageBox.information(self, "Berhasil", f"File PDF berhasil disimpan:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Gagal mengekspor PDF:\n{e}")
