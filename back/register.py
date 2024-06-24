import psycopg2
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import bcrypt

# Configurer la connexion à la base de données
conn = psycopg2.connect(
    dbname="bdd",
    user="postgres",
    password="8314",
    host="localhost"
)
cursor = conn.cursor()

# Prendre les informations de l'utilisateur
nom = input("Entrez votre nom: ")
email = input("Entrez votre email: ")
mot_de_passe = input("Entrez votre mot de passe: ")

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
    INSERT INTO utilisateurs (nom, email, cle_publique_rsa, cle_privee_rsa_chiffree, sel_mot_de_passe, mot_de_passe_hash)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING utilisateur_id
""", (nom, email, cle_publique, cle_privee_chiffree, sel_mot_de_passe, mot_de_passe_hash))
utilisateur_id = cursor.fetchone()[0]

# Confirmer les changements et fermer la connexion
conn.commit()
cursor.close()
conn.close()

print(f"Utilisateur enregistré avec l'ID: {utilisateur_id}")
