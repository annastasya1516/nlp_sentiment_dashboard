import streamlit as st
import pandas as pd
import plotly.express as px
import json
from utils.database import (
    ambil_data_db,
    hitung_total_data,
    ambil_semua_data_statistik
)
from streamlit_autorefresh import st_autorefresh

# CEK LOGIN
if not st.session_state.get("login", False):
    st.switch_page(
        "views/login.py"
    )

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
        "Silakan lakukan training model terlebih dahulu."
    )
    akurasi = "N/A"
except (json.JSONDecodeError, KeyError):
    st.warning(
        "File metrics.json tidak valid atau formatnya salah."
    )
    akurasi = "N/A"

# AUTO REFRESH
st_autorefresh(
    interval=5000,
    key="refresh_admin"
)

# HEADER
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("📊 Dashboard Admin")
    st.markdown(
        "Monitoring seluruh aktivitas klasifikasi sentimen"
    )

# LOGOUT
with col_logout:
    if st.button(
        "Logout",
        use_container_width=True
    ):
        st.session_state["login"] = False
        
        # Kembali ke /login
        st.switch_page(
            "views/login.py"
        )
        
# AMBIL DATA
df_history = ambil_data_db(limit=20)
total_data = hitung_total_data()
df_statistik = (ambil_semua_data_statistik())

# HITUNG SENTIMEN
if not df_statistik.empty:
    jumlah_positive = len(
        df_statistik[
            df_statistik["klasifikasi"]
            == "positive"
        ]
    )
    jumlah_negative = len(
        df_statistik[
            df_statistik["klasifikasi"]
            == "negative"
        ]
    )
    jumlah_neutral = len(
        df_statistik[
            df_statistik["klasifikasi"]
            == "neutral"
        ]
    )
else:
    jumlah_positive = 0
    jumlah_negative = 0
    jumlah_neutral = 0

# METRIC
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        "Akurasi Model",
        akurasi
    )
with col2:
    st.metric(
        "Total Data",
        total_data
    )
with col3:
    st.metric(
        "Positive",
        jumlah_positive
    )
with col4:
    st.metric(
        "Negative",
        jumlah_negative
    )
with col5:
    st.metric(
        "Neutral",
        jumlah_neutral
    )
st.divider()

# WARNA
warna = {
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral": "#FFC107"
}

# DISTRIBUSI SENTIMEN
st.subheader(
    "📊 Visualisasi Keseluruhan Sentimen"
)

if not df_statistik.empty:
    hitung_sentimen = (
        df_statistik["klasifikasi"]
        .value_counts()
        .reset_index()
    )
    hitung_sentimen.columns = [
        "sentimen",
        "jumlah"
    ]
    col_kiri, col_kanan = st.columns(2)
    
    # PIE CHART
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
            fig_pie,
            use_container_width=True
        )
        
    # BAR CHART
    with col_kanan:
        fig_bar = px.bar(
            hitung_sentimen,
            x="sentimen",
            y="jumlah",
            color="sentimen",
            color_discrete_map=warna,
            title="Jumlah Keseluruhan Sentimen"
        )
        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )
else:
    st.info(
        "Database masih kosong."
    )
st.divider()

# GRAFIK TREN
st.subheader(
    "📈 Grafik Tren Input"
)
if not df_statistik.empty:
    df_statistik["waktu"] = pd.to_datetime(
        df_statistik["waktu"],
        format="mixed"
    )
    pilihan = st.radio(
        "Periode",
        [
            "harian",
            "bulanan",
            "tahunan"
        ],
        horizontal=True
    )
    if pilihan == "harian":
        df_grafik = (
            df_statistik
            .groupby(
                df_statistik["waktu"].dt.date
            )
            .size()
            .reset_index(
                name="Jumlah Input"
            )
        )
    elif pilihan == "bulanan":
        df_grafik = (
            df_statistik
            .groupby(
                df_statistik["waktu"]
                .dt.to_period("M")
            )
            .size()
            .reset_index(
                name="Jumlah Input"
            )
        )
        df_grafik["waktu"] = (
            df_grafik["waktu"]
            .astype(str)
        )
    else:
        df_grafik = (
            df_statistik
            .groupby(
                df_statistik["waktu"].dt.year
            )
            .size()
            .reset_index(
                name="Jumlah Input"
            )
        )
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_line = px.line(
            df_grafik,
            x="waktu",
            y="Jumlah Input",
            title=f"Tren Input {pilihan}"
        )
        st.plotly_chart(
            fig_line,
            use_container_width=True
        )
    with col_chart2:
        fig_bar_tren = px.bar(
            df_grafik,
            x="waktu",
            y="Jumlah Input",
            title=f"Jumlah Input {pilihan}"
        )
        st.plotly_chart(
            fig_bar_tren,
            use_container_width=True
        )
st.divider()

# RIWAYAT DATA
st.subheader(
    "📋 20 Data Terbaru"
)
if not df_history.empty:
    event = st.dataframe(
        df_history,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )
    
    # ANALISIS KALIM
    st.subheader(
        "🔍 Analisis Kalimat"
    )
    if event.selection.rows:
        index = event.selection.rows[0]
        data = df_history.iloc[index]
        chart = pd.DataFrame({
            "sentimen": [
                data["klasifikasi"]
            ],
            "jumlah": [1]
        })
        fig = px.pie(
            chart,
            names="sentimen",
            values="jumlah",
            color="sentimen",
            color_discrete_map=warna,
            title="Analisis Sentimen Kalimat"
        )
        st.plotly_chart(
            fig,
            use_container_width=True
        )
    else:
        st.info(
            "Klik salah satu baris untuk "
            "melihat analisis."
        )
else:
    st.info(
        "Belum ada data."
    )