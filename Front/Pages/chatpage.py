import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import sys
sys.path.append(".")
from Backend.discussions import (
    get_discussions_for_user,
    send_message as backend_send_message,
    get_messages,
    get_discussion_by_participants,
    encrypt_message,
    create_discussion,
    decrypt_message,
)
from Backend.users import get_user_list, get_user_id_from_username


class ChatPage(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user
        self.chat_partner = None
        self.tabs = {}
        self.create_widgets()
        self.update_existing_discussions()
        self.create_new_chat_tab()  # Ensure the "New Chat" tab is always open

    def create_widgets(self):
        left_frame = tk.Frame(self)
        right_frame = tk.Frame(self)

        self.notebook = ttk.Notebook(right_frame)

        user_list_label = tk.Label(left_frame, text="CHATSEC", font=("Bodoni", 16))

        # Opened conversations
        opened_label = tk.Label(left_frame, text="Opened Conversations", font=("Helvetica", 12, "bold"))
        self.opened_listbox = tk.Listbox(left_frame)
        self.opened_listbox.bind("<<ListboxSelect>>", self.on_opened_select)

        # Unopened conversations
        unopened_label = tk.Label(left_frame, text="Unopened Conversations", font=("Helvetica", 12, "bold"))
        self.unopened_listbox = tk.Listbox(left_frame)
        self.unopened_listbox.bind("<<ListboxSelect>>", self.on_unopened_select)

        logout_button = tk.Button(left_frame, text="Logout", command=lambda: self.controller.show_frame("HomePage"))

        user_list_label.pack(fill="x")
        opened_label.pack(fill="x")
        self.opened_listbox.pack(fill="both", expand=True)
        unopened_label.pack(fill="x")
        self.unopened_listbox.pack(fill="both", expand=True)
        logout_button.pack(fill="x")

        self.notebook.pack(fill="both", expand=True)

        left_frame.pack(side=tk.LEFT, fill="y")
        right_frame.pack(side=tk.RIGHT, fill="both", expand=True)

    def create_new_chat_tab(self):
        if "New Chat" in (self.notebook.tab(tab, "text") for tab in self.notebook.tabs()):
            return  # Prevent creating multiple "New Chat" tabs

        new_chat_tab = tk.Frame(self.notebook)
        user_list = tk.Listbox(new_chat_tab)
        all_users = get_user_list()
        available_users = [user for user in all_users if user != self.current_user and user not in self.get_existing_discussions(self.current_user)]
        for user in available_users:
            user_list.insert(tk.END, user)
        user_list.pack(fill="both", expand=True)
        start_button = tk.Button(new_chat_tab, text="Start Chatting", command=lambda: self.start_chat(user_list.get(user_list.curselection())))
        start_button.pack(fill="x")
        
        if self.notebook.tabs():
            self.notebook.insert(0, new_chat_tab, text="New Chat")
        else:
            self.notebook.add(new_chat_tab, text="New Chat")
        
        self.notebook.select(new_chat_tab)  # Automatically switch to the "New Chat" tab

    def start_chat(self, selected_user):
        if selected_user:
            self.create_chat_tab(selected_user)

    def create_chat_tab(self, chat_partner):
        if chat_partner in self.tabs:
            self.notebook.select(self.tabs[chat_partner]["tab"])
            return  # Prevent opening multiple tabs for the same chat

        tab = tk.Frame(self.notebook)

        # Create a frame for the header (chat partner name and close button)
        header_frame = tk.Frame(tab)
        chat_partner_label = tk.Label(header_frame, text=chat_partner, font=("Helvetica", 12))
        close_button = tk.Button(header_frame, text="X", command=lambda: self.close_specific_tab(chat_partner))

        chat_partner_label.pack(side=tk.LEFT, padx=5)
        close_button.pack(side=tk.RIGHT, padx=5)
        header_frame.pack(fill="x")

        chat_area = tk.Text(tab, state="disabled", wrap="word")
        chat_area.pack(fill="both", expand=True)
        chat_area.tag_configure("sent", justify="right", lmargin1=100, rmargin=10, background="#DCF8C6")
        chat_area.tag_configure("received", justify="left", lmargin1=10, rmargin=100, background="#FFFFFF")
        chat_area.tag_configure("date", justify="center", font=("Helvetica", 8), foreground="gray")

        message_entry_frame = tk.Frame(tab)
        message_entry = tk.Entry(message_entry_frame)
        message_entry.pack(side=tk.LEFT, fill="x", expand=True)
        send_button = tk.Button(message_entry_frame, text="Send", command=lambda: self.send_message(chat_partner, message_entry.get()))
        send_button.pack(side=tk.RIGHT)
        message_entry_frame.pack(fill="x")

        self.notebook.add(tab, text=chat_partner)
        self.notebook.select(tab)  # Automatically switch to the newly created tab

        self.tabs[chat_partner] = {
            "tab": tab,
            "chat_area": chat_area,
            "message_entry": message_entry,
        }
        self.chat_partner = chat_partner

        self.update_messages(chat_partner)
        self.update_existing_discussions()

    def send_message(self, chat_partner, message):
        if chat_partner and message:
            sender_id = get_user_id_from_username(self.current_user)
            recipient_id = get_user_id_from_username(chat_partner)
            discussion_id = get_discussion_by_participants([sender_id, recipient_id])
            if not discussion_id:
                discussion_id = create_discussion(f"{self.current_user}-{chat_partner}", [sender_id, recipient_id])
            encrypted_content, session_key = encrypt_message(message)
            backend_send_message(sender_id, discussion_id, encrypted_content, session_key)
            self.update_messages(chat_partner)
            self.update_existing_discussions()
            self.tabs[chat_partner]["message_entry"].delete(0, tk.END)

    def close_specific_tab(self, chat_partner):
        if chat_partner in self.tabs:
            tab_info = self.tabs[chat_partner]
            self.notebook.forget(tab_info["tab"])
            del self.tabs[chat_partner]
            self.update_existing_discussions()

    def close_current_tab(self):
        current_tab = self.notebook.select()
        if current_tab and self.notebook.tab(current_tab, "text") != "New Chat":
            chat_partner = self.notebook.tab(current_tab, "text")
            self.notebook.forget(current_tab)
            del self.tabs[chat_partner]
            self.update_existing_discussions()

    def on_opened_select(self, event):
        selection = self.opened_listbox.curselection()
        if selection:
            selected_user = self.opened_listbox.get(selection[0])
            self.notebook.select(self.tabs[selected_user]["tab"])

    def on_unopened_select(self, event):
        selection = self.unopened_listbox.curselection()
        if selection:
            selected_user = self.unopened_listbox.get(selection[0])
            self.create_chat_tab(selected_user)

    def apply_message_tag(self, chat_area, message, sender):
        tag = "sent" if sender == self.current_user else "received"
        chat_area.insert(tk.END, f"{message}\n", tag)

    def update_messages(self, chat_partner):
        if chat_partner not in self.tabs:
            return

        chat_area = self.tabs[chat_partner]["chat_area"]
        chat_area.config(state="normal")
        chat_area.delete(1.0, tk.END)
        last_message_time = None
        today = datetime.now().date()
        messages = self.get_messages_between_users(self.current_user, chat_partner)
        for msg in messages:
            msg_date = msg["date"]
            if last_message_time is None or msg_date - last_message_time >= timedelta(minutes=15):
                display_date = msg_date.strftime("%I:%M %p") if msg_date.date() == today else msg_date.strftime("%d/%m/%Y")
                chat_area.insert(tk.END, f"{display_date}\n", "date")
            self.apply_message_tag(chat_area, msg["message"], msg["sender"])
            last_message_time = msg_date
        chat_area.config(state="disabled")

    def get_existing_discussions(self, current_user):
        user_id = get_user_id_from_username(current_user)
        discussions = get_discussions_for_user(user_id)
        return [d["partner_name"] for d in discussions]

    def get_messages_between_users(self, current_user, chat_partner):
        current_user_id = get_user_id_from_username(current_user)
        chat_partner_id = get_user_id_from_username(chat_partner)
        discussion_id = get_discussion_by_participants([current_user_id, chat_partner_id])
        if not discussion_id:
            return []
        messages = get_messages(discussion_id)
        return messages

    def update_existing_discussions(self):
        all_discussions = self.get_existing_discussions(self.current_user)
        opened_discussions = [user for user in all_discussions if user in self.tabs]
        unopened_discussions = [user for user in all_discussions if user not in self.tabs]

        self.opened_listbox.delete(0, tk.END)
        for user in opened_discussions:
            self.opened_listbox.insert(tk.END, user)

        self.unopened_listbox.delete(0, tk.END)
        for user in unopened_discussions:
            self.unopened_listbox.insert(tk.END, user)