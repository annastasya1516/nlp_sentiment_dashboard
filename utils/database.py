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


def ambil_data_db():
    inisialisasi_db()

    conn = None

    try:
        conn = sqlite3.connect(DB_PATH)

        df = pd.read_sql_query(
            "SELECT * FROM riwayat_sentimen ORDER BY id DESC",
            conn
        )

        return df

    except sqlite3.Error as e:
        print(f"Error mengambil data: {e}")
        return pd.DataFrame()

    finally:
        if conn:
            conn.close()