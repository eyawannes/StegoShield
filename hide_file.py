from crypto import encrypt_file, decrypt_file
from PIL import Image
import random
import hashlib

# --- Convertir des bytes en binaire ---
def to_binary(data):
    return ''.join(format(byte, '08b') for byte in data)

# --- Générer une permutation sécurisée en fonction d'un mot de passe ---
def generate_permutation(width, height, password):
    total_pixels = width * height * 3  # Chaque pixel contient 3 composantes (R, G, B)
    seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
    random.seed(seed)
    permutation = list(range(total_pixels))
    random.shuffle(permutation)
    return permutation

# --- Cacher des données (bytes) dans une image ---
def hide_data(image_path, output_path, data, password="default"):
    img = Image.open(image_path)
    width, height = img.size

    # On stocke d'abord la taille en 32 bits + les données
    data_length = len(data)
    binary = format(data_length, '032b') + to_binary(data)
    max_capacity = width * height * 3

    if len(binary) > max_capacity:
        raise ValueError("Le fichier est trop gros pour cette image !")

    # Générer permutation
    perm = generate_permutation(width, height, password)
    pixels = img.load()
    idx = 0  # index du bit à insérer

    for bit_pos in perm:
        if idx >= len(binary):
            break

        x = (bit_pos // 3) % width      # colonne
        y = (bit_pos // 3) // width     # ligne
        color = bit_pos % 3             # canal (0=R, 1=G, 2=B)

        pixel = list(pixels[x, y])
        pixel[color] = (pixel[color] & ~1) | int(binary[idx])
        pixels[x, y] = tuple(pixel)
        idx += 1

    img.save(output_path)

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



# --- Fichier à cacher ---
input_file = "cv.pdf"
# --- Mot de passe pour permutation ---
password = "QRZ@x54%uT9p!2k#"

# --- Lire le fichier en bytes ---
with open(input_file, "rb") as f:
    original_data = f.read()

# --- Chiffrement du fichier ---
encrypted_data = encrypt_file(original_data)
print("Fichier chiffré !")

# --- Mot de passe pour permutation ---
password = "QRZ@x54%uT9p!2k#"

# --- Cacher le fichier chiffré dans l'image ---
hide_data("cat.png", "image_secret.png", encrypted_data, password)
print("Fichier caché dans image_secret.png")


