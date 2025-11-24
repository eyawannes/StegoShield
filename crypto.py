from cryptography.fernet import Fernet

# --- Génération de clé ---
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# --- Charger la clé ---
def load_key():
    return open("secret.key", "rb").read()

# --- Chiffrer ---
def encrypt_message(message):
    key = load_key()
    cipher = Fernet(key)
    return cipher.encrypt(message)

# --- Déchiffrer ---
def decrypt_message(encrypted_message):
    key = load_key()
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message)
# --- Chiffrer un fichier (bytes) ---
def encrypt_file(data):
    key = load_key()
    cipher = Fernet(key)
    return cipher.encrypt(data)

# --- Déchiffrer un fichier (bytes) ---
def decrypt_file(data):
    key = load_key()
    cipher = Fernet(key)
    return cipher.decrypt(data)