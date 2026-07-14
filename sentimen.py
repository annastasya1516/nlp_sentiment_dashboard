import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# baca dataset
try:
    df_train = pd.read_csv('train_preprocess_ori.tsv', sep='\t')
    df_valid = pd.read_csv('valid_preprocess.tsv', sep='\t')
    print(f"Berhasil memuat data! Train: {len(df_train)} baris, Valid: {len(df_valid)} baris")
except FileNotFoundError:
    print("File tidak di temukan!, pastikan file berada pada folder yang sama")

print("\nContoh data train:")
print(df_valid.head(5))

# bersihin teks
def bersihkan_teks(teks):
    if not isinstance(teks, str):
        return ""
    teks = teks.lower()
    teks = re.sub(r'a-z0-9\s', '', teks)
    return teks.strip()

print("sedang membersihkan data train...")
df_train['text_clean'] = df_train['text'].apply(bersihkan_teks)

print("sedang membersihkan data valid...")
df_valid['text_clean'] = df_valid['text'].apply(bersihkan_teks)

print("proses pembersihan selesai!")

# ubah teks jadi numerik dengan TF-IDF
vectorizer = TfidfVectorizer()
X_train = vectorizer.fit_transform(df_train['text_clean'])
X_valid = vectorizer.transform(df_valid['text_clean'])

y_train = df_train['sentiment']
y_valid = df_valid['sentiment']

# train model dengan linear regression
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)
print("Model berhasil di latih!")

# prediksi akurasi df_valid
y_pred = model.predict(X_valid)
akurasi = accuracy_score(y_valid, y_pred)
print(f"Akurasi model pada data validasi: {akurasi * 100:.2f}%")

print("\nLaporan Klasifikasi detail:")
print(classification_report(y_valid, y_pred))

# test 
try:
    df_test = pd.read_csv('test_preprocess_masked_label.tsv', sep='\t')
    print(f"Berhasil memuat dataset test! Test : {len(df_test)} baris")

    df_test['text_clean'] = df_test['text'].apply(bersihkan_teks)

    X_test = vectorizer.transform(df_test['text_clean'])

    df_test['sentiment_prediction'] = model.predict(X_test)
    
    # simpan hasil prediksi ke file tsv
    nama_file_hasil = 'hasil_prediksi_sentimen_test.tsv'
    df_test.to_csv(nama_file_hasil, sep='\t', index=False)
    print(f"prediksi sentimen test berhasil di simpan ke file '{nama_file_hasil}")
    print("\nContoh hasil prediksi otomatis pada data test:")
    print(df_test[['text', 'sentiment_prediction']].head(5))

except Exception as e:
    print(f"terjadi kesalahan pada proses data test: {e}")
    



    
