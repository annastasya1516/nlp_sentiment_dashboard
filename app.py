import streamlit as st


# KONFIGURASI APLIKASI
st.set_page_config(
    page_title="NLP Sentiment",
    layout="wide"
)


# SESSION LOGIN
if "login" not in st.session_state:
    st.session_state["login"] = False


# HALAMAN APLIKASI
home = st.Page(
    "views/home.py",
    title="Klasifikasi Sentimen",
    icon="💬",
    default=True
)

login = st.Page(
    "views/login.py",
    title="Login Admin",
    icon="🔐",
    url_path="login"
)

admin = st.Page(
    "views/admin.py",
    title="Dashboard Admin",
    icon="📊",
    url_path="admin"
)


# NAVIGASI
pg = st.navigation(
    [home, login, admin],
    position="hidden"
)

pg.run()