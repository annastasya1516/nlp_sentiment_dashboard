import streamlit as st
import plotly.express as px
from services.metrics_service import ambil_akurasi
from controllers.sentiment_controller import analisis_sentimen
from components.voice_recorder import speech_to_text

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="NLP Sentiment",
    layout="wide"
)

# LOAD METRICS
akurasi = ambil_akurasi()

# SESSION STATE
if "input_version" not in st.session_state:
    st.session_state.input_version = 0
if "teks_terakhir" not in st.session_state:
    st.session_state.teks_terakhir = None
if "prediksi" not in st.session_state:
    st.session_state.prediksi = None
if "voice_processed" not in st.session_state:
    st.session_state.voice_processed = False

# LAYOUT
col_kiri, col_kanan = st.columns(2)

# KOLOM KIRI
with col_kiri:

    # JUDUL
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

    # VOICE TO TEXT
    st.subheader("🎙️ Voice to Text")
    hasil_suara = speech_to_text(
        key="voice_recorder"
    )
    if hasil_suara:
        teks_suara = hasil_suara.get(
            "text",
            ""
        )
        selesai = hasil_suara.get(
            "selesai",
            False
        )

        # SAAT MASIH MEREKA
        if not selesai:
            if teks_suara:
                st.session_state.input_teks = (
                    teks_suara
                )

            # Izinkan rekaman baru untuk diproses
            st.session_state.voice_processed = False

        # SAAT REKAMAN SELESAI
        elif selesai and teks_suara.strip():

            # Cegah prediksi berulang akibat
            # Streamlit melakukan rerun
            if not st.session_state.voice_processed:

                prediksi = analisis_sentimen(
                    teks_suara
                )

                # Simpan hasil prediksi
                st.session_state.prediksi = prediksi

                # Simpan teks yang dianalisis
                st.session_state.teks_terakhir = (
                    teks_suara
                )

                # Tandai voice sudah diproses
                st.session_state.voice_processed = True

                # Buat text area baru agar kosong
                st.session_state.input_version += 1

                # Jalankan ulang halaman
                st.rerun()

    # INPUT TEKS MANUAL
    st.subheader("Masukkan Kalimat")
    user_input = st.text_area(
        "Masukkan Kalimat",
        key=(
            f"input_teks_"
            f"{st.session_state.input_version}"
        ),
        placeholder=(
            "Contoh: Pelayanan disini "
            "sangat memuaskan"
        ),
        height=150
    )

    # TOMBOL ANALISIS
    if st.button(
        "Analisis Sentimen",
        type="primary",
        use_container_width=True
    ):
        # Cek input kosong
        if user_input.strip() == "":
            st.warning(
                "Silakan masukkan teks terlebih dahulu."
            )
        else:
            # Analisis sentimen
            prediksi = analisis_sentimen(
                user_input
            )
            # Simpan hasil prediksi
            st.session_state.prediksi = prediksi
            # Simpan teks yang dianalisis
            st.session_state.teks_terakhir = (
                user_input
            )
            # Buat text area baru agar kosong
            st.session_state.input_version += 1
            # Jalankan ulang halaman
            st.rerun()

# KOLOM KANAN
with col_kanan:
    st.subheader("📈 Hasil Analisis")
    prediksi = st.session_state.prediksi
    
    # JIKA SUDAH ADA HASIL
    if prediksi is not None:

        # HASIL KLASIFIKASI
        if prediksi == "positive":
            st.success(
                f"Hasil Klasifikasi: "
                f"{prediksi.upper()}"
            )
        elif prediksi == "negative":
            st.error(
                f"Hasil Klasifikasi: "
                f"{prediksi.upper()}"
            )
        elif prediksi == "neutral":
            st.warning(
                f"Hasil Klasifikasi: "
                f"{prediksi.upper()}"
            )
        elif prediksi == "invalid":
            st.warning(
                "⚠️ Teks tidak dapat dianalisis. "
                "Silakan masukkan kalimat yang lebih jelas."
            )

        # DATA GRAFIK
        chart = {
            "sentimen": [prediksi],
            "jumlah": [1]
        }
        
        # WARNA GRAFIK
        peta_warna = {
            "positive": "#4CAF50",
            "negative": "#F44336",
            "neutral": "#FFC107",
            "invalid": "#FF9999"
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

        # TEKS YANG TELAH DIANALISIS
        teks_terakhir = (
            st.session_state.teks_terakhir
        )
        if teks_terakhir:
            st.markdown(
                "### 📝 Teks yang Dianalisis"
            )
            st.info(
                teks_terakhir
            )

    # BELUM ADA HASIL
    else:

        st.info(
            "Hasil analisis akan muncul di sini."
        )