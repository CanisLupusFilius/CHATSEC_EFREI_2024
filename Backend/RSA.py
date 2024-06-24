import subprocess

def generate_rsa_key(key_size, private_key_file, public_key_file):
    # Commande pour générer la clé privée RSA
    subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-out', private_key_file, '-pkeyopt', f'rsa_keygen_bits:{key_size}'])

    # Commande pour extraire la clé publique de la clé privée
    subprocess.run(['openssl', 'rsa', '-pubout', '-in', private_key_file, '-out', public_key_file])

# Taille de la clé en bits
key_size = 2048

# Fichiers de sortie pour les clés privée et publique
private_key_file = 'private_key.pem'
public_key_file = 'public_key.pem'

# Générer les clés
generate_rsa_key(key_size, private_key_file, public_key_file)

print(f'Clés RSA générées: {private_key_file} (privée), {public_key_file} (publique)')
