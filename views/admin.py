import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils.database import (
    ambil_data_db,
    ambil_semua_data_statistik,
    ambil_semua_data_csv,
    hapus_data_db,
    hitung_total_data
)
from services.metrics_service import (
    ambil_akurasi
)

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Dashboard Admin",
    page_icon="📊",
    layout="wide"
)

# CEK LOGIN
if not st.session_state.get("login", False):
    st.switch_page("views/login.py")

# SESSION STATE
if "halaman_history" not in st.session_state:
    st.session_state.halaman_history = 1

if "konfirmasi_hapus" not in st.session_state:
    st.session_state.konfirmasi_hapus = False

if "id_hapus" not in st.session_state:
    st.session_state.id_hapus = None

# KONFIGURASI PAGINATION
DATA_PER_HALAMAN = 20

# AUTO REFRESH DASHBOARD
st_autorefresh(
    interval=5000,
    key="refresh_admin"
)

# HEADER
col_title, col_logout = st.columns(
    [8, 1]
)
with col_title:
    st.title("📊 Dashboard Admin")
    st.markdown(
        "Monitoring seluruh aktivitas "
        "klasifikasi sentimen."
    )
with col_logout:
    if st.button(
        "Logout",
        use_container_width=True
    ):
        st.session_state["login"] = False
        st.switch_page(
            "views/login.py"
        )
        
# LOAD AKURASI MODEL
akurasi = ambil_akurasi()

# AMBIL DATA DATABASE
total_data = hitung_total_data()
df_statistik = ambil_semua_data_statistik()

# HITUNG TOTAL HALAMAN
total_halaman = max(
    1,
    (
        total_data
        + DATA_PER_HALAMAN
        - 1
    ) // DATA_PER_HALAMAN
)

# VALIDASI HALAMAN AKTIF
if st.session_state.halaman_history < 1:
    st.session_state.halaman_history = 1
if (
    st.session_state.halaman_history
    > total_halaman
):
    st.session_state.halaman_history = (
        total_halaman
    )

# HITUNG OFFSET DATA
offset = (
    st.session_state.halaman_history - 1
) * DATA_PER_HALAMAN

# AMBIL DATA HISTORY
df_history = ambil_data_db(
    limit=DATA_PER_HALAMAN,
    offset=offset
)

# HITUNG JUMLAH SENTIMEN
jumlah_positive = 0
jumlah_negative = 0
jumlah_neutral = 0
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

# METRIC DASHBOARD
col1, col2, col3, col4, col5 = st.columns(5)

# AKURASI MODEL
with col1:
    st.metric(
        label="Akurasi Model",
        value=akurasi
    )

# TOTAL DATA
with col2:
    st.metric(
        label="Total Data",
        value=total_data
    )

# POSITIVE
with col3:
    st.metric(
        label="Positive",
        value=jumlah_positive
    )

# NEGATIVE
with col4:
    st.metric(
        label="Negative",
        value=jumlah_negative
    )

# NEUTRAL
with col5:
    st.metric(
        label="Neutral",
        value=jumlah_neutral
    )
st.divider()

# WARNA SENTIMEN
warna = {
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral": "#FFC107"
}

# VISUALISASI KESELURUHAN SENTIMEN
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

# GRAFIK TREN INPUT
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

    # HARIAN
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

    # BULANAN
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
        
    # TAHUNAN
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

    # LINE CHART
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

    # BAR CHART

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
else:
    st.info(
        "Belum ada data untuk menampilkan grafik tren."
    )

st.divider()

# RIWAYAT DATA
col_history, col_analysis = st.columns(
    [2.2, 1.3]
)

# KOLOM KIRI
# RIWAYAT DATA
with col_history:

    st.subheader(
        f"📋 Riwayat Data "
        f"(Halaman "
        f"{st.session_state.halaman_history} "
        f"dari {total_halaman})"
    )

    # DOWNLOAD CSV

    df_csv = ambil_semua_data_csv()

    if not df_csv.empty:

        st.download_button(
            label="📥 Download Riwayat CSV",
            data=df_csv.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="riwayat_sentimen.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    # TABEL RIWAYAT

    if not df_history.empty:

        event = st.dataframe(
            df_history,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # PAGINATION
        
        if total_data > DATA_PER_HALAMAN:
            col_prev, col_info, col_next = st.columns(
                [1, 1.2, 1]
            )

            # SEBELUMNYA
            with col_prev:
                if st.button(
                    "← Sebelumnya",
                    disabled=(
                        st.session_state.halaman_history
                        == 1
                    ),
                    use_container_width=True
                ):

                    st.session_state.halaman_history -= 1
                    st.rerun()

            # INFORMASI HALAMAN
            with col_info:
                st.markdown(
                    f"""
                    <div style="
                        text-align: center;
                        padding-top: 8px;
                    ">
                        Halaman
                        <b>
                            {st.session_state.halaman_history}
                        </b>
                        dari
                        <b>
                            {total_halaman}
                        </b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # BERIKUTNYA
            with col_next:
                if st.button(
                    "Berikutnya →",
                    disabled=(
                        st.session_state.halaman_history
                        == total_halaman
                    ),
                    use_container_width=True
                ):
                    st.session_state.halaman_history += 1
                    st.rerun()
    else:
        st.info(
            "Belum ada data."
        )

# KOLOM KANAN
# ANALISIS KALIMAT

with col_analysis:
    st.subheader(
        "🔍 Analisis Kalimat"
    )

    # CEK DATA YANG DIPILIH
    if (
        not df_history.empty
        and event.selection.rows
    ):

        index = event.selection.rows[0]

        data = df_history.iloc[index]

        # DETAIL DATA
        
        st.write(
            f"**ID:** {data['id']}"
        )

        st.write(
            f"**Teks:** {data['teks_asli']}"
        )

        st.write(
            f"**Sentimen:** {data['klasifikasi']}"
        )

        st.write(
            f"**Waktu:** {data['waktu']}"
        )

        # TOMBOL HAPUS
        
        if st.button(
            "🗑️ Hapus Data",
            use_container_width=True
        ):
            st.session_state.konfirmasi_hapus = True
            st.session_state.id_hapus = int(
                data["id"]
            )
            st.rerun()
            
        # KONFIRMASI HAPUS
        if st.session_state.konfirmasi_hapus:
            st.warning(
                "⚠️ Yakin ingin menghapus data ini?"
            )
            col_hapus, col_batal = st.columns(2)

            # YA, HAPUS
            with col_hapus:
                if st.button(
                    "Ya, Hapus",
                    type="primary",
                    use_container_width=True
                ):
                    berhasil = hapus_data_db(
                        st.session_state.id_hapus
                    )

                    if berhasil:
                        st.success(
                            "Data berhasil dihapus."
                        )
                    else:
                        st.error(
                            "Data gagal dihapus."
                        )

                    st.session_state.konfirmasi_hapus = False
                    st.session_state.id_hapus = None
                    st.rerun()
                    
            # BATAL
            with col_batal:
                if st.button(
                    "Batal",
                    use_container_width=True
                ):
                    st.session_state.konfirmasi_hapus = False
                    st.session_state.id_hapus = None
                    st.rerun()
                    
        # CHART SENTIMEN
        chart = pd.DataFrame(
            {
                "sentimen": [
                    data["klasifikasi"]
                ],
                "jumlah": [1]
            }
        )

        fig = px.pie(
            chart,
            names="sentimen",
            values="jumlah",
            color="sentimen",
            color_discrete_map=warna,
            title="Analisis Sentimen"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info(
            "Klik salah satu baris pada tabel "
            "untuk melihat analisis."
        )