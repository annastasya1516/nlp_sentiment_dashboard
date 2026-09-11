import sqlite3
import os


def simpan_ke_db(teks_asli, teks_bersih, klasifikasi):

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

    koneksi = sqlite3.connect(db_path)

    cursor = koneksi.cursor()

    cursor.execute(
        """
        INSERT INTO riwayat_sentimen
        (teks_asli, teks_bersih, klasifikasi)
        VALUES (?, ?, ?)
        """,
        (
            teks_asli,
            teks_bersih,
            klasifikasi
        )
    )

    koneksi.commit()

    koneksi.close()


def ambil_riwayat(limit=20, offset=0):

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

    koneksi = sqlite3.connect(db_path)

    cursor = koneksi.cursor()

    cursor.execute(
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
        (
            limit,
            offset
        )
    )

    data = cursor.fetchall()

    koneksi.close()

    return data


def hitung_total_riwayat():

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

    koneksi = sqlite3.connect(db_path)

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


def ambil_statistik():

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

    koneksi = sqlite3.connect(db_path)

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


def ambil_semua_riwayat():

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

    koneksi = sqlite3.connect(db_path)

    cursor = koneksi.cursor()

    cursor.execute(
        """
        SELECT
            id,
            teks_asli,
            teks_bersih,
            klasifikasi,
            waktu
        FROM riwayat_sentimen
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    koneksi.close()

    return data


def ambil_statistik_harian():

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

    koneksi = sqlite3.connect(db_path)

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


def ambil_statistik_bulanan():

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

    koneksi = sqlite3.connect(db_path)

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

def ambil_statistik_tahunan():

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

    koneksi = sqlite3.connect(db_path)

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