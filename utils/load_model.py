import pickle
import streamlit as st

@st.cache_resource
def load_model_assets():
    try:
        with open(
            "models/model_sentimen.pkl",
            "rb"
        ) as f_model:
            model = pickle.load(f_model)

        with open(
            "models/vectorizer_tfidf.pkl",
            "rb"
        ) as f_vec:
            vectorizer = pickle.load(f_vec)

        return model, vectorizer

    except FileNotFoundError as e:
        st.error(
            "File model tidak ditemukan. "
            "Silakan lakukan training model terlebih dahulu."
        )
        st.stop()

    except (pickle.UnpicklingError, EOFError) as e:
        st.error(
            "File model rusak atau tidak dapat dibaca. "
            "Silakan lakukan training model kembali."
        )
        st.stop()

    except Exception as e:
        st.error(
            f"Terjadi kesalahan saat memuat model: {e}"
        )
        st.stop()