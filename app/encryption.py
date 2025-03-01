from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


def hash_with_salt(texto):
    texto = texto.encode()  
    salt = get_random_bytes(16)  
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
    return texto_descifrado.decode()


def encrypt_aes(texto, clave):
    # Convertir el texto a bytes
    texto_bytes = texto.encode()

    # Crear un objeto AES con la clave proporcionada
    cipher = AES.new(clave, AES.MODE_EAX)

    # Cifrar el texto
    nonce = cipher.nonce
    texto_cifrado, tag = cipher.encrypt_and_digest(texto_bytes)

    # Convertir el texto cifrado en bytes a una cadena de texto
    texto_cifrado_str = texto_cifrado.hex()

    # Devolver el texto cifrado y el nonce
    return texto_cifrado_str, nonce.hex()

# Función para ofuscar el DNI
def ofuscar_dni(dni):
    return '*' * (len(dni) - 4) + dni[-4:]

if __name__ == '__main__':
    texto = "Hola Mundo"
    clave = get_random_bytes(16)
    texto_cifrado, nonce = encrypt_aes(texto, clave)
    print("Texto cifrado: " + texto_cifrado)
    print("Nonce: " + nonce)
    des = decrypt_aes(texto_cifrado, nonce, clave)
    print("Texto descifrado: " + des)

