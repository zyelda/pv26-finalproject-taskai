import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog, QFormLayout, QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.db_manager import setup_database, ganti_password
from ui.manajemen_proyek_page import ManajemenProyekPage
from ui.laporan_kinerja_page import LaporanKinerjaPage
from assets import icon

_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_qss(filename: str) -> str:
    path = os.path.join(_DIR, "assets", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


class GantiPasswordDialog(QDialog):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self._username = username
        self.setWindowTitle("Ganti Password")
        self.setMinimumWidth(360)
        self.setModal(True)

        form = QFormLayout(self)
        form.setContentsMargins(24, 24, 24, 24)
        form.setSpacing(12)

        self.txt_lama = QLineEdit(); self.txt_lama.setEchoMode(QLineEdit.Password)
        self.txt_baru = QLineEdit(); self.txt_baru.setEchoMode(QLineEdit.Password)
        self.txt_konfirm = QLineEdit(); self.txt_konfirm.setEchoMode(QLineEdit.Password)
        self.txt_lama.setPlaceholderText("Password saat ini")
        self.txt_baru.setPlaceholderText("Password baru")
        self.txt_konfirm.setPlaceholderText("Ulangi password baru")
        self.txt_lama.setFixedHeight(38)
        self.txt_baru.setFixedHeight(38)
        self.txt_konfirm.setFixedHeight(38)

        form.addRow("Password Lama:", self.txt_lama)
        form.addRow("Password Baru:", self.txt_baru)
        form.addRow("Konfirmasi:", self.txt_konfirm)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("Simpan"); btn_ok.setFixedHeight(38)
        btn_batal = QPushButton("Batal"); btn_batal.setFixedHeight(38)
        btn_ok.clicked.connect(self._simpan); btn_batal.clicked.connect(self.reject)
        btn_row.addStretch(); btn_row.addWidget(btn_batal); btn_row.addWidget(btn_ok)
        form.addRow(btn_row)

    def _simpan(self):
        if not self.txt_baru.text():
            QMessageBox.warning(self, "Gagal", "Password baru tidak boleh kosong."); return
        if self.txt_baru.text() != self.txt_konfirm.text():
            QMessageBox.warning(self, "Gagal", "Konfirmasi password tidak cocok."); return

        berhasil = ganti_password(self._username, self.txt_lama.text(), self.txt_baru.text())
        if not berhasil:
            QMessageBox.warning(self, "Gagal", "Password lama salah."); return

        QMessageBox.information(self, "Berhasil", "Password berhasil diubah.")
        self.accept()


class MainWindow(QMainWindow):
    # Dark-mode overlay — meng-override warna hardcoded pada child widgets
    _DARK_QSS = """
        QWidget { color: #e2e8f0; background-color: #0f172a; }
        QMainWindow { background-color: #0f172a; }
        QStackedWidget, QStackedWidget > QWidget { background-color: #0f172a; }
        QFrame#sidebar { background-color: #020617; border-right: 1px solid #1e293b; }
        QFrame#header_bar { background-color: #0f172a; border-bottom: 1px solid #1e293b; }
        QFrame#login_card, QFrame#stat_card, QFrame#export_frame,
        QFrame#frame_progress { background-color: #1e293b; border-color: #334155; }
        QLineEdit, QTextEdit, QComboBox, QDateEdit {
            background-color: #1e293b; color: #e2e8f0; border-color: #475569; }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
            border-color: #3b82f6; }
        QComboBox QAbstractItemView { background: #1e293b; color: #e2e8f0;
            selection-background-color: #334155; }
        QTableWidget { background-color: #1e293b; alternate-background-color: #162032;
            color: #e2e8f0; gridline-color: #334155; }
        QTableWidget::item { color: #e2e8f0; background-color: transparent; }
        QTableWidget::item:selected { background-color: #334155; color: #f8fafc; }
        QHeaderView::section { background-color: #020617; color: #94a3b8;
            border-color: #1e293b; }
        QDialog { background-color: #1e293b; }
        QMessageBox { background-color: #1e293b; }
        QMessageBox QLabel { color: #e2e8f0; background: transparent; }
        QLabel { color: #e2e8f0; background: transparent; }
        QLabel#page_subtitle, QLabel#stat_label { color: #94a3b8; }
        QLabel#sidebar_subtitle { color: #64748b; }
        QScrollBar:vertical, QScrollBar:horizontal { background: #1e293b; }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background: #475569; }
        QMenu { background-color: #1e293b; color: #e2e8f0; border-color: #334155; }
        QMenu::item:selected { background-color: #334155; color: #f8fafc; }
        QFrame[frameShape="4"], QFrame[frameShape="5"] { background: #334155; }
        /* Kanban cards di dark mode */
        QFrame#kanban_card { background-color: #1e293b; border-color: #334155; }
        QScrollArea { background: transparent; border: none; }
        /* Kolom kanban di dark mode */
        QWidget#kolom_todo { background-color: #1a1f3a; }
        QWidget#kolom_prog { background-color: #2a1f0a; }
        QWidget#kolom_done { background-color: #0a2a1a; }
        /* Pastikan label stat cards terbaca */
        QLabel#stat_number { background: transparent; }
        QLabel#stat_label { background: transparent; }
        QLabel#stat_icon { background: transparent; }
        /* Header bar page title */
        QLabel#page_title_header { color: #f1f5f9; background: transparent; }
        QLabel#page_sub_header { color: #94a3b8; background: transparent; }
        /* Panel konten Manajemen Proyek — jangan biarkan tetap terang */
        QWidget#manajemen_content { background-color: #0f172a; }
        /* Link Daftar/Masuk di halaman login & register */
        QPushButton#btn_auth_link { color: #60a5fa; }
        QPushButton#btn_auth_link:hover { color: #93c5fd; }
        QLabel#login_switch_label { color: #94a3b8; }
    """

    def __init__(self, username: str = "admin"):
        super().__init__()
        self._username = username
        self.setWindowTitle("TaskAI")
        self.setWindowIcon(icon("taskai.png"))
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self._active_btn = None
        self._dark_mode = False
        self._setup_central_widget()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._switch_page(0, self._btn_manajemen)

    def _setup_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._setup_sidebar(layout)
        self._setup_pages(layout)

    def _setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        # Logo area
        logo_area = QWidget()
        logo_area.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_area)
        logo_layout.setContentsMargins(20, 24, 20, 16)
        logo_layout.setSpacing(4)

        lbl_app = QLabel("TaskAI")
        lbl_app.setObjectName("sidebar_title")
        lbl_app.setFont(QFont("Segoe UI", 14, QFont.Bold))
        logo_layout.addWidget(lbl_app)

        lbl_app_sub = QLabel("Manajemen Proyek")
        lbl_app_sub.setObjectName("sidebar_subtitle")
        logo_layout.addWidget(lbl_app_sub)

        side_layout.addWidget(logo_area)

        divider = QFrame()
        divider.setObjectName("sidebar_divider")
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        side_layout.addWidget(divider)
        side_layout.addSpacing(10)

        lbl_nav = QLabel("NAVIGASI")
        lbl_nav.setStyleSheet(
            "color: #475569; font-size: 7.5pt; font-weight: bold;"
            " letter-spacing: 1px; padding: 0 16px 4px 16px; background: transparent;"
        )
        side_layout.addWidget(lbl_nav)

        self._btn_manajemen = self._make_nav_btn(icon("project.png", "#cbd5e1"), "Manajemen Proyek")
        self._btn_kanban    = self._make_nav_btn(icon("board.png",   "#cbd5e1"), "Kanban Board")
        self._btn_laporan   = self._make_nav_btn(icon("report.png",  "#cbd5e1"), "Laporan Kinerja")

        self._btn_manajemen.clicked.connect(lambda: self._switch_page(0, self._btn_manajemen))
        self._btn_kanban.clicked.connect(lambda: self._switch_page(1, self._btn_kanban))
        self._btn_laporan.clicked.connect(lambda: self._switch_page(2, self._btn_laporan))

        side_layout.addWidget(self._btn_manajemen)
        side_layout.addWidget(self._btn_kanban)
        side_layout.addWidget(self._btn_laporan)
        side_layout.addStretch()

        # Info pengguna + tombol logout
        user_area = QWidget()
        user_area.setStyleSheet("background: transparent;")
        user_layout = QVBoxLayout(user_area)
        user_layout.setContentsMargins(16, 8, 16, 12)
        user_layout.setSpacing(8)

        lbl_user = QLabel(f"👤 {self._username}")
        lbl_user.setStyleSheet(
            "color: #cbd5e1; font-size: 9pt; font-weight: 600; background: transparent;"
        )
        user_layout.addWidget(lbl_user)

        btn_logout = QPushButton(icon("login.png", "#f87171"), "  Logout")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setObjectName("btn_logout_sidebar")
        btn_logout.setStyleSheet(
            "QPushButton#btn_logout_sidebar {"
            " background: transparent; color: #f87171; border: 1px solid #f87171;"
            " border-radius: 6px; padding: 6px 10px; font-size: 9pt; font-weight: 600;"
            " text-align: left; }"
            "QPushButton#btn_logout_sidebar:hover { background: rgba(248,113,113,0.12); }"
            "QPushButton#btn_logout_sidebar:pressed { background: rgba(248,113,113,0.22); }"
        )
        btn_logout.clicked.connect(self._logout)
        user_layout.addWidget(btn_logout)

        side_layout.addWidget(user_area)

        lbl_ver = QLabel("v1.0  •  Kelompok 13")
        lbl_ver.setStyleSheet(
            "color: #475569; font-size: 7.5pt; padding: 0 16px 12px 16px; background: transparent;"
        )
        side_layout.addWidget(lbl_ver)

        parent_layout.addWidget(sidebar)

    @staticmethod
    def _make_nav_btn(btn_icon, text: str) -> QPushButton:
        btn = QPushButton(btn_icon, f"  {text}")
        btn.setCheckable(False)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("active", False)
        return btn

    def _switch_page(self, index: int, btn: QPushButton):
        if self._active_btn and self._active_btn is not btn:
            self._active_btn.setProperty("active", False)
            self._active_btn.style().unpolish(self._active_btn)
            self._active_btn.style().polish(self._active_btn)

        btn.setProperty("active", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self._active_btn = btn
        self.stacked_widget.setCurrentIndex(index)

        # Refresh halaman saat dibuka
        if index == 1:
            self.page_kanban._load_proyek()
            self.page_kanban.refresh()
        elif index == 2:
            self.page_laporan.load_statistik()

    def _setup_pages(self, parent_layout):
        self.stacked_widget = QStackedWidget()
        parent_layout.addWidget(self.stacked_widget, 1)

        self.page_manajemen = ManajemenProyekPage()
        self.stacked_widget.addWidget(self.page_manajemen)

        from ui.kanban_board_page import KanbanBoardPage
        self.page_kanban = KanbanBoardPage()
        self.stacked_widget.addWidget(self.page_kanban)

        self.page_laporan = LaporanKinerjaPage()
        self.stacked_widget.addWidget(self.page_laporan)

    def _setup_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Ekspor CSV/PDF", lambda: self._switch_page(2, self._btn_laporan))
        self._action_dark = file_menu.addAction("Mode Gelap", self._toggle_dark_mode)
        self._action_dark.setCheckable(True)
        file_menu.addAction("Ganti Password", self._ganti_password)
        file_menu.addSeparator()
        file_menu.addAction("Logout", self._logout)
        file_menu.addAction("Exit", self.close)
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About App", self._show_about)

    def _toggle_dark_mode(self):
        self._dark_mode = not self._dark_mode
        app = QApplication.instance()
        base_qss = _load_qss("style.qss")
        if self._dark_mode:
            app.setStyleSheet(base_qss + self._DARK_QSS)
            self._action_dark.setText("Mode Terang")
        else:
            app.setStyleSheet(base_qss)
            self._action_dark.setText("Mode Gelap")

    def _ganti_password(self):
        GantiPasswordDialog(self._username, self).exec()

    def _logout(self):
        jawaban = QMessageBox.question(
            self, "Logout", "Apakah Anda yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if jawaban == QMessageBox.Yes:
            app = QApplication.instance()
            callback = getattr(app, "_on_logout", None)
            self.close()
            if callable(callback):
                callback()

    def _setup_status_bar(self):
        self.statusBar().showMessage(
            "Kelompok 13: Toriq (F1D02310031)  •  Afif (F1D02310125)  •  Izzul (F1D02410077)"
        )

    def _show_about(self):
        QMessageBox.information(
            self, "About TaskAI",
            "TaskAI v1.0\nAplikasi Manajemen Proyek dan Tugas\n\n"
            "Dibangun dengan PySide6 & SQLite\n"
            "Pemrograman Visual — Semester Genap 2025/2026\n\n"
            "Kelompok 13:\n"
            "• Toriq (F1D02310031)\n"
            "• Afif (F1D02310125)\n"
            "• Izzul (F1D02410077)",
        )


def main():
    app = QApplication(sys.argv)

    setup_database()

    base_qss = _load_qss("style.qss")
    if base_qss:
        app.setStyleSheet(base_qss)

    from ui.login_page import LoginPage
    from ui.register_page import RegisterPage

    state = {"login": None, "register": None, "window": None}

    def show_login():
        if state["window"] is not None:
            state["window"] = None
        if state["register"] is not None:
            state["register"].close()
            state["register"] = None
        login = LoginPage()
        login.login_success.connect(lambda: on_login_success(login))
        login.daftar_diminta.connect(lambda: show_register())
        state["login"] = login
        login.show()

    def show_register():
        if state["login"] is not None:
            state["login"].close()
            state["login"] = None
        register = RegisterPage()
        register.register_success.connect(lambda: show_login())
        register.kembali_ke_login.connect(lambda: show_login())
        state["register"] = register
        register.show()

    def on_login_success(login_page):
        username = login_page.txt_username.text().strip()
        login_page.close()
        state["login"] = None
        window = MainWindow(username=username)
        window.show()
        state["window"] = window
        app._main_window = window

    app._on_logout = show_login

    show_login()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
