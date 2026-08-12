import sqlite3
import pandas as pd
from datetime import datetime


DB_PATH = "database/riwayat_sentimen.db"


def inisialisasi_db():
    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS riwayat_sentimen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teks_asli TEXT,
                teks_bersih TEXT,
                klasifikasi TEXT,
                waktu DATETIME
            )
        """)

        conn.commit()

    except sqlite3.Error as e:
        print(f"Error inisialisasi database: {e}")

    finally:
        if conn:
            conn.close()


def simpan_ke_db(teks_asli, teks_bersih, klasifikasi):
    inisialisasi_db()

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO riwayat_sentimen
            (teks_asli, teks_bersih, klasifikasi, waktu)
            VALUES (?, ?, ?, ?)
        """, (teks_asli, teks_bersih, klasifikasi, waktu))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Error menyimpan data: {e}")

    finally:
        if conn:
            conn.close()


def ambil_data_db(limit=20):
    inisialisasi_db()

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)

        df = pd.read_sql_query(
            """
            SELECT *
            FROM riwayat_sentimen
            ORDER BY id DESC
            LIMIT ?
            """,
            conn,
            params=(limit,)
        )

        return df

    except sqlite3.Error as e:
        print(f"Error mengambil data: {e}")
        return pd.DataFrame()

    finally:
        if conn:
            conn.close()
            
def hitung_total_data():
    inisialisasi_db()

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM riwayat_sentimen
        """)

        total = cursor.fetchone()[0]

        return total

    except sqlite3.Error as e:
        print(f"Error menghitung total data: {e}")
        return 0

    finally:
        if conn:
            conn.close()
            
def ambil_semua_data_statistik():
    inisialisasi_db()

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)

        df = pd.read_sql_query(
            """
            SELECT klasifikasi, waktu
            FROM riwayat_sentimen
            ORDER BY id ASC
            """,
            conn
        )

        return df

    except sqlite3.Error as e:
        print(f"Error mengambil data statistik: {e}")
        return pd.DataFrame()

    finally:
        if conn:
            conn.close()