import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import sys
sys.path.append(".")
from Backend.discussions import get_discussions_for_user, send_message as backend_send_message, get_messages, get_discussion_by_participants, encrypt_message
from Backend.users import get_user_list, get_user_id_from_username

class ChatPage(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user  # Store the current user
        self.chat_partner = None  # Store the chat partner

        self.create_widgets()
        self.update_existing_discussions()

    def create_widgets(self):
        left_frame = tk.Frame(self)
        right_frame = tk.Frame(self)

        user_list_label = tk.Label(left_frame, text="Existing Discussions", font=("Helvetica", 16))
        self.user_combobox = ttk.Combobox(left_frame, state="readonly")
        self.user_listbox = tk.Listbox(left_frame)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_user_select)
        self.user_combobox.bind("<<ComboboxSelected>>", self.start_chat)

        self.update_user_combobox()

        style = ttk.Style()
        style.configure("TCombobox", padding=5, relief="flat")
        logout_button = tk.Button(left_frame, text="Logout", command=lambda: self.controller.show_frame("HomePage"))

        user_list_label.pack(fill="x")
        self.user_listbox.pack(fill="both", expand=True)
        logout_button.pack(fill="x")

        # Banner Frame
        banner_frame = tk.Frame(right_frame, bg="lightgray", height=30)
        self.chat_partner_label = tk.Label(banner_frame, text="", anchor="w", bg="lightgray", font=("Helvetica", 12))
        self.last_chat_date_label = tk.Label(banner_frame, text="", anchor="e", bg="lightgray", font=("Helvetica", 12))
        self.chat_partner_label.pack(side=tk.LEFT, padx=10)
        self.last_chat_date_label.pack(side=tk.RIGHT, padx=10)
        banner_frame.pack(fill="x")

        self.chat_area = tk.Text(right_frame, state='disabled', wrap='word')
        self.chat_area.tag_configure('sent', justify='right', background='#DCF8C6')
        self.chat_area.tag_configure('received', justify='left', background='#FFFFFF')
        self.chat_area.tag_configure('date', justify='center', font=('Helvetica', 8), foreground='gray')
        message_entry_frame = tk.Frame(right_frame)
        self.message_entry = tk.Entry(message_entry_frame)
        send_button = tk.Button(message_entry_frame, text="Send", command=self.send_message)

        self.chat_area.pack(fill="both", expand=True)
        self.message_entry.pack(side=tk.LEFT, fill="x", expand=True)
        send_button.pack(side=tk.RIGHT)
        message_entry_frame.pack(fill="x")

        left_frame.pack(side=tk.LEFT, fill='y')
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

    def update_user_combobox(self):
        all_users = get_user_list()
        existing_discussions = self.get_existing_discussions(self.current_user)
        available_users = [user for user in all_users if user != self.current_user and user not in existing_discussions]

        if available_users:
            self.user_combobox['values'] = available_users
            self.user_combobox.set("New Chat")
            self.user_combobox.pack(fill="x")
        else:
            self.user_combobox.pack_forget()

    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            selected_user = self.user_listbox.get(selection[0])
            self.chat_partner = selected_user
            self.update_messages()

    def start_chat(self, event):
        selected_user = self.user_combobox.get()
        if selected_user != "New Chat":
            self.chat_partner = selected_user
            self.update_messages()
            self.update_existing_discussions()

    def send_message(self):
        message = self.message_entry.get()
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

    def update_messages(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        last_message_time = None
        last_chat_date = ""
        today = datetime.now().date()
        if self.chat_partner:
            messages = self.get_messages_between_users(self.current_user, self.chat_partner)
            for msg in messages:
                msg_date = datetime.strptime(msg['date'], "%Y-%m-%d %H:%M:%S")
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
        self.update_banner(last_chat_date)

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

        self.update_user_combobox()

    def update_banner(self, last_chat_date):
        if self.chat_partner:
            self.chat_partner_label.config(text=f"Chat with: {self.chat_partner}")
            self.last_chat_date_label.config(text=f"Last chat date: {last_chat_date}")
        else:
            self.chat_partner_label.config(text="")
            self.last_chat_date_label.config(text="")
