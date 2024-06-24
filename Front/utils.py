import os

USER_DATA_FILE = "users.txt"
MESSAGE_DATA_FILE = "messages.txt"

def register_user(username, password):
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w') as file:
            pass

    with open(USER_DATA_FILE, 'r') as file:
        users = file.readlines()
        
    for user in users:
        stored_username, _ = user.strip().split(':')
        if stored_username == username:
            return False

    with open(USER_DATA_FILE, 'a') as file:
        file.write(f"{username}:{password}\n")
    
    return True

def verify_login(username, password):
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, 'r') as file:
        users = file.readlines()
    
    for user in users:
        stored_username, stored_password = user.strip().split(':')
        if stored_username == username and stored_password == password:
            return True
    
    return False

def get_user_list():
    if not os.path.exists(USER_DATA_FILE):
        return []

    with open(USER_DATA_FILE, 'r') as file:
        users = file.readlines()
    
    user_list = [user.strip().split(':')[0] for user in users]
    return user_list

def send_message(sender, recipient, message):
    if not os.path.exists(MESSAGE_DATA_FILE):
        with open(MESSAGE_DATA_FILE, 'w') as file:
            pass

    with open(MESSAGE_DATA_FILE, 'a') as file:
        file.write(f"{sender}:{recipient}:{message}\n")

def get_messages_for_user(user):
    if not os.path.exists(MESSAGE_DATA_FILE):
        return []

    with open(MESSAGE_DATA_FILE, 'r') as file:
        messages = file.readlines()
    
    message_list = []
    for msg in messages:
        try:
            sender, recipient, message = msg.strip().split(':')
            if user == sender or user == recipient:
                message_list.append({'sender': sender, 'recipient': recipient, 'message': message})
        except ValueError:
            print(f"Skipping malformed message: {msg.strip()}")
    
    return message_list
