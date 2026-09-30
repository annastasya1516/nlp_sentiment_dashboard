import csv
import io
import json
import os
import pickle

import pandas as pd
from dotenv import load_dotenv
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
from jinja2 import ChoiceLoader, FileSystemLoader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from werkzeug.utils import secure_filename
from services.dataset_service import proses_file_dataset
from services.sentiment_service import proses_sentimen
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
    simpan_ke_db
)
from utils.preprocessing import bersihkan_teks
from utils.security import verify_password


# =========================
# Environment
# =========================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY belum diatur di file .env"
    )

if not ADMIN_USERNAME:
    raise RuntimeError(
        "ADMIN_USERNAME belum diatur di file .env"
    )

if not ADMIN_PASSWORD_HASH:
    raise RuntimeError(
        "ADMIN_PASSWORD_HASH belum diatur di file .env"
    )


# =========================
# Path
# =========================

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

DATASET_DIR = os.path.join(
    PROJECT_DIR,
    "datasets"
)

MODEL_DIR = os.path.join(
    PROJECT_DIR,
    "models"
)

METRICS_PATH = os.path.join(
    MODEL_DIR,
    "metrics.json"
)


# =========================
# App
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    FileSystemLoader(ADMIN_TEMPLATE_DIR),
    FileSystemLoader(ADMIN_DIR)
])


# =========================
# Helper
# =========================

def admin_sudah_login():
    return session.get(
        "admin_login",
        False
    )


def ambil_akurasi_model():

    try:
        with open(
            METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            metrics = json.load(file)

        return metrics.get(
            "accuracy",
            "N/A"
        )

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):
        return "N/A"


def ambil_daftar_dataset():

    daftar_dataset = []

    if not os.path.exists(DATASET_DIR):
        return daftar_dataset

    for nama_file in os.listdir(DATASET_DIR):

        file_path = os.path.join(
            DATASET_DIR,
            nama_file
        )

        if not os.path.isfile(file_path):
            continue

        ekstensi = os.path.splitext(
            nama_file
        )[1].lower()

        if ekstensi not in [
            ".csv",
            ".tsv"
        ]:
            continue

        daftar_dataset.append({
            "nama": nama_file,
            "ekstensi": ekstensi.replace(
                ".",
                ""
            ).upper()
        })

    daftar_dataset.sort(
        key=lambda data: data["nama"].lower()
    )

    return daftar_dataset


def redirect_ke_model():
    return redirect(
        url_for("model_sentimen")
    )


def redirect_ke_dataset():
    return redirect(
        url_for("dataset")
    )


# =========================
# Security
# =========================

@app.after_request
def tambahkan_header_keamanan(response):

    response.headers["Cache-Control"] = (
        "no-store, no-cache, "
        "must-revalidate, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================
# Admin Static
# =========================

@app.route(
    "/admin-static/<path:filename>"
)
def admin_static(filename):

    return send_from_directory(
        ADMIN_DIR,
        filename
    )


# =========================
# User
# =========================

@app.route("/")
def home():

    return render_template(
        "index.html",
        akurasi=ambil_akurasi_model()
    )


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

    prediksi, confidence = proses_sentimen(
        teks
    )

    akurasi = ambil_akurasi_model()

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


# =========================
# Login
# =========================

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

        password_benar = verify_password(
            password,
            ADMIN_PASSWORD_HASH
        )

        if (
            username == ADMIN_USERNAME
            and password_benar
        ):

            session["admin_login"] = True

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "admin_login.html",
            error="Username atau password salah."
        )

    return render_template(
        "admin_login.html"
    )


# =========================
# Dashboard
# =========================

@app.route(
    "/admin/dashboard"
)
def dashboard():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    return render_template(
        "dashboard.html",
        statistik=ambil_statistik(),
        riwayat=ambil_riwayat(
            limit=20,
            offset=0
        ),
        statistik_harian=ambil_statistik_harian()
    )


# =========================
# Statistik
# =========================

@app.route(
    "/admin/statistik"
)
def statistik():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    return render_template(
        "statistik.html",
        statistik=ambil_statistik(),
        statistik_harian=ambil_statistik_harian(),
        statistik_bulanan=ambil_statistik_bulanan(),
        statistik_tahunan=ambil_statistik_tahunan()
    )


# =========================
# Riwayat
# =========================

@app.route(
    "/admin/riwayat"
)
def riwayat():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    return render_template(
        "riwayat.html",
        riwayat=ambil_semua_riwayat()
    )


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

        confidence_input = request.form.get(
            "confidence",
            ""
        ).strip()

        try:
            confidence = (
                float(confidence_input)
                if confidence_input
                else None
            )
        except ValueError:
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


