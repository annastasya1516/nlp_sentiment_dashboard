import pandas as pd
import re
import pickle
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

#buat database sqlite
conn = sqlite3.connect('riwayat_sentimen.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS riwayat_sentimen(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teks_asli TEXT,
        teks_bersih TEXT,
        klasifikasi TEXT,
        waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
print("Database 'riwayat_sentimen.db' berhasil di buat!")

# proses train model
df_train = pd.read_csv('train_preprocess_ori.tsv', sep='\t')

def bersihkan_teks(teks):
    if not isinstance(teks, str):
        return ""
    teks = teks.lower()
    teks = re.sub(r'a-z9-0\s', '', teks)
    return teks.strip()

print("sedang memproses penguncian model...")
df_train['text_clean'] = df_train['text'].apply(bersihkan_teks)

# ekstraksi fitur dengan tf-idf
vectorizer = TfidfVectorizer()  
X_train = vectorizer.fit_transform(df_train['text_clean'])
y_train = df_train['sentiment']

# training model dengan logistic regression
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# eksport model biar akurasi konsisten (pickle)
with open('model_sentimen.pkl', 'wb') as f_model:
    pickle.dump(model, f_model)
with open('vectorizer_tfidf.pkl', 'wb') as f_vec:
    pickle.dump(vectorizer, f_vec)
    
print("Model dan vectorizer berhasil di kunci menjadi file .pkl! Akurasi tidak akan berubah.")
    




