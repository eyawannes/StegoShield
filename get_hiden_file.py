from crypto import decrypt_file
from PIL import Image
import random
import hashlib

# --- Générer une permutation sécurisée en fonction d'un mot de passe ---
def generate_permutation(width, height, password):
    total_pixels = width * height * 3  # Chaque pixel contient 3 composantes (R, G, B)
    seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
    random.seed(seed)
    permutation = list(range(total_pixels))
    random.shuffle(permutation)
    return permutation

    # --- Extraire des données d'une image ---
def recover_data(image_path, password="default"):
    img = Image.open(image_path)
    width, height = img.size

    perm = generate_permutation(width, height, password)
    pixels = img.load()

    bits = ""
    data_len = None

    for bit_pos in perm:
        x = (bit_pos // 3) % width
        y = (bit_pos // 3) // width
        color = bit_pos % 3

        bits += str(pixels[x, y][color] & 1)

        if len(bits) == 32 and data_len is None:
            data_len = int(bits, 2)              # Longueur du fichier
            total_bits = 32 + data_len * 8       # Nombre total de bits nécessaires

        if data_len is not None and len(bits) >= total_bits:
            break

    if data_len is None:
        return None

    data_bits = bits[32 : 32 + data_len * 8]
    data_bytes = [int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8)]
    return bytes(data_bytes)

# Nom du fichier contenant l'image avec les données cachées
img = "image_secret.png"

# --- Mot de passe pour permutation ---
password = "QRZ@x54%uT9p!2k#"

# --- Récupérer les données cachées ---
hidden_data = recover_data(img, password)
print(f"Données récupérées ! Taille = {len(hidden_data)} octets")

# --- Déchiffrer les données récupérées ---
decrypted_data = decrypt_file(hidden_data)
print("Déchiffrement réussi !")

# --- Sauvegarder le PDF final ---
output_file = "extracted.pdf"
with open(output_file, "wb") as f:
    f.write(decrypted_data)

print(f"PDF reconstruit : {output_file}")
