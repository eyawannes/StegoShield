from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

# ------------------------
# Génération des clés RSA
# ------------------------
def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Sauvegarde clé privée
    with open("private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Sauvegarde clé publique
    with open("public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("🔑 Clés RSA générées : private.pem & public.pem")


# ------------------------
# Chiffrement hybride
# ------------------------
def hybrid_encrypt(data: bytes) -> bytes:
    # Charger clé publique
    with open("public.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())

    # Générer clé AES (Fernet)
    aes_key = Fernet.generate_key()
    cipher = Fernet(aes_key)

    encrypted_data = cipher.encrypt(data)

    # Chiffrer la clé AES avec RSA
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Format : [taille clé][clé RSA chiffrée][data AES chiffrée]
    return len(encrypted_key).to_bytes(4, "big") + encrypted_key + encrypted_data


# ------------------------
# Déchiffrement hybride
# ------------------------
def hybrid_decrypt(payload: bytes) -> bytes:
    # Charger clé privée
    with open("private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    # Extraire longueur de la clé RSA
    key_len = int.from_bytes(payload[:4], "big")
    encrypted_key = payload[4:4 + key_len]
    encrypted_data = payload[4 + key_len:]

    # Déchiffrer clé AES
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    cipher = Fernet(aes_key)
    return cipher.decrypt(encrypted_data)
