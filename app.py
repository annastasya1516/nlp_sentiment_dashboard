import streamlit as st
import plotly.express as px
from utils.preprocessing import bersihkan_teks
from utils.database import simpan_ke_db
from utils.load_model import load_model_assets
from streamlit_mic_recorder import speech_to_text

st.set_page_config(
        page_title="NLP Sentiment",
        layout="wide"
    )

model, vectorizer = load_model_assets()

prediksi = None

col_kiri, col_kanan = st.columns(2)
with col_kiri:
    st.title("Klasifikasi Sentimen")
    st.markdown("Masukkan kalimat untuk mengetahui analisis sentimennya")

    st.metric(
        label="Model Akurasi (Logistic Regression)",
        value="87.46%"
    )

    st.divider()
    
    # voice to text
    st.subheader("Voice to Text")
    if "input_teks" not in st.session_state:
        st.session_state.input_teks = ""
        
    hasil_suara = speech_to_text(
        language="id",
        use_container_width=True,
        just_once=True,
        key="STT"
    )
    if hasil_suara is not None:
        st.session_state.input_teks = hasil_suara
    
    user_input = st.text_area(
        "Masukkan kalimat", 
        key="input_teks",
        placeholder="Contoh: Pelayanan disini sangat memuaskan"
    )
        
    if st.button("Analisis Sentimen", type="primary"):
        
        with col_kanan:
            if user_input.strip() != "":
                teks_bersih = bersihkan_teks(user_input)
                teks_vektor = vectorizer.transform([teks_bersih])
                prediksi = model.predict(teks_vektor)[0]
                    
                simpan_ke_db(user_input, teks_bersih, prediksi)
            else:
                st.info("Silahkan masukkan teks terlebih dahulu")

with col_kanan:
    st.subheader("📈 Hasil Ananlisis")    
    if prediksi is not None:
        if prediksi == 'positive' :
            st.success(f"Hasil Klasifikasi adalah: {prediksi.upper()}")
        elif prediksi == 'negative' :
            st.error(f"Hasil Klasifikasi adalah: {prediksi.upper()}")
        else:
            st.warning(f"Hasil Klasifikasi: {prediksi.upper()}")
                    
        chart={
            "sentimen": [prediksi],
            "jumlah": [1]
        }
        peta_warna = {
            'positive' : '#4CAF50',
            'negative' : '#F44336',
            'neutral' : '#FFC107'
        }

        fig = px.pie(
            chart,
            names="sentimen",
            values="jumlah",
            title="Hasil Analisis Sentimen",
            color="sentimen",
            color_discrete_map=peta_warna
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Hasil analisis akan muncul disini")
        
    
    

