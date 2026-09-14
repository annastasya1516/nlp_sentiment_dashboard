import json
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from flask_app.utils.preprocessing import bersihkan_teks

# BACA DATASET
df_train = pd.read_csv(
    "datasets/train_preprocess_ori.tsv",
    sep="\t"
)

df_valid = pd.read_csv(
    "datasets/valid_preprocess.tsv",
    sep="\t"
)

print(
    f"Berhasil memuat data! "
    f"Train: {len(df_train)} baris, "
    f"Valid: {len(df_valid)} baris"
)

# PREPROCESSING
print("\nSedang membersihkan data train...")

df_train["text_clean"] = df_train["text"].apply(
    bersihkan_teks
)

print("Sedang membersihkan data validasi...")

df_valid["text_clean"] = df_valid["text"].apply(
    bersihkan_teks
)

print("Proses pembersihan selesai!")

# TF-IDF
print("\nSedang melakukan ekstraksi fitur TF-IDF...")

vectorizer = TfidfVectorizer()

X_train = vectorizer.fit_transform(
    df_train["text_clean"]
)

X_valid = vectorizer.transform(
    df_valid["text_clean"]
)

y_train = df_train["sentiment"]
y_valid = df_valid["sentiment"]

print("Ekstraksi fitur selesai!")

# TRAINING MODEL
print("\nSedang melakukan training model...")

model = LogisticRegression(
    max_iter=1000
)

model.fit(
    X_train,
    y_train
)

print("Model berhasil dilatih!")

# EVALUASI MODEL
y_pred = model.predict(X_valid)

akurasi = accuracy_score(
    y_valid,
    y_pred
)

akurasi_persen = akurasi * 100

print(
    f"\nAkurasi model pada data validasi: "
    f"{akurasi_persen:.2f}%"
)

# SIMPAN METRICS
metrics = {
    "accuracy": f"{akurasi_persen:.2f}%"
}

with open(
    "models/metrics.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        metrics,
        file,
        indent=4
    )

print(
    "Metrics berhasil disimpan "
    "ke models/metrics.json"
)

# SIMPAN MODEL
with open(
    "models/model_sentimen.pkl",
    "wb"
) as file_model:
    pickle.dump(
        model,
        file_model
    )

print(
    "Model berhasil disimpan "
    "ke models/model_sentimen.pkl"
)

# SIMPAN VECTORIZER
with open(
    "models/vectorizer_tfidf.pkl",
    "wb"
) as file_vectorizer:
    pickle.dump(
        vectorizer,
        file_vectorizer
    )

print(
    "Vectorizer berhasil disimpan "
    "ke models/vectorizer_tfidf.pkl"
)

print("\nProses training dan penyimpanan selesai!")