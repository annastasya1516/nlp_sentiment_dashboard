from utils.preprocessing import bersihkan_teks
from services.validation_service import (
    adalah_pertanyaan_sederhana,
    teks_tidak_jelas
)
from utils.load_model import load_model_assets
from utils.database import simpan_ke_db


def proses_sentimen(teks):
    if teks_tidak_jelas(teks):
        teks_bersih = bersihkan_teks(teks)
        prediksi = "invalid"
        confidence = None

        simpan_ke_db(
            teks,
            teks_bersih,
            prediksi,
            confidence
        )

        return prediksi, confidence

    teks_bersih = bersihkan_teks(teks)

    if adalah_pertanyaan_sederhana(teks):
        prediksi = "neutral"
        confidence = None

    else:
        model, vectorizer = load_model_assets()

        teks_vektor = vectorizer.transform(
            [teks_bersih]
        )

        prediksi = model.predict(
            teks_vektor
        )[0]

        probabilitas = model.predict_proba(
            teks_vektor
        )[0]

        confidence = max(
            probabilitas
        ) * 100

    simpan_ke_db(
        teks,
        teks_bersih,
        prediksi,
        confidence
    )

    return prediksi, confidence