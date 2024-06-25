import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import sys
sys.path.append(".")
from Backend.discussions import get_discussions_for_user, send_message as backend_send_message, get_messages, get_discussion_by_participants, encrypt_message, create_discussion, decrypt_message
from Backend.users import get_user_list, get_user_id_from_username

class ChatPage(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user
        self.chat_partner = None  # Initialize chat_partner variable
        self.chat_area = None  # Initialize chat_area variable

        self.create_widgets()
        self.update_existing_discussions()

    def create_widgets(self):
        left_frame = tk.Frame(self)
        right_frame = tk.Frame(self)  # Frame to hold the notebook and the close button
        self.notebook = ttk.Notebook(right_frame)

        user_list_label = tk.Label(left_frame, text="CHATSEC", font=("Bodoni", 16))
        self.user_listbox = tk.Listbox(left_frame)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_user_select)
        new_chat_button = tk.Button(left_frame, text="New Chat", command=self.create_new_chat_tab_if_absent)
        logout_button = tk.Button(left_frame, text="Logout", command=lambda: self.controller.show_frame("HomePage"))

        user_list_label.pack(fill="x")
        self.user_listbox.pack(fill="both", expand=True)
        new_chat_button.pack(fill="x")
        logout_button.pack(fill="x")

        # Initialize the chat area here but pack it in the create_chat_tab method
        self.chat_area = tk.Text(right_frame, state='disabled', wrap='word')
        self.chat_area.tag_configure('sent', justify='right', lmargin1=100, rmargin=10, background='#DCF8C6')
        self.chat_area.tag_configure('received', justify='left', lmargin1=10, rmargin=100, background='#FFFFFF')
        self.chat_area.tag_configure('date', justify='center', font=('Helvetica', 8), foreground='gray')

        # Place close button at the top right of the right_frame
        close_button = tk.Button(right_frame, text="X", command=self.close_current_tab)
        close_button.pack(side="top", anchor="e")

        self.notebook.pack(fill="both", expand=True)

        left_frame.pack(side=tk.LEFT, fill='y')
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

    def create_new_chat_tab_if_absent(self):
        if "New Chat" not in (self.notebook.tab(tab, "text") for tab in self.notebook.tabs()):
            self.create_new_chat_tab()

    def create_new_chat_tab(self):
        new_chat_tab = tk.Frame(self.notebook)
        user_list = tk.Listbox(new_chat_tab)
        all_users = get_user_list()
        available_users = [user for user in all_users if user != self.current_user]
        for user in available_users:
            user_list.insert(tk.END, user)
        user_list.pack(fill="both", expand=True)
        start_button = tk.Button(new_chat_tab, text="Start Chatting", command=lambda: self.start_chat(user_list.get(user_list.curselection())))
        start_button.pack(fill="x")
        self.notebook.add(new_chat_tab, text="New Chat")
        self.notebook.select(new_chat_tab)

    def start_chat(self, selected_user):
        if selected_user:
            self.create_chat_tab(selected_user)

    def create_chat_tab(self, chat_partner):
        if any(self.notebook.tab(tab, option="text") == chat_partner for tab in self.notebook.tabs()):
            return  # Prevent opening multiple tabs for the same chat

        tab = tk.Frame(self.notebook)
        self.chat_area = tk.Text(tab, state='disabled', wrap='word')
        self.chat_area.pack(fill="both", expand=True)

        message_entry_frame = tk.Frame(tab)
        self.message_entry = tk.Entry(message_entry_frame)  # Store self.message_entry
        self.message_entry.pack(side=tk.LEFT, fill="x", expand=True)
        send_button = tk.Button(message_entry_frame, text="Send", command=lambda: self.send_message(self.message_entry.get()))
        send_button.pack(side=tk.RIGHT)
        message_entry_frame.pack(fill="x")

        self.notebook.add(tab, text=chat_partner)
        self.notebook.select(tab)
        self.chat_partner = chat_partner  # Set chat_partner

        # Update messages for the selected chat partner
        self.update_messages()

    def send_message(self, message):
        if self.chat_partner and message:
            sender_id = get_user_id_from_username(self.current_user)
            recipient_id = get_user_id_from_username(self.chat_partner)
            discussion_id = get_discussion_by_participants([sender_id, recipient_id])
            if not discussion_id:
                discussion_id = create_discussion(f"{self.current_user}-{self.chat_partner}", [sender_id, recipient_id])
            encrypted_content, session_key = encrypt_message(message)
            backend_send_message(sender_id, discussion_id, encrypted_content, session_key)
            self.update_messages()
            self.update_existing_discussions()
            self.message_entry.delete(0, tk.END)

            # Update messages for the selected chat partner
            self.update_messages()

    def close_current_tab(self):
        current_tab = self.notebook.select()
        if current_tab:
            self.notebook.forget(current_tab)

    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            selected_user = self.user_listbox.get(selection[0])
            self.create_chat_tab(selected_user)

    def update_messages(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        last_message_time = None
        last_chat_date = ""
        today = datetime.now().date()
        if self.chat_partner:
            messages = self.get_messages_between_users(self.current_user, self.chat_partner)
            for msg in messages:
                msg_date = msg['date']  # This is already a datetime object
                if last_message_time is None or msg_date - last_message_time >= timedelta(minutes=15):
                    if msg_date.date() == today:
                        display_date = msg_date.strftime("%I:%M %p")
                    else:
                        display_date = msg_date.strftime("%d/%m/%Y")
                    self.chat_area.insert(tk.END, f"{display_date}\n", 'date')
                tag = 'sent' if msg['sender'] == self.current_user else 'received'
                self.chat_area.insert(tk.END, f"{msg['message']}\n", tag)
                last_message_time = msg_date
                last_chat_date = msg_date.strftime("%d/%m/%Y") if msg_date.date() != today else msg_date.strftime("%I:%M %p")
        self.chat_area.config(state='disabled')

    def get_existing_discussions(self, current_user):
        user_id = get_user_id_from_username(current_user)
        discussions = get_discussions_for_user(user_id)
        return [d['partner_name'] for d in discussions]

    def get_messages_between_users(self, current_user, chat_partner):
        current_user_id = get_user_id_from_username(current_user)
        chat_partner_id = get_user_id_from_username(chat_partner)
        discussion_id = get_discussion_by_participants([current_user_id, chat_partner_id])
        if not discussion_id:
            return []
        messages = get_messages(discussion_id)
        return messages
    
    def update_existing_discussions(self):
        existing_discussions = self.get_existing_discussions(self.current_user)
        self.user_listbox.delete(0, tk.END)
        for user in existing_discussions:
            self.user_listbox.insert(tk.END, user)
