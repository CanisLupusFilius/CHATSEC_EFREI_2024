import bcrypt

def creer_sel_et_hash(mot_de_passe):
    # Générer un sel
    sel = bcrypt.gensalt()

    # Hasher le mot de passe avec le sel
    mot_de_passe_hash = bcrypt.hashpw(mot_de_passe.encode('utf-8'), sel)

    return sel, mot_de_passe_hash

def verifier_mot_de_passe(mot_de_passe_entre, mot_de_passe_hash, sel):
    # Vérifier le mot de passe en utilisant le sel et le hash existant
    if bcrypt.checkpw(mot_de_passe_entre.encode('utf-8'), mot_de_passe_hash):
        print("Le mot de passe est correct!")
    else:
        print("Le mot de passe est incorrect.")

# Exemple d'utilisation
if __name__ == "__main__":
    # Demander à l'utilisateur de saisir un mot de passe
    mot_de_passe_utilisateur = input("Entrez votre mot de passe: ")

    # Créer un sel et un hash pour ce mot de passe
    sel, mot_de_passe_hash = creer_sel_et_hash(mot_de_passe_utilisateur)

    print(f"Sel: {sel}")
    print(f"Mot de passe hashé: {mot_de_passe_hash}")

    # Simuler la vérification d'un autre mot de passe (normalement, vous le saisiriez à nouveau)
    autre_mot_de_passe = input("Entrez un autre mot de passe pour vérification: ")

    # Vérifier si le mot de passe correspond au hash existant
    verifier_mot_de_passe(autre_mot_de_passe, mot_de_passe_hash, sel)
