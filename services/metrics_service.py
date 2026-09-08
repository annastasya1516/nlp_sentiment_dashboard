import json

def ambil_akurasi():
    """
    Mengambil nilai akurasi model dari file metrics.json.
    """

    try:
        with open(
            "models/metrics.json",
            "r",
            encoding="utf-8"
        ) as file:
            metrics = json.load(file)

        return metrics["accuracy"]

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return "N/A"