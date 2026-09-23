import csv
import io
import json
import os

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for
)

from jinja2 import (
    ChoiceLoader,
    FileSystemLoader
)

from services.sentiment_service import (
    proses_sentimen
)

from utils.database import (
    ambil_riwayat,
    ambil_riwayat_by_id,
    ambil_semua_riwayat,
    ambil_statistik,
    ambil_statistik_bulanan,
    ambil_statistik_harian,
    ambil_statistik_tahunan,
    edit_riwayat as update_riwayat,
    hapus_riwayat,
    hitung_total_riwayat,
    simpan_ke_db
)

from utils.security import (
    verify_password
)


# =========================================================
# PATH PROJECT
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

ADMIN_DIR = os.path.join(
    BASE_DIR,
    "admin"
)

ADMIN_TEMPLATE_DIR = os.path.join(
    ADMIN_DIR,
    "templates"
)

METRICS_PATH = os.path.join(
    PROJECT_DIR,
    "models",
    "metrics.json"
)


# =========================================================
# KONFIGURASI APLIKASI
# =========================================================

app = Flask(__name__)

app.secret_key = (
    "kunci-rahasia-aplikasi"
)


# =========================================================
# TEMPLATE LOADER
# =========================================================
#
# Template utama:
# flask_app/templates
#
# Template admin:
# flask_app/admin/templates
#
# Component admin:
# flask_app/admin/components
#
# =========================================================

app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    FileSystemLoader(ADMIN_TEMPLATE_DIR),
    FileSystemLoader(ADMIN_DIR)
])


# =========================================================
# KONFIGURASI ADMIN
# =========================================================

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD_HASH = (
    "c976fb9fcc6d65c5d8a8efba43101fd4fba53682b4e224316acea7c5b063044e"
)


# =========================================================
# ASSET SB ADMIN
# =========================================================

@app.route(
    "/admin-static/<path:filename>"
)
def admin_static(filename):

    return send_from_directory(
        ADMIN_DIR,
        filename
    )


# =========================================================
# FUNGSI CEK LOGIN ADMIN
# =========================================================

def admin_sudah_login():

    return session.get(
        "admin_login",
        False
    )


# =========================================================
# INFORMASI MODEL
# =========================================================

def ambil_akurasi_model():

    try:

        with open(
            METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            metrics = json.load(
                file
            )

        return metrics.get(
            "accuracy",
            "N/A"
        )

    except FileNotFoundError:

        print(
            "metrics.json tidak ditemukan:"
        )

        print(
            METRICS_PATH
        )

        return "N/A"

    except json.JSONDecodeError:

        print(
            "Format metrics.json tidak valid."
        )

        return "N/A"


# =========================================================
# HALAMAN UTAMA USER
# =========================================================

@app.route("/")
def home():

    akurasi = (
        ambil_akurasi_model()
    )

    return render_template(
        "index.html",
        akurasi=akurasi
    )


# =========================================================
# ANALISIS SENTIMEN
# =========================================================

@app.route(
    "/analisis",
    methods=["POST"]
)
def analisis():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "Data tidak ditemukan."
        }), 400

    teks = data.get(
        "teks",
        ""
    )

    print(
        "Teks yang diterima:",
        teks
    )

    prediksi, confidence = (
        proses_sentimen(teks)
    )

    akurasi = (
        ambil_akurasi_model()
    )

    print(
        "Hasil prediksi:",
        prediksi
    )

    print(
        "Confidence:",
        confidence
    )

    return jsonify({
        "status": "success",
        "teks": teks,
        "sentimen": prediksi,
        "confidence": confidence,
        "akurasi": akurasi
    })


# =========================================================
# LOGIN ADMIN
# =========================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin_login():

    if admin_sudah_login():

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        password_benar = (
            verify_password(
                password,
                ADMIN_PASSWORD_HASH
            )
        )

        if (
            username == ADMIN_USERNAME
            and password_benar
        ):

            session[
                "admin_login"
            ] = True

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "admin_login.html",
            error=(
                "Username atau "
                "password salah."
            )
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# DASHBOARD ADMIN
# =========================================================

@app.route(
    "/admin/dashboard"
)
def dashboard():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    statistik = (
        ambil_statistik()
    )

    riwayat = ambil_riwayat(
        limit=20,
        offset=0
    )

    statistik_harian = (
        ambil_statistik_harian()
    )

    return render_template(
        "dashboard.html",
        statistik=statistik,
        riwayat=riwayat,
        statistik_harian=(
            statistik_harian
        )
    )


# =========================================================
# STATISTIK ADMIN
# =========================================================

@app.route(
    "/admin/statistik"
)
def statistik():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    data_statistik = (
        ambil_statistik()
    )

    statistik_harian = (
        ambil_statistik_harian()
    )

    statistik_bulanan = (
        ambil_statistik_bulanan()
    )

    statistik_tahunan = (
        ambil_statistik_tahunan()
    )

    return render_template(
        "statistik.html",
        statistik=data_statistik,
        statistik_harian=(
            statistik_harian
        ),
        statistik_bulanan=(
            statistik_bulanan
        ),
        statistik_tahunan=(
            statistik_tahunan
        )
    )


