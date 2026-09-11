import hashlib

def hash_password(password):
    """
    Mengubah password menjadi hash SHA-256.
    """
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

def verify_password(password, password_hash):
    """
    Mengecek apakah password sesuai dengan
    hash SHA-256 yang tersimpan.
    """
    return hash_password(password) == password_hash