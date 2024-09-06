from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

def encrypt_document(file_data, key):
    # Generate a random 16-byte IV (Initialization Vector)
    iv = os.urandom(16)
    backend = default_backend()

    # Create a cipher object using AES algorithm, key, and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

    # Pad the plaintext to ensure it is a multiple of the block size
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()

    # Encrypt the padded data
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return iv + encrypted_data

def decrypt_document(encrypted_data, key):
    # Extract the IV from the beginning of the encrypted data
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    backend = default_backend()

    # Create a cipher object using AES algorithm, key, and IV
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

    # Decrypt the data
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    return decrypted_data

def generate_key():
    return os.urandom(32)  # AES-256 key
