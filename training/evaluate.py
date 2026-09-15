import json
import pickle
import pandas as pd
from sklearn.metrics import accuracy_score
from flask_app.utils.preprocessing import bersihkan_teks

# BACA DATA VALIDASI
df_valid = pd.read_csv(
    "datasets/valid_preprocess.tsv",
    sep="\t"
)

print(
    f"Berhasil memuat data validasi: "
    f"{len(df_valid)} baris"
)

# LOAD MODEL
with open(
    "models/model_sentimen.pkl",
    "rb"
) as file_model:
    model = pickle.load(file_model)

# LOAD VECTORIZER
with open(
    "models/vectorizer_tfidf.pkl",
    "rb"
) as file_vectorizer:
    vectorizer = pickle.load(file_vectorizer
    )

print(
    "Model dan vectorizer berhasil dimuat!"
)

# PREPROCESSING
df_valid["text_clean"] = df_valid["text"].apply(
    bersihkan_teks
)

# TRANSFORM DATA
X_valid = vectorizer.transform(
    df_valid["text_clean"]
)
y_valid = df_valid["sentiment"]

# PREDIKSI
y_pred = model.predict(
    X_valid
)

# HITUNG AKURASI
akurasi = accuracy_score(
    y_valid,
    y_pred
)

akurasi_persen = akurasi * 100

print(
    f"Akurasi model pada data validasi: "
    f"{akurasi_persen:.2f}%"
)

# UPDATE METRICS
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
    "Metrics berhasil diperbarui "
    "di models/metrics.json"
)