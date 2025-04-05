from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import os
from dotenv import load_dotenv


def get_master_key():
    if not os.path.exists("Banking_System-RodriguezPatino-CruzReichert/.env"):
        key = get_random_bytes(32)
        open(".env","w").write("DNI_KEY=" +  key.hex())
        load_dotenv(".env")
        return bytes.fromhex(os.environ.get("DNI_KEY"))
    else:
        load_dotenv("Banking_System-RodriguezPatino-CruzReichert/.env")
        return bytes.fromhex(os.environ.get("DNI_KEY"))


def hash_with_salt(texto):
    texto = texto.encode()  
    salt = get_random_bytes(32)  
    hash = SHA256.new()
    hash.update(texto)
    hash.update(salt)
    return hash.digest(), salt 

def verify_password(input_password, stored_hash, stored_salt):
    input_password = input_password.encode()  
    stored_salt = bytes.fromhex(stored_salt)  
    stored_hash = bytes.fromhex(stored_hash)  
    
    hash = SHA256.new()
    hash.update(input_password)
    hash.update(stored_salt)

    return hash.digest() == stored_hash  # Compare hashes


def decrypt_aes(texto_cifrado, nonce, clave):
    texto_cifrado_bytes = bytes.fromhex(texto_cifrado)
    nonce_bytes = bytes.fromhex(nonce)
    cipher = AES.new(clave, AES.MODE_EAX, nonce=nonce_bytes)
    texto_descifrado = cipher.decrypt(texto_cifrado_bytes)
    return texto_descifrado.decode("UTF-8")


def encrypt_aes(texto, clave):
    texto_bytes = texto.encode("UTF-8")
    cipher = AES.new(clave, AES.MODE_EAX)
    nonce = cipher.nonce
    texto_cifrado, tag = cipher.encrypt_and_digest(texto_bytes)
    texto_cifrado_str = texto_cifrado.hex()
    return texto_cifrado_str, nonce.hex()


def ofuscar_dni(dni):
    return '*' * (len(dni) - 4) + dni[-4:]

if __name__ == '__main__':
    print("hola mundo")

