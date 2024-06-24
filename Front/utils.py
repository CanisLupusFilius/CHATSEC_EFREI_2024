import os
from datetime import datetime

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

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MESSAGE_DATA_FILE, 'a') as file:
        file.write(f"{sender}|{recipient}|{message}|{current_date}\n")

def get_messages_between_users(user1, user2):
    if not os.path.exists(MESSAGE_DATA_FILE):
        return []

    with open(MESSAGE_DATA_FILE, 'r') as file:
        messages = file.readlines()
    
    message_list = []
    for msg in messages:
        try:
            sender, recipient, message, date = msg.strip().split('|')
            if (sender == user1 and recipient == user2) or (sender == user2 and recipient == user1):
                message_list.append({'sender': sender, 'recipient': recipient, 'message': message, 'date': date})
        except ValueError:
            # Handle the error or log it
            print(f"Skipping malformed message: {msg.strip()}")
    
    return message_list

def get_existing_discussions(current_user):
    if not os.path.exists(MESSAGE_DATA_FILE):
        return []

    with open(MESSAGE_DATA_FILE, 'r') as file:
        messages = file.readlines()
    
    discussions = set()
    for msg in messages:
        try:
            sender, recipient, _, _ = msg.strip().split('|')
            if sender == current_user:
                discussions.add(recipient)
            elif recipient == current_user:
                discussions.add(sender)
        except ValueError:
            # Handle the error or log it
            print(f"Skipping malformed message: {msg.strip()}")
    
    return list(discussions)
