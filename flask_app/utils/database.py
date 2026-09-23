import os
import sqlite3

from datetime import datetime
from zoneinfo import ZoneInfo


# =========================================================
# DATABASE CONNECTION
# =========================================================

def _get_db_connection():

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    db_path = os.path.join(
        base_dir,
        "database",
        "riwayat_sentimen.db"
    )

    return sqlite3.connect(db_path)


# =========================================================
# SIMPAN RIWAYAT
# =========================================================

def simpan_ke_db(
    teks_asli,
    teks_bersih,
    klasifikasi,
    confidence=None
):

    # Ambil waktu lokal Indonesia (WIB)
    waktu = datetime.now(
        ZoneInfo("Asia/Jakarta")
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        INSERT INTO riwayat_sentimen (
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence,
            waktu
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence,
            waktu
        )
    )


    koneksi.commit()
    koneksi.close()


# =========================================================
# AMBIL RIWAYAT
# =========================================================

def ambil_riwayat(
    limit=20,
    offset=0
):

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            id,
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence,
            waktu
        FROM riwayat_sentimen
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        (
            limit,
            offset
        )
    )


    data = cursor.fetchall()

    koneksi.close()

    return data


# =========================================================
# HITUNG TOTAL RIWAYAT
# =========================================================

def hitung_total_riwayat():

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM riwayat_sentimen
        """
    )


    total = cursor.fetchone()[0]

    koneksi.close()

    return total


# =========================================================
# STATISTIK SENTIMEN
# =========================================================

def ambil_statistik():

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            klasifikasi,
            COUNT(*)
        FROM riwayat_sentimen
        GROUP BY klasifikasi
        """
    )


    data = cursor.fetchall()

    koneksi.close()


    statistik = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "invalid": 0
    }


    for klasifikasi, jumlah in data:

        if klasifikasi in statistik:

            statistik[klasifikasi] = jumlah


    statistik["total"] = sum(
        statistik.values()
    )


    return statistik


# =========================================================
# AMBIL SEMUA RIWAYAT
# =========================================================

def ambil_semua_riwayat():

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            id,
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence,
            waktu
        FROM riwayat_sentimen
        ORDER BY id DESC
        """
    )


    data = cursor.fetchall()

    koneksi.close()

    return data


# =========================================================
# STATISTIK HARIAN
# =========================================================

def ambil_statistik_harian():

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            DATE(waktu) AS tanggal,
            COUNT(*) AS jumlah
        FROM riwayat_sentimen
        GROUP BY DATE(waktu)
        ORDER BY tanggal ASC
        """
    )


    data = cursor.fetchall()

    koneksi.close()

    return data


# =========================================================
# STATISTIK BULANAN
# =========================================================

def ambil_statistik_bulanan():

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            strftime('%Y-%m', waktu) AS bulan,
            COUNT(*) AS jumlah
        FROM riwayat_sentimen
        GROUP BY strftime('%Y-%m', waktu)
        ORDER BY bulan ASC
        """
    )


    data = cursor.fetchall()

    koneksi.close()

    return data


# =========================================================
# STATISTIK TAHUNAN
# =========================================================

def ambil_statistik_tahunan():

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            strftime('%Y', waktu) AS tahun,
            COUNT(*) AS jumlah
        FROM riwayat_sentimen
        GROUP BY strftime('%Y', waktu)
        ORDER BY tahun ASC
        """
    )


    data = cursor.fetchall()

    koneksi.close()

    return data


# =========================================================
# HAPUS RIWAYAT
# =========================================================

def hapus_riwayat(ids_data):

    if not ids_data:
        return


    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    placeholder = ",".join(
        "?" for _ in ids_data
    )


    cursor.execute(
        f"""
        DELETE FROM riwayat_sentimen
        WHERE id IN ({placeholder})
        """,
        ids_data
    )


    koneksi.commit()
    koneksi.close()


# =========================================================
# EDIT RIWAYAT
# =========================================================

def edit_riwayat(
    id_data,
    teks_asli,
    teks_bersih,
    klasifikasi,
    confidence
):

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        UPDATE riwayat_sentimen
        SET
            teks_asli = ?,
            teks_bersih = ?,
            klasifikasi = ?,
            confidence = ?
        WHERE id = ?
        """,
        (
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence,
            id_data
        )
    )


    koneksi.commit()
    koneksi.close()


# =========================================================
# AMBIL RIWAYAT BERDASARKAN ID
# =========================================================

def ambil_riwayat_by_id(id_data):

    koneksi = _get_db_connection()
    cursor = koneksi.cursor()


    cursor.execute(
        """
        SELECT
            id,
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence,
            waktu
        FROM riwayat_sentimen
        WHERE id = ?
        """,
        (id_data,)
    )


    data = cursor.fetchone()

    koneksi.close()

    return data