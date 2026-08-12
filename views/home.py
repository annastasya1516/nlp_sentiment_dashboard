import streamlit as st
import plotly.express as px
import json
from utils.preprocessing import bersihkan_teks
from utils.database import simpan_ke_db
from utils.load_model import load_model_assets
from components.voice_recorder import speech_to_text

st.set_page_config(
    page_title="NLP Sentiment",
    layout="wide"
)

# LOAD MODEL

model, vectorizer = load_model_assets()

# LOAD METRICS

try:
    with open(
        "models/metrics.json",
        "r",
        encoding="utf-8"
    ) as file:
        metrics = json.load(file)

    akurasi = metrics["accuracy"]

except FileNotFoundError:

    st.warning(
        "File metrics.json tidak ditemukan. "
        "Silakan jalankan training model terlebih dahulu."
    )

    akurasi = "N/A"

except (json.JSONDecodeError, KeyError):

    st.warning(
        "File metrics.json tidak valid atau formatnya salah."
    )

    akurasi = "N/A"

# SESSION STATE

if "input_teks" not in st.session_state:
    st.session_state.input_teks = ""

if "prediksi" not in st.session_state:
    st.session_state.prediksi = None

# LAYOUT

col_kiri, col_kanan = st.columns(2)

# KOLOM KIRI

with col_kiri:

    st.title("Klasifikasi Sentimen")

    st.markdown(
        "Masukkan kalimat untuk mengetahui "
        "analisis sentimennya."
    )

    st.metric(
        label="Model Akurasi (Logistic Regression)",
        value=akurasi
    )

    st.divider()
    
    # voice to text
    
    st.subheader("🎙️ Voice to Text")

    hasil_suara = speech_to_text(
        key="voice_recorder"
    )

    if hasil_suara:
        st.session_state.input_teks = hasil_suara

    # INPUT TEKS

    st.subheader("Masukkan Kalimat")

    user_input = st.text_area(
        "teks",
        key="input_teks",
        placeholder="Contoh: Pelayanan disini sangat memuaskan",
        height=150
    )

    # TOMBOL ANALISIS

    if st.button(
        "Analisis Sentimen",
        type="primary",
        use_container_width=True
    ):

        if user_input.strip() == "":
            
            st.warning(
                "Silakan masukkan teks terlebih dahulu."
            )

        else:

            # Bersihkan teks
            teks_bersih = bersihkan_teks(user_input)

            # Ubah teks menjadi TF-IDF
            teks_vektor = vectorizer.transform(
                [teks_bersih]
            )

            # Prediksi sentimen
            prediksi = model.predict(
                teks_vektor
            )[0]

            # Simpan hasil ke session
            st.session_state.prediksi = prediksi

            # Simpan ke database
            simpan_ke_db(
                user_input,
                teks_bersih,
                prediksi
            )

# KOLOM KANAN

with col_kanan:

    st.subheader("📈 Hasil Analisis")

    prediksi = st.session_state.prediksi

    if prediksi is not None:

        # HASIL SENTIMEN

        if prediksi == "positive":

            st.success(
                f"Hasil Klasifikasi: {prediksi.upper()}"
            )

        elif prediksi == "negative":

            st.error(
                f"Hasil Klasifikasi: {prediksi.upper()}"
            )

        else:

            st.warning(
                f"Hasil Klasifikasi: {prediksi.upper()}"
            )

        # DATA GRAFIK

        chart = {
            "sentimen": [prediksi],
            "jumlah": [1]
        }
        
        # WARNA SENTIMEN

        peta_warna = {
            "positive": "#4CAF50",
            "negative": "#F44336",
            "neutral": "#FFC107"
        }

        # PIE CHART

        fig = px.pie(
            chart,
            names="sentimen",
            values="jumlah",
            title="Hasil Analisis Sentimen",
            color="sentimen",
            color_discrete_map=peta_warna
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Hasil analisis akan muncul di sini."
        )