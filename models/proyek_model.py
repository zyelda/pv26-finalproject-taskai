from typing import List, Dict, Optional
from database.db_manager import get_connection


class ProyekModel:
    @staticmethod
    def add_proyek(nama_proyek: str, klien: str, deadline: str, status: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO proyek (nama_proyek, klien, deadline, status) VALUES (?, ?, ?, ?)",
            (nama_proyek, klien, deadline, status),
        )
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    @staticmethod
    def get_all_proyek() -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proyek ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def update_proyek(
        proyek_id: int,
        nama_proyek: str,
        klien: str,
        deadline: str,
        status: str,
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE proyek SET nama_proyek = ?, klien = ?, deadline = ?, status = ? WHERE id = ?",
            (nama_proyek, klien, deadline, status, proyek_id),
        )
        conn.commit()
        affected = cursor.rowcount > 0
        conn.close()
        return affected

    @staticmethod
    def delete_proyek(proyek_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proyek WHERE id = ?", (proyek_id,))
        conn.commit()
        affected = cursor.rowcount > 0
        conn.close()
        return affected
