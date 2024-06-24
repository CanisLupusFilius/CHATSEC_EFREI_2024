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
    SELECT cle_publique_rsa, cle_privee_rsa_chiffree, sel_mot_de_passe, mot_de_passe_hash
    FROM utilisateurs
    WHERE email = %s
""", (email,))
result = cursor.fetchone()

if result is None:
    print("Utilisateur non trouvé")
else:
    cle_publique_rsa, cle_privee_rsa_chiffree, sel_mot_de_passe, mot_de_passe_hash = result

    # Convertir les hash récupérés en format bytes
    mot_de_passe_hash = mot_de_passe_hash.encode('utf-8') if isinstance(mot_de_passe_hash, str) else mot_de_passe_hash
    sel_mot_de_passe = sel_mot_de_passe.encode('utf-8') if isinstance(sel_mot_de_passe, str) else sel_mot_de_passe

    # Vérifier le mot de passe
    if bcrypt.checkpw(mot_de_passe.encode('utf-8'), mot_de_passe_hash):
        print("Connexion réussie")
        # Vous pouvez maintenant accéder aux autres informations comme cle_publique_rsa et cle_privee_rsa_chiffree
        # selon vos besoins
    else:
        print("Mot de passe incorrect")

# Fermer la connexion à la base de données
cursor.close()
conn.close()
