import psycopg2
from datetime import datetime
from cryptography.fernet import Fernet

def create_discussion(title, participants):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="8314",
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

def send_message(sender_id, discussion_id, encrypted_content, encrypted_session_key):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="8314",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (discussion_id, utilisateur_id, contenu_chiffre, cle_session_chiffree) VALUES (%s, %s, %s, %s)",
        (discussion_id, sender_id, encrypted_content, encrypted_session_key)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_messages(discussion_id):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="8314",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.contenu_chiffre, m.cle_session_chiffree, m.date_envoi, u.nom
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
        session_key = message[1]
        decrypted_message = decrypt_message(encrypted_message, session_key)
        decrypted_messages.append({
            'message': decrypted_message,
            'session_key': session_key,
            'date': message[2],
            'sender': message[3]
        })
    
    return decrypted_messages


def get_discussion_by_participants(participant_ids):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="8314",
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

def encrypt_message(message):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    if not message:
        return None, None
    encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
    return encrypted_message, key


def decrypt_message(encrypted_message, session_key):
    cipher_suite = Fernet(session_key)
    decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
    return decrypted_message


def get_discussions_for_user(user_id):
    conn = psycopg2.connect(
        dbname="bdd",
        user="postgres",
        password="8314",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.nom, MAX(m.date_envoi) as last_message_date
        FROM discussions d
        JOIN participants p ON d.discussion_id = p.discussion_id
        JOIN utilisateurs u ON u.utilisateur_id = p.utilisateur_id
        JOIN messages m ON d.discussion_id = m.discussion_id
        WHERE p.utilisateur_id != %s AND d.discussion_id IN (
            SELECT discussion_id FROM participants WHERE utilisateur_id = %s
        )
        GROUP BY u.nom
        ORDER BY last_message_date DESC
    """, (user_id, user_id))
    discussions = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{'partner_name': discussion[0], 'last_message_date': discussion[1].strftime("%Y-%m-%d %H:%M:%S")} for discussion in discussions]