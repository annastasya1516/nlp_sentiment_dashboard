import re

def adalah_pertanyaan_sederhana(teks):
    """
    Mengecek apakah teks merupakan pertanyaan sederhana
    tanpa indikasi sentimen positif atau negatif yang kuat.
    """

    teks = teks.lower().strip()

    # Kata tanya umum
    kata_tanya = [
        "apa",
        "apakah",
        "bagaimana",
        "kapan",
        "dimana",
        "dimana",
        "siapa",
        "mengapa",
        "kenapa",
        "berapa",
        "bolehkah",
        "bisakah"
    ]

    # Kata yang menunjukkan sentimen kuat
    kata_sentimen = [
        "bagus",
        "baik",
        "mantap",
        "puas",
        "suka",
        "senang",
        "buruk",
        "jelek",
        "kecewa",
        "benci",
        "lambat",
        "parah",
        "mengecewakan"
    ]

    # Cek tanda tanya
    ada_tanda_tanya = "?" in teks

    # Cek kata tanya di awal kalimat
    kata_pertama = teks.split()[0] if teks.split() else ""

    ada_kata_tanya = kata_pertama in kata_tanya

    # Cek apakah terdapat sentimen kuat
    ada_sentimen_kuat = any(
        kata in teks
        for kata in kata_sentimen
    )

    # Pertanyaan sederhana = pertanyaan
    # tetapi tidak mengandung sentimen kuat
    if (
        (ada_tanda_tanya or ada_kata_tanya)
        and not ada_sentimen_kuat
    ):
        return True

    return False

def teks_tidak_jelas(teks):
    """
    Mengecek apakah teks terlalu pendek atau terlihat
    seperti teks acak/tidak bermakna.
    """

    teks = teks.lower().strip()

    # Jika kosong
    if not teks:
        return True

    kata = teks.split()

    # Terlalu pendek
    if len(teks) < 3:
        return True

    # Jika hanya satu kata, cek pola huruf yang tidak wajar
    if len(kata) == 1:
        kata_satu = kata[0]

        # Tidak memiliki vokal sama sekali
        if not re.search(r"[aeiou]", kata_satu):
            return True

        # Terlalu banyak konsonan berurutan
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", kata_satu):
            return True

    return False