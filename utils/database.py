import sqlite3
import pandas as pd

def simpan_ke_db(teks_asli, teks_bersih, klasifikasi):
    conn = sqlite3.connect('database/riwayat_sentimen.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO riwayat_sentimen (teks_asli, teks_bersih, klasifikasi) VALUES (?, ?, ?)', 
        (teks_asli, teks_bersih, klasifikasi)
    )
    conn.commit()
    conn.close()
    
def ambil_data_db():
    conn = sqlite3.connect('database/riwayat_sentimen.db')
    df = pd.read_sql_query('SELECT * FROM riwayat_sentimen ORDER BY id DESC', conn)
    conn.close()
    return df
