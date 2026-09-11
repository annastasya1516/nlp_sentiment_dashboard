import re

def bersihkan_teks(teks):
    if not isinstance (teks, str):
        return ""
    
    teks = teks.lower()
    teks = re.sub(r'[^a-z0-9\s]', '', teks)
    return teks.strip()
