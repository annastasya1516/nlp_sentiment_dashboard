import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    ConfusionMatrixDisplay
)
from utils.preprocessing import bersihkan_teks

# BACA DATASET
try:
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

except FileNotFoundError:
    print(
        "File dataset tidak ditemukan. "
        "Pastikan file berada di folder datasets."
    )
    raise SystemExit

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

print(
    f"\nAkurasi model pada data validasi: "
    f"{akurasi * 100:.2f}%"
)

print("\nLaporan Klasifikasi Detail:")

print(
    classification_report(
        y_valid,
        y_pred
    )
)

# PREDIKSI DATA TEST
try:
    df_test = pd.read_csv(
        "datasets/test_preprocess_masked_label.tsv",
        sep="\t"
    )

    print(
        f"\nBerhasil memuat dataset test: "
        f"{len(df_test)} baris"
    )

    df_test["text_clean"] = df_test["text"].apply(
        bersihkan_teks
    )

    X_test = vectorizer.transform(
        df_test["text_clean"]
    )

    df_test["sentiment_prediction"] = model.predict(
        X_test
    )

    nama_file_hasil = (
        "datasets/hasil_prediksi_sentimen_test.tsv"
    )

    df_test.to_csv(
        nama_file_hasil,
        sep="\t",
        index=False
    )

    print(
        f"Prediksi data test berhasil disimpan "
        f"ke '{nama_file_hasil}'"
    )

    print("\nContoh hasil prediksi:")

    print(
        df_test[
            ["text", "sentiment_prediction"]
        ].head(5)
    )

except FileNotFoundError:
    print(
        "\nDataset test tidak ditemukan. "
        "Proses prediksi test dilewati."
    )

# CONFUSION MATRIX
ConfusionMatrixDisplay.from_predictions(
    y_valid,
    y_pred,
    cmap="Blues"
)
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()