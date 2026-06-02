import sqlite3
import os

_db_path: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "taskai.db")


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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_proyek TEXT,
            klien TEXT,
            deadline TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tugas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyek_id INTEGER,
            nama_tugas TEXT,
            deskripsi TEXT,
            prioritas TEXT,
            status TEXT,
            FOREIGN KEY(proyek_id) REFERENCES proyek(id)
        )
    """)
    conn.commit()
    conn.close()
