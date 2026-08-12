import streamlit as st
import bcrypt


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
            admin_password_hash = st.secrets["admin_password_hash"]

            password_cocok = bcrypt.checkpw(
                password.encode("utf-8"),
                admin_password_hash.encode("utf-8")
            )

            if username == admin_user and password_cocok:
                st.session_state["login"] = True
                st.success("Login Berhasil!")
                st.switch_page("pages/admin.py")
            else:
                st.error("Username dan Password Salah!")

        except KeyError:
            st.error(
                "Konfigurasi username atau password hash "
                "tidak ditemukan di secrets.toml."
            )

        except FileNotFoundError:
            st.error(
                "Konfigurasi secrets.toml tidak ditemukan."
            )