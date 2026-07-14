import streamlit as st
import pandas as pd
import pickle
import sqlite3
import re
import plotly.express as px

st.set_page_config(layout="wide", page_title="NLP Sentiment Dashboard")

@st.cache_resource
def load_model_assets():
    with open('model_sentimen.pkl', 'rb') as f_model:
        model = pickle.load(f_model)
    with open('vectorizer_tfidf.pkl', 'rb') as f_vec:
        vectorizer = pickle.load(f_vec)
        return model, vectorizer
    
model, vectorizer = load_model_assets()

def bersihkan_teks(teks):
    if not isinstance(teks, str):
        return ""
    teks = teks.lower()
    teks = re.sub(r'[^a-z0-9\s]','', teks)
    return teks.strip()

def simpan_ke_db(teks_asli, teks_bersih, klasifikasi):
    conn = sqlite3.connect('riwayat_sentimen.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO riwayat_sentimen (teks_asli, teks_bersih, klasifikasi) VALUES (?, ?, ?)', 
        (teks_asli, teks_bersih, klasifikasi)
    )
    conn.commit()
    conn.close()
    
def ambil_data_db():
    conn = sqlite3.connect('riwayat_sentimen.db')
    df = pd.read_sql_query("SELECT * FROM riwayat_sentimen ORDER BY id DESC", conn)
    conn.close()
    return df

df_history = ambil_data_db()

st.title("Dashboard Klasifikasi Sentimen NLP")
st.markdown("Aplikasi web interaktif klasifikasi sentimen otomatis")

col_metric1, col_metric2 = st.columns(2)
with col_metric1:
    st.metric(label="Model Akurasi Teruji (Logistic Regression)", value="87.46%", delta="konsisten")
with col_metric2:
    st.metric(label="Total data yang masuk", value=str(len(df_history)))
    
st.markdown("---")

col_kiri, col_kanan = st.columns([1, 1.2])
with col_kiri:
    st.subheader("📥 Input kalimat baru")
    user_input = st.text_area("Masukkan teks ulasan dibawah ini", placeholder="Masukkan text disini")
    
    if st.button("Analisis Sentiment", type="primary"):
        if user_input.strip() != "":
            teks_bersih = bersihkan_teks(user_input)
            teks_vektor = vectorizer.transform([teks_bersih])
            prediksi = model.predict(teks_vektor)[0]
            
            simpan_ke_db(user_input, teks_bersih, prediksi)
            
            if prediksi == 'positive' :
                st.success(f"Hasil Klasifikasi adalah: {prediksi.upper()}")
            elif prediksi == 'negative' :
                st.error(f"Hasil Klasifikasi adalah: {prediksi.upper()}")
            else:
                st.warning(f"Hasil Klasifikasi: {prediksi.upper()}")
            
            df_history = ambil_data_db()
        else:
             st.info("Silahkan masukkan teks terlebih dahulu") 
    st.markdown("📜 Riwayat Data Klasifikasi:")
    st.dataframe(df_history[['waktu', 'teks_asli', 'klasifikasi']].head(5), use_container_width=True)
    
    if not df_history.empty:
        hitung_sentimen = df_history['klasifikasi'].value_counts().reset_index()
        hitung_sentimen.columns = ['sentimen', 'jumlah']
    
        peta_warna = {
            'positive' : '#4CAF50',
            'negative' : '#F44336',
            'neutral' : '#FFC107'
        }
        urutan_kategori = {'sentimen' : ['positive', 'negative', 'neutral']}

        df_history['waktu'] = pd.to_datetime(df_history['waktu'])
        df_tren = df_history.groupby(df_history['waktu'].dt.date).size().reset_index(name='Jumlah Input')
        fig_line = px.line(df_tren, x='waktu', y='Jumlah Input', title='Tren aktivitas penginputan data baru')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Belum ada visualisasi, database masih kosong, silahkan input kalimat pertamamu!")
        
with col_kanan:
    st.subheader("📊 Visualisasi Interaktif")
    
    if not df_history.empty:
        fig_pie = px.pie(hitung_sentimen, values='jumlah', names='sentimen', 
                     title='Distribusi keseluruhan sentimen di database', color='sentimen', 
                     color_discrete_map=peta_warna, category_orders=urutan_kategori)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        fig_bar = px.bar(hitung_sentimen, x='sentimen', y='jumlah',
                        title='Jumlah data sentimen berdasarkan kategori', color='sentimen',
                        color_discrete_map=peta_warna, category_orders=urutan_kategori)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Belum ada visualisasi, database masih kosong, silahkan input kalimat pertamamu!")
    
    
    
        

  
            
                
            
    


    