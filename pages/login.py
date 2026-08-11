import streamlit as st


st.set_page_config(
    page_title="Login Admin",
    layout="centered"
)


st.title("🔐 Login Admin")
st.write("Silahkan login untuk mengakses dashboard admin")


username = st.text_input("Username")
password = st.text_input("Password", type="password")


if st.button("Login"):
    if username.strip() == "" and password.strip() == "":
        st.warning("Silahkan isi Username dan Password terlebih dahulu!")
    elif username.strip() == "":
        st.warning("Silahkan isi Username terlebih dahulu")
    elif password.strip() == "":
        st.warning("Silahkan isi Password terlebih dahulu")
    else:
        try:
            admin_user = st.secrets["admin_username"]
            admin_pass = st.secrets["admin_password"]

            if username == admin_user and password == admin_pass:
                st.session_state["login"] = True
                st.success("Login Berhasil!")
                st.switch_page("pages/admin.py")
            else:
                st.error("Username dan Password Salah!")

        except FileNotFoundError:
            st.error("Konfigurasi secrets.toml tidak ditemukan.")
