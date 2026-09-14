from utils.preprocessing import bersihkan_teks
from services.validation_service import (
    adalah_pertanyaan_sederhana,
    teks_tidak_jelas
)
from utils.load_model import load_model_assets
from utils.database import simpan_ke_db

def proses_sentimen(teks):
    """
    Memproses teks sampai menghasilkan klasifikasi sentimen.
    """

    # CEK TEKS TIDAK JELAS
    if teks_tidak_jelas(teks):

        teks_bersih = bersihkan_teks(teks)

        prediksi = "invalid"

        simpan_ke_db(
            teks,
            teks_bersih,
            prediksi
        )

        return prediksi

    # BERSIHKAN TEKS
    teks_bersih = bersihkan_teks(teks)

    # CEK PERTANYAAN SEDERHANA
    if adalah_pertanyaan_sederhana(teks):

        prediksi = "neutral"

    else:

        # LOAD MODEL
        model, vectorizer = load_model_assets()

        # UBAH TEKS MENJADI TF-IDF
        teks_vektor = vectorizer.transform(
            [teks_bersih]
        )

        # PREDIKSI SENTIMEN
        prediksi = model.predict(
            teks_vektor
        )[0]

    # SIMPAN HASIL KLASIFIKASI KE DATABASE
    simpan_ke_db(
        teks,
        teks_bersih,
        prediksi
    )

    return prediksi