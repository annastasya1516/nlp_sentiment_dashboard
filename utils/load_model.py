import pickle
import streamlit as st

@st.cache_resource
def load_model_assets():
    with open('models/model_sentimen.pkl', 'rb') as f_model:
        model = pickle.load(f_model)
    with open('models/vectorizer_tfidf.pkl', 'rb') as f_vec:
        vectorizer = pickle.load(f_vec)
    return model, vectorizer