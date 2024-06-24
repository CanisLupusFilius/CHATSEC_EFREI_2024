import psycopg2
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
email = input("Entrez votre email: ")
mot_de_passe = input("Entrez votre mot de passe: ")

# Récupérer les informations de l'utilisateur depuis la base de données
cursor.execute("""
    SELECT sel_mot_de_passe, mot_de_passe_hash
    FROM utilisateurs
    WHERE email = %s
""", (email,))
result = cursor.fetchone()

if result is None:
    print("Utilisateur non trouvé")
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

# Fermer la connexion à la base de données
cursor.close()
conn.close()