@app.route(
    "/admin/riwayat/edit/<int:id_data>",
    methods=["GET", "POST"]
)
def edit_riwayat(id_data):

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    data = ambil_riwayat_by_id(
        id_data
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

        confidence_input = request.form.get(
            "confidence",
            ""
        ).strip()

        try:
            confidence = (
                float(confidence_input)
                if confidence_input
                else None
            )
        except ValueError:
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


# =========================
# Download Riwayat
# =========================

@app.route(
    "/admin/riwayat/download"
)
def download_csv():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    data_riwayat = ambil_semua_riwayat()

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

    writer.writerows(
        data_riwayat
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
        download_name="riwayat_sentimen.csv"
    )


# =========================
# Model
# =========================

@app.route(
    "/admin/model"
)
def model_sentimen():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    return render_template(
        "model.html",
        akurasi=ambil_akurasi_model(),
        daftar_dataset=ambil_daftar_dataset()
    )


# =========================
# Dataset
# =========================

@app.route(
    "/admin/dataset"
)
def dataset():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    return render_template(
        "dataset.html",
        daftar_dataset=ambil_daftar_dataset()
    )


@app.route(
    "/admin/dataset/<nama_file>"
)
def detail_dataset(nama_file):

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    nama_file = secure_filename(
        nama_file
    )

    ekstensi = os.path.splitext(
        nama_file
    )[1].lower()

    if ekstensi not in [
        ".csv",
        ".tsv"
    ]:

        flash(
            "File dataset tidak valid.",
            "danger"
        )

        return redirect_ke_dataset()

    file_path = os.path.join(
        DATASET_DIR,
        nama_file
    )

    if not os.path.isfile(file_path):

        flash(
            "Dataset tidak ditemukan.",
            "danger"
        )

        return redirect_ke_dataset()

    try:

        separator = (
            "\t"
            if ekstensi == ".tsv"
            else ","
        )

        data = pd.read_csv(
            file_path,
            sep=separator,
            dtype=str,
            keep_default_na=False
        )

        kolom = list(
            data.columns
        )

        return render_template(
            "dataset_detail.html",
            nama_file=nama_file,
            ekstensi=ekstensi.replace(
                ".",
                ""
            ).upper(),
            jumlah_baris=len(data),
            jumlah_kolom=len(kolom),
            kolom=kolom,
            data=data.to_dict(
                orient="records"
            )
        )

    except Exception as error:

        flash(
            f"Dataset gagal dibaca: {error}",
            "danger"
        )

        return redirect_ke_dataset()


# =========================
# Upload Dataset
# =========================

@app.route(
    "/admin/model/upload-dataset",
    methods=["POST"]
)
def upload_dataset():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    file = request.files.get(
        "dataset"
    )

    if not file or not file.filename:

        flash(
            "Silakan pilih file dataset.",
            "danger"
        )

        return redirect_ke_dataset()

    nama_file = secure_filename(
        file.filename
    )

    ekstensi = os.path.splitext(
        nama_file
    )[1].lower()

    if ekstensi not in [
        ".csv",
        ".tsv"
    ]:

        flash(
            "Format file harus CSV atau TSV.",
            "danger"
        )

        return redirect_ke_dataset()

    os.makedirs(
        DATASET_DIR,
        exist_ok=True
    )

    file_path = os.path.join(
        DATASET_DIR,
        nama_file
    )

    file.save(
        file_path
    )

    try:

        hasil = proses_file_dataset(
            file_path,
            ekstensi
        )

        hasil.to_csv(
            file_path,
            sep="\t" if ekstensi == ".tsv" else ",",
            index=False
        )

        flash(
            f"Dataset {nama_file} berhasil diproses. "
            f"{len(hasil)} data siap digunakan.",
            "success"
        )

    except Exception as error:

        if os.path.exists(file_path):
            os.remove(file_path)

        flash(
            f"Dataset gagal diproses: {error}",
            "danger"
        )

    return redirect_ke_dataset()

    return redirect_ke_dataset()


# =========================
# Delete Dataset
# =========================

@app.route(
    "/admin/model/delete-dataset/<nama_file>",
    methods=["POST"]
)
def delete_dataset(nama_file):

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    nama_file = secure_filename(
        nama_file
    )

    ekstensi = os.path.splitext(
        nama_file
    )[1].lower()

    if ekstensi not in [
        ".csv",
        ".tsv"
    ]:

        flash(
            "File dataset tidak valid.",
            "danger"
        )

        return redirect_ke_dataset()

    file_path = os.path.join(
        DATASET_DIR,
        nama_file
    )

    if not os.path.isfile(file_path):

        flash(
            "Dataset tidak ditemukan.",
            "danger"
        )

        return redirect_ke_dataset()

    try:

        os.remove(
            file_path
        )

        flash(
            f"Dataset {nama_file} berhasil dihapus.",
            "danger"
        )

    except OSError:

        flash(
            f"Dataset {nama_file} gagal dihapus.",
            "danger"
        )

    return redirect_ke_dataset()


# =========================
# Training
# =========================

@app.route(
    "/admin/model/train",
    methods=["POST"]
)
def train_model():

    if not admin_sudah_login():
        return redirect(
            url_for("admin_login")
        )

    training_dataset = request.form.get(
        "training_dataset",
        ""
    ).strip()

    validation_dataset = request.form.get(
        "validation_dataset",
        ""
    ).strip()

    if (
        not training_dataset
        or not validation_dataset
    ):

        flash(
            "Training dan validation dataset harus dipilih.",
            "danger"
        )

        return redirect_ke_model()

    training_dataset = secure_filename(
        training_dataset
    )

    validation_dataset = secure_filename(
        validation_dataset
    )

    ekstensi_training = os.path.splitext(
        training_dataset
    )[1].lower()

    ekstensi_validation = os.path.splitext(
        validation_dataset
    )[1].lower()

    if ekstensi_training not in [
        ".csv",
        ".tsv"
    ]:

        flash(
            "Format training dataset harus CSV atau TSV.",
            "danger"
        )

        return redirect_ke_model()

    if ekstensi_validation not in [
        ".csv",
        ".tsv"
    ]:

        flash(
            "Format validation dataset harus CSV atau TSV.",
            "danger"
        )

        return redirect_ke_model()

    training_path = os.path.join(
        DATASET_DIR,
        training_dataset
    )

    validation_path = os.path.join(
        DATASET_DIR,
        validation_dataset
    )

    if not os.path.isfile(
        training_path
    ):

        flash(
            "Training dataset tidak ditemukan.",
            "danger"
        )

        return redirect_ke_model()

    if not os.path.isfile(
        validation_path
    ):

        flash(
            "Validation dataset tidak ditemukan.",
            "danger"
        )

        return redirect_ke_model()

    try:

        separator_training = (
            "\t"
            if ekstensi_training == ".tsv"
            else ","
        )

        separator_validation = (
            "\t"
            if ekstensi_validation == ".tsv"
            else ","
        )

        df_train = pd.read_csv(
            training_path,
            sep=separator_training
        )

        df_valid = pd.read_csv(
            validation_path,
            sep=separator_validation
        )

        kolom_wajib = [
            "text",
            "sentiment"
        ]

        for kolom in kolom_wajib:

            if kolom not in df_train.columns:

                flash(
                    f"Kolom '{kolom}' tidak ditemukan "
                    "pada training dataset.",
                    "danger"
                )

                return redirect_ke_model()

            if kolom not in df_valid.columns:

                flash(
                    f"Kolom '{kolom}' tidak ditemukan "
                    "pada validation dataset.",
                    "danger"
                )

                return redirect_ke_model()

        df_train = df_train[
            ["text", "sentiment"]
        ].dropna()

        df_valid = df_valid[
            ["text", "sentiment"]
        ].dropna()

        if df_train.empty:

            flash(
                "Training dataset tidak memiliki data.",
                "danger"
            )

            return redirect_ke_model()

        if df_valid.empty:

            flash(
                "Validation dataset tidak memiliki data.",
                "danger"
            )

            return redirect_ke_model()

        df_train["text_clean"] = (
            df_train["text"]
            .astype(str)
            .apply(bersihkan_teks)
        )

        df_valid["text_clean"] = (
            df_valid["text"]
            .astype(str)
            .apply(bersihkan_teks)
        )

        vectorizer = TfidfVectorizer()

        X_train = vectorizer.fit_transform(
            df_train["text_clean"]
        )

        X_valid = vectorizer.transform(
            df_valid["text_clean"]
        )

        y_train = df_train["sentiment"]
        y_valid = df_valid["sentiment"]

        model = LogisticRegression(
            max_iter=1000
        )

        model.fit(
            X_train,
            y_train
        )

        prediksi = model.predict(
            X_valid
        )

        accuracy = accuracy_score(
            y_valid,
            prediksi
        )

        accuracy_percent = (
            f"{accuracy * 100:.2f}%"
        )

        os.makedirs(
            MODEL_DIR,
            exist_ok=True
        )

        with open(
            os.path.join(
                MODEL_DIR,
                "model_sentimen.pkl"
            ),
            "wb"
        ) as file:

            pickle.dump(
                model,
                file
            )

        with open(
            os.path.join(
                MODEL_DIR,
                "vectorizer_tfidf.pkl"
            ),
            "wb"
        ) as file:

            pickle.dump(
                vectorizer,
                file
            )

        with open(
            METRICS_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "accuracy": accuracy_percent
                },
                file,
                indent=4
            )

        flash(
            "Training model berhasil. "
            f"Akurasi validation: {accuracy_percent}",
            "success"
        )

    except Exception as error:

        print(
            "Training error:",
            error
        )

        flash(
            f"Training gagal: {error}",
            "danger"
        )

    return redirect_ke_model()


# =========================
# Logout
# =========================

@app.route(
    "/admin/logout",
    methods=["GET", "POST"]
)
def logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================
# Run
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )