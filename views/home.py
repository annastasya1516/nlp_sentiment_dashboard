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

# AMBIL AKURASI MODEL
akurasi = ambil_akurasi()

# SESSION STATE
if "input_version" not in st.session_state:
    st.session_state.input_version = 0
if "teks_terakhir" not in st.session_state:
    st.session_state.teks_terakhir = None
if "prediksi" not in st.session_state:
    st.session_state.prediksi = None
if "last_voice_id" not in st.session_state:
    st.session_state.last_voice_id = None
    
col_kiri, col_kanan = st.columns(2)

# KOLOM KIRI
with col_kiri:
    st.title("Klasifikasi Sentimen")
    st.markdown(
        "Masukkan kalimat untuk mengetahui "
        "analisis sentimennya."
    )

    # AKURASI MODEL
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
        voice_id = hasil_suara.get(
            "recording_id"
        )

        # CEK REKAMAN SELESAI
        if (
            selesai
            and teks_suara.strip()
            and voice_id != st.session_state.last_voice_id
        ):

            # ANALISIS SENTIMEN
            prediksi = analisis_sentimen(
                teks_suara
            )
            
            # SIMPAN HASIL KE SESSION STATE
            st.session_state.prediksi = (
                prediksi
            )
            st.session_state.teks_terakhir = (
                teks_suara
            )
            st.session_state.last_voice_id = (
                voice_id
            )

            # SIAPKAN TEXT AREA BARU
            new_version = (
                st.session_state.input_version
                + 1
            )
            st.session_state[
                f"input_teks_{new_version}"
            ] = teks_suara
            st.session_state.input_version = (
                new_version
            )
            
            # REFRESH HALAMAN
            st.rerun()

    # INPUT KALIMAT
    st.subheader("Masukkan Kalimat")
    input_key = (
        f"input_teks_"
        f"{st.session_state.input_version}"
    )
    user_input = st.text_area(
        "Masukkan Kalimat",
        key=input_key,
        placeholder=(
            "Contoh: Pelayanan disini "
            "sangat memuaskan"
        ),
        height=150
    )

    # TOMBOL ANALISIS MANUAL
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
            prediksi = analisis_sentimen(
                user_input
            )
            st.session_state.prediksi = (
                prediksi
            )
            st.session_state.teks_terakhir = (
                user_input
            )

            # Buat text area baru agar
            # input lama dapat dikosongkan
            st.session_state.input_version += 1
            st.rerun()
            
# KOLOM KANAN
with col_kanan:
    st.subheader("📈 Hasil Analisis")
    prediksi = (
        st.session_state.prediksi
    )
    # BELUM ADA HASIL
    if prediksi is None:
        st.info(
            "Hasil analisis akan muncul di sini."
        )

    # SUDAH ADA HASIL
    else:
        # HASIL KLASIFIKASI
        if prediksi == "positive":
            st.success(
                "Hasil Klasifikasi: "
                f"{prediksi.upper()}"
            )
        elif prediksi == "negative":
            st.error(
                "Hasil Klasifikasi: "
                f"{prediksi.upper()}"
            )
        elif prediksi == "neutral":
            st.warning(
                "Hasil Klasifikasi: "
                f"{prediksi.upper()}"
            )
        elif prediksi == "invalid":
            st.warning(
                "⚠️ Teks tidak dapat dianalisis. "
                "Silakan masukkan kalimat yang lebih jelas."
            )

        # DATA CHART
        chart = {
            "sentimen": [prediksi],
            "jumlah": [1]
        }

        # WARNA CHART
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

        # TEKS YANG DIANALISIS
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