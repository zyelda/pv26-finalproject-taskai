from database.db_manager import get_connection


class TugasModel:

    @staticmethod
    def add_tugas(proyek_id, nama_tugas, deskripsi, prioritas, status):
        """Tambah tugas baru ke database."""
        conn = get_connection()
        try:
            conn.execute(
                """INSERT INTO tugas (proyek_id, nama_tugas, deskripsi, prioritas, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (proyek_id, nama_tugas, deskripsi, prioritas, status)
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_tugas_by_proyek(proyek_id):
        """Ambil semua tugas milik sebuah proyek."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM tugas WHERE proyek_id = ? ORDER BY id DESC",
                (proyek_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_all_tugas():
        """Ambil semua tugas dari semua proyek."""
        conn = get_connection()
        try:
            cursor = conn.execute("SELECT * FROM tugas ORDER BY id DESC")
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_tugas_by_id(tugas_id):
        """Ambil satu tugas berdasarkan ID."""
        conn = get_connection()
        try:
            cursor = conn.execute("SELECT * FROM tugas WHERE id = ?", (tugas_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update_status_tugas(tugas_id, status):
        """Update kolom status tugas (drag-and-drop Kanban)."""
        conn = get_connection()
        try:
            conn.execute(
                "UPDATE tugas SET status = ? WHERE id = ?",
                (status, tugas_id)
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def update_tugas(tugas_id, nama_tugas, deskripsi, prioritas, status):
        """Update semua kolom sebuah tugas."""
        conn = get_connection()
        try:
            conn.execute(
                """UPDATE tugas
                   SET nama_tugas = ?, deskripsi = ?, prioritas = ?, status = ?
                   WHERE id = ?""",
                (nama_tugas, deskripsi, prioritas, status, tugas_id)
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete_tugas(tugas_id):
        """Hapus tugas berdasarkan ID."""
        conn = get_connection()
        try:
            conn.execute("DELETE FROM tugas WHERE id = ?", (tugas_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def search_tugas(keyword):
        """Cari tugas berdasarkan nama atau deskripsi."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """SELECT * FROM tugas
                   WHERE nama_tugas LIKE ? OR deskripsi LIKE ?
                   ORDER BY id DESC""",
                (f"%{keyword}%", f"%{keyword}%")
            )
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def filter_tugas(proyek_id=None, prioritas=None, status=None):
        """Filter tugas dinamis berdasarkan kombinasi kolom."""
        conn = get_connection()
        try:
            query = "SELECT * FROM tugas WHERE 1=1"
            params = []

            if proyek_id is not None:
                query += " AND proyek_id = ?"
                params.append(proyek_id)
            if prioritas is not None:
                query += " AND prioritas = ?"
                params.append(prioritas)
            if status is not None:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY id DESC"
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()
