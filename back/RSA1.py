import subprocess
import os

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

def generate_rsa_key(key_size, private_key_file, public_key_file):
    subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', private_key_file, '-pkeyopt', f'rsa_keygen_bits:{key_size}'])
    subprocess.run(['openssl', 'rsa', '-pubout', '-in', private_key_file, '-out', public_key_file])

def encrypt_message(public_key_file, message, encrypted_file):
    with open("message.txt", "w") as msg_file:
        msg_file.write(message)
    subprocess.run(['openssl', 'rsautl', '-encrypt', '-inkey', public_key_file, '-pubin', '-in', 'message.txt', '-out', encrypted_file])
    os.remove("message.txt")

def decrypt_message(private_key_file, encrypted_file, decrypted_file):
    subprocess.run(['openssl', 'rsautl', '-decrypt', '-inkey', private_key_file, '-in', encrypted_file, '-out', decrypted_file])

if __name__ == "__main__":
    if check_openssl_installed():
        key_size = 2048

        private_key_file = 'user2_private_key.pem'
        public_key_file = 'user2_public_key.pem'

        generate_rsa_key(key_size, private_key_file, public_key_file)
        print(f'Clés RSA générées pour l\'utilisateur 2: {private_key_file} (privée), {public_key_file} (publique)')

        message = input("Entrez le message à chiffrer : ")
        encrypted_file = 'encrypted_message.bin'
        decrypted_file = 'decrypted_message.txt'

        encrypt_message(public_key_file, message, encrypted_file)
        print(f'Message chiffré dans le fichier : {encrypted_file}')

        decrypt_message(private_key_file, encrypted_file, decrypted_file)
        print(f'Message déchiffré dans le fichier : {decrypted_file}')
        
        with open(decrypted_file, 'r') as file:
            decrypted_message = file.read()
            print(f'Message déchiffré : {decrypted_message}')

        # Nettoyage des fichiers temporaires
        os.remove(encrypted_file)
        os.remove(decrypted_file)
    else:
        print("Veuillez installer OpenSSL et ajouter son répertoire 'bin' au PATH.")
