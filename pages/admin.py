import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import ambil_data_db

st.set_page_config(
    page_title="Dashboard Admin",
    layout="wide"
)

st.title("Dashboard Admin")
st.markdown("Monitoring seluruh aktivitas klasifikasi sentimen")

df_history = ambil_data_db()

jumlah_positive = len(df_history[df_history["klasifikasi"]=="positive"])
jumlah_negative = len(df_history[df_history["klasifikasi"]=="negative"])
jumlah_neutral = len(df_history[df_history["klasifikasi"]=="neutral"])

col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    st.metric("Akurasi Model", "87.46%")
with col2:
    st.metric("Total Data", len(df_history))
with col3:
    st.metric("Positive", jumlah_positive)
with col4:
    st.metric("Negative", jumlah_negative)
with col5:
    st.metric("Neutral", jumlah_neutral)
    
st.divider()

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

st.subheader("📈 Grafik Tren")
if not df_history.empty:
    df_history["waktu"] = pd.to_datetime(df_history["waktu"])

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
        
    st.subheader("📋 Riwayat Seluruh Data")
    st.dataframe(
        df_history,
        width="stretch",
        hide_index=True
    )
else:
    st.info("Data masih kosong")