# =========================================================
# RIWAYAT KLASIFIKASI
# =========================================================

@app.route(
    "/admin/riwayat"
)
def riwayat():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    data_riwayat = (
        ambil_semua_riwayat()
    )

    return render_template(
        "riwayat.html",
        riwayat=data_riwayat
    )


# =========================================================
# TAMBAH RIWAYAT
# =========================================================

@app.route(
    "/admin/riwayat/tambah",
    methods=["GET", "POST"]
)
def tambah_riwayat():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    if request.method == "POST":

        teks_asli = request.form.get(
            "teks_asli",
            ""
        ).strip()

        teks_bersih = request.form.get(
            "teks_bersih",
            ""
        ).strip()

        klasifikasi = request.form.get(
            "klasifikasi",
            ""
        )

        confidence_input = (
            request.form.get(
                "confidence",
                ""
            ).strip()
        )

        if confidence_input:

            try:

                confidence = float(
                    confidence_input
                )

            except ValueError:

                confidence = None

        else:

            confidence = None

        simpan_ke_db(
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence
        )

        flash(
            "Data berhasil ditambahkan!",
            "success"
        )

        return redirect(
            url_for("riwayat")
        )

    return render_template(
        "riwayat_tambah.html"
    )


# =========================================================
# EDIT RIWAYAT
# =========================================================

@app.route(
    "/admin/riwayat/edit/<int:id_data>",
    methods=["GET", "POST"]
)
def edit_riwayat(id_data):

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    data = (
        ambil_riwayat_by_id(
            id_data
        )
    )

    if data is None:

        flash(
            "Data tidak ditemukan.",
            "danger"
        )

        return redirect(
            url_for("riwayat")
        )

    if request.method == "POST":

        teks_asli = request.form.get(
            "teks_asli",
            ""
        ).strip()

        teks_bersih = request.form.get(
            "teks_bersih",
            ""
        ).strip()

        klasifikasi = request.form.get(
            "klasifikasi",
            ""
        )

        confidence_input = (
            request.form.get(
                "confidence",
                ""
            ).strip()
        )

        if confidence_input:

            try:

                confidence = float(
                    confidence_input
                )

            except ValueError:

                confidence = None

        else:

            confidence = None

        update_riwayat(
            id_data,
            teks_asli,
            teks_bersih,
            klasifikasi,
            confidence
        )

        flash(
            "Data berhasil diperbarui!",
            "warning"
        )

        return redirect(
            url_for("riwayat")
        )

    return render_template(
        "riwayat_edit.html",
        data=data
    )


# =========================================================
# HAPUS SATU RIWAYAT
# =========================================================

@app.route(
    "/admin/riwayat/hapus/<int:id_data>",
    methods=["POST"]
)
def hapus_satu_riwayat(id_data):

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    hapus_riwayat(
        [id_data]
    )

    flash(
        "Data berhasil dihapus!",
        "danger"
    )

    return redirect(
        url_for("riwayat")
    )


# =========================================================
# HAPUS BANYAK RIWAYAT
# =========================================================

@app.route(
    "/admin/riwayat/hapus",
    methods=["POST"]
)
def hapus_banyak_riwayat():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    ids_data = request.form.getlist(
        "ids_data"
    )

    if ids_data:

        hapus_riwayat(
            ids_data
        )

        flash(
            "Data berhasil dihapus!",
            "danger"
        )

    return redirect(
        url_for("riwayat")
    )


# =========================================================
# DOWNLOAD RIWAYAT CSV
# =========================================================

@app.route(
    "/admin/riwayat/download"
)
def download_csv():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    data_riwayat = (
        ambil_semua_riwayat()
    )

    output = io.StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow([
        "ID",
        "Teks Asli",
        "Teks Bersih",
        "Sentimen",
        "Confidence",
        "Waktu"
    ])

    for data in data_riwayat:

        writer.writerow(
            data
        )

    output.seek(0)

    return send_file(
        io.BytesIO(
            output.getvalue().encode(
                "utf-8-sig"
            )
        ),
        mimetype="text/csv",
        as_attachment=True,
        download_name=(
            "riwayat_sentimen.csv"
        )
    )


# =========================================================
# MODEL SENTIMEN
# =========================================================

@app.route(
    "/admin/model"
)
def model_sentimen():

    if not admin_sudah_login():

        return redirect(
            url_for("admin_login")
        )

    akurasi = (
        ambil_akurasi_model()
    )

    return render_template(
        "model.html",
        akurasi=akurasi
    )


# =========================================================
# LOGOUT ADMIN
# =========================================================

@app.route(
    "/admin/logout",
    methods=["GET", "POST"]
)
def logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# MENJALANKAN APLIKASI
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )