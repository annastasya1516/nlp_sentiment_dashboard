import json

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    Response
)

from services.sentiment_service import proses_sentimen
from utils.security import verify_password

from utils.database import (
    ambil_statistik,
    ambil_riwayat,
    hitung_total_riwayat,
    ambil_semua_riwayat,
    ambil_statistik_harian,
    ambil_statistik_bulanan,
    ambil_statistik_tahunan
)


# =========================================
# FLASK APPLICATION
# =========================================

app = Flask(__name__)

app.secret_key = "kunci-rahasia-aplikasi"


# =========================================
# ADMIN ACCOUNT
# =========================================

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD_HASH = "c976fb9fcc6d65c5d8a8efba43101fd4fba53682b4e224316acea7c5b063044e"


# =========================================
# LOAD MODEL ACCURACY
# =========================================

with open(
    "models/metrics.json",
    "r",
    encoding="utf-8"
) as file:

    metrics = json.load(file)


akurasi = metrics["accuracy"]

print("Akurasi model:", akurasi)


# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        akurasi=akurasi
    )


# =========================================
# ANALISIS SENTIMEN
# =========================================

@app.route("/analisis", methods=["POST"])
def analisis():

    data = request.get_json()

    teks = data.get("teks", "")

    print("Teks yang diterima:", teks)

    prediksi = proses_sentimen(teks)

    print("Hasil prediksi:", prediksi)

    return jsonify({
        "status": "success",
        "teks": teks,
        "sentimen": prediksi,
        "akurasi": akurasi
    })


# =========================================
# ADMIN LOGIN
# =========================================

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        print("Username:", username)

        if username == ADMIN_USERNAME and verify_password(password, ADMIN_PASSWORD_HASH):
            session["admin_login"] = True
            return redirect("/admin/dashboard")

        return render_template(
            "admin_login.html",
            error="Username atau password salah."
        )

    return render_template("admin_login.html")

# =========================================
# ADMIN DASHBOARD
# =========================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin_login"):
        return redirect("/admin")

    statistik = ambil_statistik()

    riwayat = ambil_riwayat()

    return render_template(
        "admin_dashboard.html",
        statistik=statistik,
        riwayat=riwayat
    )


# =========================================
# ADMIN STATISTIK
# =========================================

@app.route("/admin/statistik")
def admin_statistik():

    if not session.get("admin_login"):
        return redirect("/admin")

    # Statistik keseluruhan
    statistik = ambil_statistik()

    # Statistik harian
    statistik_harian = ambil_statistik_harian()

    # Statistik bulanan
    statistik_bulanan = ambil_statistik_bulanan()

    # Statistik tahunan
    statistik_tahunan = ambil_statistik_tahunan()

    return render_template(
        "admin_statistik.html",
        statistik=statistik,
        statistik_harian=statistik_harian,
        statistik_bulanan=statistik_bulanan,
        statistik_tahunan=statistik_tahunan
    )


# =========================================
# ADMIN RIWAYAT
# =========================================

@app.route("/admin/riwayat")
def admin_riwayat():

    if not session.get("admin_login"):
        return redirect("/admin")

    halaman = request.args.get(
        "halaman",
        1,
        type=int
    )

    data_per_halaman = 20

    offset = (
        halaman - 1
    ) * data_per_halaman

    riwayat = ambil_riwayat(
        limit=data_per_halaman,
        offset=offset
    )

    total_data = hitung_total_riwayat()

    total_halaman = (
        (total_data + data_per_halaman - 1)
        // data_per_halaman
    )

    return render_template(
        "admin_riwayat.html",
        riwayat=riwayat,
        halaman=halaman,
        total_halaman=total_halaman
    )


# =========================================
# DOWNLOAD CSV
# =========================================

@app.route("/admin/riwayat/download")
def download_csv():

    if not session.get("admin_login"):
        return redirect("/admin")

    riwayat = ambil_semua_riwayat()

    csv_data = (
        "ID,Teks Asli,Teks Bersih,Sentimen,Waktu\n"
    )

    for data in riwayat:

        csv_data += (
            f'"{data[0]}",'
            f'"{data[1]}",'
            f'"{data[2]}",'
            f'"{data[3]}",'
            f'"{data[4]}"\n'
        )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=riwayat_sentimen.csv"
        }
    )


# =========================================
# ADMIN MODEL
# =========================================

@app.route("/admin/model")
def admin_model():

    if not session.get("admin_login"):
        return redirect("/admin")

    return render_template(
        "admin_model.html",
        akurasi=akurasi
    )


# =========================================
# ADMIN LOGOUT
# =========================================

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_login", None)

    return render_template(
        "admin_login.html",
        success="Anda berhasil logout."
    )

# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )