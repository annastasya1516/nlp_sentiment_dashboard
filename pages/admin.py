import streamlit as st
import pandas as pd
import plotly.express as px
import json
from utils.database import ambil_data_db
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Dashboard Admin",
    layout="wide"
)

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
        "Silakan lakukan training model terlebih dahulu."
    )
    akurasi = "N/A"

except (json.JSONDecodeError, KeyError):
    st.warning(
        "File metrics.json tidak valid atau formatnya salah."
    )
    akurasi = "N/A"
    
# ga bisa kebuka dashboard admin kalo blom login
if "login" not in st.session_state:
    st.session_state["login"] = False
    
if not st.session_state["login"]:
    st.warning("Silahkan Login Terlebih Dahulu")
    st.switch_page("pages/login.py")

#auto refresh
st_autorefresh(
    interval=5000,
    key="refresh_admin"
)

col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("Dashboard Admin")
    st.markdown("Monitoring seluruh aktivitas klasifikasi sentimen")

# tombol logout
with col_logout:
    if st.button("Logout"):
        st.session_state["login"] = False
        st.switch_page("app.py")
    
df_history = ambil_data_db()

# total data
jumlah_positive = len(df_history[df_history["klasifikasi"]=="positive"])
jumlah_negative = len(df_history[df_history["klasifikasi"]=="negative"])
jumlah_neutral = len(df_history[df_history["klasifikasi"]=="neutral"])

col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    st.metric("Akurasi Model", akurasi)
with col2:
    st.metric("Total Data", len(df_history))
with col3:
    st.metric("Positive", jumlah_positive)
with col4:
    st.metric("Negative", jumlah_negative)
with col5:
    st.metric("Neutral", jumlah_neutral)
    
st.divider()

#visualisasi grafik seluruh data
st.subheader("📊 Visualisasi Keseluruhan Sentimen")   

if not df_history.empty:
    hitung_sentimen = (
        df_history["klasifikasi"].value_counts().reset_index()
    )
    hitung_sentimen.columns = ["sentimen", "jumlah"]
    warna = {
        "positive":"#4CAF50",
        "negative":"#F44336",
        "neutral":"#FFC107"
    }
    
    col_kiri, col_kanan = st.columns(2)
    with col_kiri:
        fig_pie = px.pie(
            hitung_sentimen,
            names="sentimen",
            values="jumlah",
            color="sentimen",
            color_discrete_map=warna,
            title="Distribusi Sentimen"
        )
        st.plotly_chart(
            fig_pie, width="stretch"
        )
        
    with col_kanan:
        fig_bar_sentimen = px.bar(
            hitung_sentimen,
            x="sentimen",
            y="jumlah",
            color="sentimen",
            color_discrete_map=warna,
            title="Jumlah Keseluruhan Sentimen"
        )
        st.plotly_chart(
            fig_bar_sentimen, width="stretch"
        )
else:
    st.info("Database masih kosong")
    
st.divider()

#visualisasi grafik kategori tren input(data yang masuk)
st.subheader("📈 Grafik Tren")
if not df_history.empty:
    df_history["waktu"] = pd.to_datetime(
        df_history["waktu"],
        format="mixed"
    )
    
    pilihan = st.radio(
        "periode",
        ["harian", "bulanan", "tahunan"],
        horizontal=True
    )
    if pilihan == "harian":
        df_grafik = (
            df_history.groupby(df_history["waktu"].dt.date).size().reset_index(name="Jumlah Input")
        )
    elif pilihan == "bulanan":
        df_grafik = (
            df_history.groupby(df_history["waktu"].dt.to_period("M")).size().reset_index(name="Jumlah Input")
        )
        df_grafik["waktu"] = df_grafik["waktu"].astype(str)
        
    else:
        df_grafik = (
            df_history.groupby(df_history["waktu"].dt.year).size().reset_index(name="Jumlah Input")
        )

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_line = px.line(
            df_grafik,
            x="waktu",
            y="Jumlah Input",
            title=f"Tren Input {pilihan}"
        )
        st.plotly_chart(fig_line, width="stretch")
        

    with col_chart2:
        fig_bar_tren = px.bar(
            df_grafik,
            x="waktu",
            y="Jumlah Input",
            title=f"Jumlah Input berdasarkan Tren {pilihan}"
        )
        st.plotly_chart(fig_bar_tren, width="stretch")
    
    st.divider()
    
    # tabel seluruh database 
    col_riwayat, col_analisis = st.columns(2)
    with col_riwayat:       
        st.subheader("📋 Riwayat Seluruh Data")
        event = st.dataframe(
            df_history,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
    # hasil analisis per kalimat
    with col_analisis:
        st.subheader("🔍 Analisis Kalimat")
        
        if event.selection.rows:
            index = event.selection.rows[0]
            data = df_history.iloc[index]
        
            chart = pd.DataFrame({
                "sentimen" : [data["klasifikasi"]],
                "jumlah" : [1]
            })
            
            fig = px.pie(
                chart,
                names="sentimen",
                values="jumlah",
                color="sentimen",
                color_discrete_map=warna,
                title="Analisis Sentimen Kalimat"
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Klik pada salah satu baris tabel")
else:
    st.info("Data masih kosong")
    

