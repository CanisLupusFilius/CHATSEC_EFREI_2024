import subprocess
import os
import psycopg2
import base64
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Connexion à la base de données PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname="BDD",
        user="votre_utilisateur",
        password="votre_mot_de_passe",
        host="localhost"
    )

def check_openssl_installed():
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("OpenSSL est installé :")
            print(result.stdout)
        else:
            print("OpenSSL n'est pas installé correctement.")
            return False
    except FileNotFoundError:
        print("OpenSSL n'est pas installé ou n'est pas dans le PATH.")
        return False
    return True

def generate_rsa_key(key_size):
    private_key_file = 'temp_private_key.pem'
    public_key_file = 'temp_public_key.pem'
    subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', private_key_file, '-pkeyopt', f'rsa_keygen_bits:{key_size}'])
    subprocess.run(['openssl', 'rsa', '-pubout', '-in', private_key_file, '-out', public_key_file])
    
    with open(private_key_file, 'r') as priv_file:
        private_key = priv_file.read()
    with open(public_key_file, 'r') as pub_file:
        public_key = pub_file.read()
    
    os.remove(private_key_file)
    os.remove(public_key_file)
    
    return private_key, public_key

def store_user(nom, email, mot_de_passe, private_key, public_key):
    sel = os.urandom(16)
    kdf = Scrypt(salt=sel, length=32, n=2**14, r=8, p=1, backend=default_backend())
    key = kdf.derive(mot_de_passe.encode())
    
    cipher = Cipher(algorithms.AES(key), modes.CTR(os.urandom(16)), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_private_key = encryptor.update(private_key.encode()) + encryptor.finalize()
    
    hashed_password = hashlib.sha256(mot_de_passe.encode() + sel).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO utilisateurs (nom, email, cle_publique_rsa, cle_privee_rsa_chiffree, sel_mot_de_passe, mot_de_passe_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nom, email, public_key, base64.b64encode(encrypted_private_key).decode(), base64.b64encode(sel).decode(), hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

def get_public_key(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT clé_publique_rsa FROM utilisateurs WHERE email = %s", (email,))
    public_key = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return public_key

def get_private_key(email, mot_de_passe):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT clé_privée_rsa_chiffrée, sel_mot_de_passe FROM utilisateurs WHERE email = %s", (email,))
    encrypted_private_key, sel = cursor.fetchone()
    cursor.close()
    conn.close()
    
    sel = base64.b64decode(sel)
    kdf = Scrypt(salt=sel, length=32, n=2**14, r=8, p=1, backend=default_backend())
    key = kdf.derive(mot_de_passe.encode())
    
    encrypted_private_key = base64.b64decode(encrypted_private_key)
    
    cipher = Cipher(algorithms.AES(key), modes.CTR(encrypted_private_key[:16]), backend=default_backend())
    decryptor = cipher.decryptor()
    private_key = decryptor.update(encrypted_private_key[16:]) + decryptor.finalize()
    
    return private_key.decode()

def encrypt_message(public_key, message, encrypted_file):
    with open("message.txt", "w") as msg_file:
        msg_file.write(message)
    with open("public_key.pem", "w") as pub_file:
        pub_file.write(public_key)
    subprocess.run(['openssl', 'rsautl', '-encrypt', '-inkey', 'public_key.pem', '-pubin', '-in', 'message.txt', '-out', encrypted_file])
    os.remove("message.txt")
    os.remove("public_key.pem")

def decrypt_message(private_key, encrypted_file, decrypted_file):
    with open("private_key.pem", "w") as priv_file:
        priv_file.write(private_key)
    subprocess.run(['openssl', 'rsautl', '-decrypt', '-inkey', 'private_key.pem', '-in', encrypted_file, '-out', decrypted_file])
    os.remove("private_key.pem")

if __name__ == "__main__":
    if check_openssl_installed():
        # Génération des clés et stockage de l'utilisateur
        nom = "Utilisateur2"
        email = "user2@example.com"
        mot_de_passe = "password123"

        private_key, public_key = generate_rsa_key(2048)
        store_user(nom, email, mot_de_passe, private_key, public_key)

        # Récupération de la clé publique de l'utilisateur 2 pour le chiffrement
        user2_public_key = get_public_key("user2@example.com")

        # Chiffrement du message
        message = input("Entrez le message à chiffrer : ")
        encrypted_file = 'encrypted_message.bin'
        decrypted_file = 'decrypted_message.txt'
        encrypt_message(user2_public_key, message, encrypted_file)
        print(f'Message chiffré dans le fichier : {encrypted_file}')

        # Récupération de la clé privée de l'utilisateur 2 pour le déchiffrement
        user2_private_key = get_private_key("user2@example.com", "password123")
        decrypt_message(user2_private_key, encrypted_file, decrypted_file)
        print(f'Message dechiffre dans le fichier : {decrypted_file}')
        
        with open(decrypted_file, 'r') as file:
            decrypted_message = file.read()
            print(f'Message dechiffre : {decrypted_message}')

        # Nettoyage des fichiers temporaires
        os.remove(encrypted_file)
        os.remove(decrypted_file)
    else:
        print("Veuillez installer OpenSSL et ajouter son repertoire 'bin' au PATH.")
