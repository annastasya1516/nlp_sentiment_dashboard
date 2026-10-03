import pandas as pd
from utils.preprocessing import bersihkan_teks
KOLOM_TEXT = [
    "text",
    "teks",
    "review",
    "ulasan",
    "komentar",
    "comment",
    "tweet",
    "caption",
    "Teks Asli",
    "teks asli"
]

KOLOM_SENTIMEN = [
    "sentiment",
    "sentimen",
    "label",
    "kategori",
    "class",
    "polarity"
]

def cari_kolom(df, daftar_kolom):

    kolom_dataset = {
        kolom.strip().lower(): kolom
        for kolom in df.columns
    }

    for nama in daftar_kolom:

        if nama in kolom_dataset:
            return kolom_dataset[nama]

    return None
def deteksi_kolom_dataset(df):

    kolom_text = cari_kolom(
        df,
        KOLOM_TEXT
    )

    kolom_sentimen = cari_kolom(
        df,
        KOLOM_SENTIMEN
    )

    return kolom_text, kolom_sentimen
def transformasi_dataset(df):

    kolom_text, kolom_sentimen = deteksi_kolom_dataset(df)

    if not kolom_text:
        raise ValueError(
            "Kolom teks tidak dapat ditemukan."
        )

    if not kolom_sentimen:
        raise ValueError(
            "Kolom sentimen tidak dapat ditemukan."
        )

    df = df.rename(
        columns={
            kolom_text: "text",
            kolom_sentimen: "sentiment"
        }
    )

    df = df[
        ["text", "sentiment"]
    ].copy()

    return df

def normalisasi_dataset_tanpa_header(df):
    if df.shape[1] != 4:
        raise ValueError(
            "Format dataset tanpa header tidak sesuai."
        )

    df = df.rename(
        columns={
            2: "sentiment",
            3: "text"
        }
    )

    df = df[
        ["text", "sentiment"]
    ].copy()

    df = df[
        df["sentiment"].isin([
            "Positive",
            "Negative",
            "Neutral"
        ])
    ].copy()

    df["sentiment"] = (
        df["sentiment"]
        .str.lower()
    )

    return df

def normalisasi_label_sentimen(df):

    mapping = {
        "positive": "positive",
        "positif": "positive",
        "negative": "negative",
        "negatif": "negative",
        "neutral": "neutral",
        "netral": "neutral"
    }

    df["sentiment"] = (
        df["sentiment"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
    )

    df = df.dropna(
        subset=["sentiment"]
    ).copy()

    return df

def bersihkan_dataset(df):

    df["text"] = (
        df["text"]
        .astype(str)
        .apply(bersihkan_teks)
    )

    df = df[
        df["text"].str.strip() != ""
    ].copy()

    return df

def validasi_dataset(df):

    df = df.drop_duplicates().copy()

    df = df[
        df["text"].str.strip() != ""
    ].copy()

    df = df[
        df["sentiment"].notna()
    ].copy()

    return df

def proses_etl_dataset(df, tanpa_header=False):

    if tanpa_header:
        df = normalisasi_dataset_tanpa_header(df)
    else:
        df = transformasi_dataset(df)

    df = normalisasi_label_sentimen(df)
    df = bersihkan_dataset(df)
    df = validasi_dataset(df)

    return df

def proses_file_dataset(file_path, ekstensi):

    separator = "\t" if ekstensi == ".tsv" else ","

    df = pd.read_csv(
        file_path,
        sep=separator,
        dtype=str,
        keep_default_na=False
    )

    kolom_text, kolom_sentimen = deteksi_kolom_dataset(df)

    if kolom_text and kolom_sentimen:
        return proses_etl_dataset(
            df,
            tanpa_header=False
        )

    df = pd.read_csv(
        file_path,
        sep=separator,
        header=None,
        dtype=str,
        keep_default_na=False
    )

    return proses_etl_dataset(
        df,
        tanpa_header=True
    )