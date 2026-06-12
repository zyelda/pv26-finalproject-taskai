import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt
from database.db_manager import setup_database
from ui.manajemen_proyek_page import ManajemenProyekPage
from ui.laporan_kinerja_page import LaporanKinerjaPage
from PySide6.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TaskAI")
        self.setWindowIcon(
            QIcon("assets/icons/taskai.png")
        )

        self.resize(1200, 800)

        setup_database()

        self._setup_central_widget()
        self._setup_menu_bar()
        self._setup_status_bar()

    def _setup_central_widget(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._setup_sidebar(layout)
        self._setup_pages(layout)

    def _setup_sidebar(self, parent_layout: QHBoxLayout) -> None:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(
            "QFrame#sidebar { background-color: #2c3e50; }"
            "QPushButton { color: white; background: transparent;"
            "  border: none; padding: 15px; text-align: left; font-size: 14px; }"
            "QPushButton:hover { background-color: #34495e; }"
            "QPushButton:pressed { background-color: #1abc9c; }"
        )

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 10, 0, 10)
        side_layout.setSpacing(0)

        btn_manajemen = QPushButton(
            QIcon("assets/icons/project.png"),
            "Manajemen Proyek"
        )

        btn_kanban = QPushButton(
            QIcon("assets/icons/board.png"),
            "Kanban Board"
        )

        btn_laporan = QPushButton(
            QIcon("assets/icons/report.png"),
            "Laporan Kinerja"
        )

        btn_manajemen.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn_kanban.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        btn_laporan.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        side_layout.addWidget(btn_manajemen)
        side_layout.addWidget(btn_kanban)
        side_layout.addWidget(btn_laporan)
        side_layout.addStretch()

        parent_layout.addWidget(sidebar)

    def _setup_pages(self, parent_layout: QHBoxLayout) -> None:
        self.stacked_widget = QStackedWidget()
        parent_layout.addWidget(self.stacked_widget, 1)

        self.page_manajemen = ManajemenProyekPage()
        self.stacked_widget.addWidget(self.page_manajemen)

        self.page_kanban = QWidget()
        QVBoxLayout(self.page_kanban).addWidget(
        QLabel("Kanban Board"),
        alignment=Qt.AlignCenter
    )
        self.stacked_widget.addWidget(self.page_kanban)

        self.page_laporan = LaporanKinerjaPage()
        self.stacked_widget.addWidget(self.page_laporan)

    def _setup_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Export")
        file_menu.addAction("Toggle Dark Mode")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About App", self._show_about)

    def _setup_status_bar(self) -> None:
        status_bar = self.statusBar()
        status_bar.setEnabled(False)
        status_bar.showMessage(
            "Kelompok 13: Toriq (F1D02310031), Afif (F1D02310125), Izzul (F1D02410077)"
        )

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About TaskAI",
            "TaskAI v1.0\n"
            "Aplikasi Manajemen Proyek dan Tugas\n\n"
            "Dibangun dengan PySide6 & SQLite\n"
            "Pemrograman Visual - Semester Genap 2025/2026",
        )


def main():

    app = QApplication(sys.argv)

    window = MainWindow()

    # Load style.qss
    qss_path = os.path.join(
        os.path.dirname(__file__),
        "assets",
        "style.qss"
    )

    if os.path.exists(qss_path):

        with open(qss_path, "r") as file:

            app.setStyleSheet(
                file.read()
            )

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
