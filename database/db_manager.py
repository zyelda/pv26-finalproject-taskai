import sqlite3
import os
import hashlib
import secrets

_db_path: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "taskai.db"
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def setup_database() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyek (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_proyek TEXT    NOT NULL,
            klien       TEXT    NOT NULL,
            deadline    TEXT    NOT NULL,
            status      TEXT    NOT NULL
        )
    """)
    # FIX: tambah ON DELETE CASCADE agar hapus proyek ikut hapus tugas-nya
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tugas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            proyek_id  INTEGER NOT NULL,
            nama_tugas TEXT    NOT NULL,
            deskripsi  TEXT,
            prioritas  TEXT    NOT NULL,
            status     TEXT    NOT NULL,
            FOREIGN KEY(proyek_id) REFERENCES proyek(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pengguna (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            salt          TEXT    NOT NULL,
            dibuat_pada   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Akun default agar kompatibel dengan login lama (admin/admin)
    cursor.execute("SELECT COUNT(*) AS jumlah FROM pengguna")
    if cursor.fetchone()["jumlah"] == 0:
        salt, password_hash = _hash_password("admin")
        cursor.execute(
            "INSERT INTO pengguna (username, password_hash, salt) VALUES (?, ?, ?)",
            ("admin", password_hash, salt),
        )
        conn.commit()

    conn.close()


def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password dengan PBKDF2-HMAC-SHA256 + salt acak.
    Mengembalikan tuple (salt, password_hash)."""
    if salt is None:
        salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    ).hex()
    return salt, password_hash


def username_tersedia(username: str) -> bool:
    """True jika username belum dipakai (tersedia untuk didaftarkan)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pengguna WHERE username = ?", (username,))
    hasil = cursor.fetchone()
    conn.close()
    return hasil is None


def daftar_pengguna(username: str, password: str) -> bool:
    """Mendaftarkan pengguna baru. Mengembalikan False jika username sudah ada."""
    if not username_tersedia(username):
        return False
    salt, password_hash = _hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pengguna (username, password_hash, salt) VALUES (?, ?, ?)",
        (username, password_hash, salt),
    )
    conn.commit()
    conn.close()
    return True


def verifikasi_login(username: str, password: str) -> bool:
    """Mengecek kecocokan username & password terhadap tabel pengguna."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, salt FROM pengguna WHERE username = ?", (username,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return False
    _, password_hash = _hash_password(password, row["salt"])
    return secrets.compare_digest(password_hash, row["password_hash"])


def ganti_password(username: str, password_lama: str, password_baru: str) -> bool:
    """Mengganti password pengguna jika password_lama cocok.
    Mengembalikan False jika username tidak ada atau password_lama salah."""
    if not verifikasi_login(username, password_lama):
        return False
    salt, password_hash = _hash_password(password_baru)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pengguna SET password_hash = ?, salt = ? WHERE username = ?",
        (password_hash, salt, username),
    )
    conn.commit()
    conn.close()
    return True
