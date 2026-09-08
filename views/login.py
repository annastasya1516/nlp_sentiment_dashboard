import streamlit as st
from utils.security import verify_password

# CEK JIKA SUDAH LOGIN
if st.session_state.get("login", False):
    st.switch_page(
        "views/admin.py"
    )

# HALAMAN LOGIN
st.title("🔐 Login Admin")
st.write(
    "Silakan login untuk mengakses dashboard admin."
)

# INPUT
username = st.text_input(
    "Username"
)
password = st.text_input(
    "Password",
    type="password"
)

# PROSES LOGIN
if st.button(
    "Login",
    type="primary",
    use_container_width=True
):
    if not username.strip() and not password.strip():
        st.warning(
            "Silakan isi Username dan Password terlebih dahulu!"
        )
    elif not username.strip():
        st.warning(
            "Silakan isi Username terlebih dahulu."
        )
    elif not password.strip():
        st.warning(
            "Silakan isi Password terlebih dahulu."
        )
    else:
        try:
            # Ambil data dari secrets.toml
            admin_user = st.secrets["admin_username"]
            admin_password_hash = st.secrets[
                "admin_password_hash"
            ]
            # Cek password dengan SHA-256
            password_cocok = verify_password(
                password,
                admin_password_hash
            )
            # Cek username dan password
            if (
                username.strip() == admin_user
                and password_cocok
            ):
                st.session_state["login"] = True
                # Langsung masuk ke /admin
                st.switch_page(
                    "views/admin.py"
                )
            else:
                st.error(
                    "Username atau Password salah!"
                )
        except KeyError:
            st.error(
                "Konfigurasi username atau "
                "password hash tidak ditemukan "
                "di secrets.toml."
            )