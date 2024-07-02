import psycopg2
from datetime import datetime
from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
from cryptography.hazmat.backends import default_backend

def encrypt_message(message, public_key_pem):
    public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
    session_key = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(session_key), modes.CFB8(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
    encrypted_session_key = public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message, encrypted_session_key, iv

def decrypt_message(encrypted_message, encrypted_session_key, private_key_pem, iv):
    
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
    session_key = private_key.decrypt(
        encrypted_session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    cipher = Cipher(algorithms.AES(session_key), modes.CFB8(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return decrypted_message.decode('utf-8')



def create_discussion(title, participants):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="831411",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO discussions (titre) VALUES (%s) RETURNING discussion_id", (title,))
    discussion_id = cursor.fetchone()[0]

    # Add participants
    for user_id in participants:
        cursor.execute("INSERT INTO participants (discussion_id, utilisateur_id) VALUES (%s, %s)", (discussion_id, user_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    return discussion_id

def send_message(sender_id, discussion_id, encrypted_content, session_key,iv):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="831411",
        host="localhost"
    )
    cursor = conn.cursor()

    # Insérer le message chiffré dans la base de données
    cursor.execute(
        "INSERT INTO messages (discussion_id, utilisateur_id, contenu_chiffre, cle_session_chiffree,iv) VALUES (%s, %s, %s, %s, %s)",
        (discussion_id, sender_id, encrypted_content, session_key,iv)
    )
    
    conn.commit()
    cursor.close()
    conn.close()




def get_messages(discussion_id, user_id):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="831411",
        host="localhost"
    )
    cursor = conn.cursor()
    
    # Récupérer la clé privée RSA de l'utilisateur
    cursor.execute("SELECT cle_privee_rsa_chiffree FROM utilisateurs WHERE utilisateur_id = %s", (user_id,))
    private_key_pem = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT m.contenu_chiffre, m.cle_session_chiffree, m.date_envoi, u.nom ,m.iv
        FROM messages m
        JOIN utilisateurs u ON m.utilisateur_id = u.utilisateur_id
        WHERE m.discussion_id = %s
        ORDER BY m.date_envoi
    """, (discussion_id,))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Decrypt the messages
    decrypted_messages = []
    for message in messages:
        encrypted_message = bytes(message[0])  # Convert memoryview to bytes
        encrypted_session_key = bytes(message[1])
        iv = bytes(message[4])
        decrypted_message = decrypt_message(encrypted_message, encrypted_session_key, private_key_pem, iv)
        decrypted_messages.append({
            'message': decrypted_message,
            'session_key': encrypted_session_key,
            'date': message[2],
            'sender': message[3]
        })
    
    return decrypted_messages



def get_discussion_by_participants(participant_ids):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="831411",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.discussion_id
        FROM discussions d
        JOIN participants p ON d.discussion_id = p.discussion_id
        GROUP BY d.discussion_id
        HAVING ARRAY_AGG(p.utilisateur_id ORDER BY p.utilisateur_id) = ARRAY[%s, %s]
    """, tuple(sorted(participant_ids)))
    discussion = cursor.fetchone()
    cursor.close()
    conn.close()
    return discussion[0] if discussion else None

def get_public_key_from_user_id(user_id):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="831411",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT cle_publique_rsa FROM utilisateurs WHERE utilisateur_id = %s", (user_id,))
    public_key_pem = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return public_key_pem


def get_discussions_for_user(user_id):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="831411",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.discussion_id, array_agg(p.utilisateur_id) as participants, MAX(m.date_envoi) as last_message_date
        FROM discussions d
        JOIN participants p ON d.discussion_id = p.discussion_id
        JOIN messages m ON d.discussion_id = m.discussion_id
        WHERE d.discussion_id IN (
            SELECT discussion_id FROM participants WHERE utilisateur_id = %s
        )
        GROUP BY d.discussion_id
        ORDER BY last_message_date DESC
    """, (user_id,))
    discussions = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{'discussion_id': discussion[0], 'participants': discussion[1], 'last_message_date': discussion[2].strftime("%Y-%m-%d %H:%M:%S")} for discussion in discussions]
