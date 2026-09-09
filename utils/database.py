import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "database/riwayat_sentimen.db"

def inisialisasi_db():
    """
    Membuat database dan tabel jika belum tersedia.
    """

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS riwayat_sentimen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teks_asli TEXT,
                    teks_bersih TEXT,
                    klasifikasi TEXT,
                    waktu DATETIME
                )
            """)

    except sqlite3.Error as e:
        print(f"Error inisialisasi database: {e}")

def simpan_ke_db(teks_asli, teks_bersih, klasifikasi):
    inisialisasi_db()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            waktu = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            conn.execute("""
                INSERT INTO riwayat_sentimen
                (teks_asli, teks_bersih, klasifikasi, waktu)
                VALUES (?, ?, ?, ?)
            """, (
                teks_asli,
                teks_bersih,
                klasifikasi,
                waktu
            ))

    except sqlite3.Error as e:
        print(f"Error menyimpan data: {e}")

def ambil_data_db(limit=20, offset=0):
    inisialisasi_db()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(
                """
                SELECT
                    id,
                    teks_asli,
                    teks_bersih,
                    klasifikasi,
                    waktu
                FROM riwayat_sentimen
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                conn,
                params=(limit, offset)
            )

        return df

    except sqlite3.Error as e:
        print(f"Error mengambil data: {e}")
        return pd.DataFrame()

def hapus_data_db(id_data):
    inisialisasi_db()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                """
                DELETE FROM riwayat_sentimen
                WHERE id = ?
                """,
                (id_data,)
            )

            return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Error menghapus data: {e}")
        return False

def hitung_total_data():
    inisialisasi_db()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM riwayat_sentimen
            """)

            return cursor.fetchone()[0]

    except sqlite3.Error as e:
        print(f"Error menghitung total data: {e}")
        return 0

def ambil_semua_data_statistik():
    inisialisasi_db()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(
                """
                SELECT
                    klasifikasi,
                    waktu
                FROM riwayat_sentimen
                ORDER BY id ASC
                """,
                conn
            )

        return df

    except sqlite3.Error as e:
        print(f"Error mengambil data statistik: {e}")
        return pd.DataFrame()

def ambil_semua_data_csv():
    inisialisasi_db()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(
                """
                SELECT
                    id,
                    teks_asli,
                    teks_bersih,
                    klasifikasi,
                    waktu
                FROM riwayat_sentimen
                ORDER BY id DESC
                """,
                conn
            )

        return df

    except sqlite3.Error as e:
        print(f"Error mengambil data CSV: {e}")
        return pd.DataFrame()