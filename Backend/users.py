import psycopg2
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import bcrypt
import re


def get_db_connection():
    return psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="8314",
        host="localhost"
    )


def login_back(username, password):
# Configurer la connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # Prendre les informations de l'utilisateur
    name = username
    mot_de_passe = password

    # Récupérer les informations de l'utilisateur depuis la base de données
    cursor.execute("""
        SELECT sel_mot_de_passe, mot_de_passe_hash
        FROM utilisateurs
        WHERE nom = %s
    """, (name,))
    result = cursor.fetchone()

    if result is None:
        print("Utilisateur non trouvé")
        cursor.close()
        conn.close()
        return False
    else:
        sel_mot_de_passe_db, mot_de_passe_hash_db = result

        # Convertir les données de type memoryview en bytes
        sel_mot_de_passe_db = bytes(sel_mot_de_passe_db)
        mot_de_passe_hash_db = bytes(mot_de_passe_hash_db)

        # Vérifier le mot de passe
        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), mot_de_passe_hash_db):
            print("Connexion réussie")
            # Vous pouvez maintenant accéder aux autres informations si nécessaire
        else:
            print("Mot de passe incorrect")
        
        cursor.close()
        conn.close()
        return True


def registering_back(username, password):
    mdp_valid = False
    mot_de_passe = password
    nom = username

    # Configurer la connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # Générer une paire de clés RSA
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    cle_privee = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    cle_publique = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Générer un sel et hasher le mot de passe
    sel_mot_de_passe = bcrypt.gensalt()
    sel_mot_de_passe_hex = sel_mot_de_passe  # Convertir en hexadécimal

    mot_de_passe_hash = bcrypt.hashpw(mot_de_passe.encode('utf-8'), sel_mot_de_passe)

    # Chiffrer la clé privée RSA avec le mot de passe (hashed)
    cle_privee_chiffree = bcrypt.hashpw(cle_privee, sel_mot_de_passe)

    # Insérer les informations dans la base de données
    cursor.execute("""
        INSERT INTO utilisateurs (nom, cle_publique_rsa, cle_privee_rsa_chiffree, sel_mot_de_passe, mot_de_passe_hash)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING utilisateur_id
    """, (nom, cle_publique, cle_privee_chiffree, sel_mot_de_passe, mot_de_passe_hash))
    utilisateur_id = cursor.fetchone()[0]

    # Confirmer les changements et fermer la connexion
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Utilisateur enregistré avec l'ID: {utilisateur_id}")

    return True

def get_user_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nom FROM utilisateurs")
        users = cursor.fetchall()
        return [user[0] for user in users]
    finally:
        cursor.close()
        conn.close()

def get_user_id_from_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT utilisateur_id FROM utilisateurs WHERE nom = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        conn.close()

def get_username(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nom FROM utilisateurs WHERE utilisateur_id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        conn.close()
