import tkinter as tk
from tkinter import messagebox, ttk
from utils import get_user_list, send_message, get_messages_between_users, get_existing_discussions

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

        user_list = get_user_list()
        if self.current_user in user_list:
            user_list.remove(self.current_user)  # Remove the current user from the list

        self.user_combobox['values'] = user_list
        self.user_combobox.set("New Chat")

        style = ttk.Style()
        style.configure("TCombobox", padding=5, relief="flat")
        logout_button = tk.Button(left_frame, text="Logout", command=lambda: self.controller.show_frame("HomePage"))

        user_list_label.pack(fill="x")
        self.user_listbox.pack(fill="both", expand=True)
        self.user_combobox.pack(fill="x")
        logout_button.pack(fill="x")


        self.chat_area = tk.Text(right_frame, state='disabled', wrap='word')
        message_entry_frame = tk.Frame(right_frame)
        self.message_entry = tk.Entry(message_entry_frame)
        send_button = tk.Button(message_entry_frame, text="Send", command=self.send_message)

        self.chat_area.pack(fill="both", expand=True)
        self.message_entry.pack(side=tk.LEFT, fill="x", expand=True)
        send_button.pack(side=tk.RIGHT)
        message_entry_frame.pack(fill="x")


        left_frame.pack(side=tk.LEFT, fill='y')
        right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

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
            send_message(self.current_user, self.chat_partner, message)
            self.update_messages()
            self.update_existing_discussions()
            self.message_entry.delete(0, tk.END)

    def update_messages(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        if self.chat_partner:
            messages = get_messages_between_users(self.current_user, self.chat_partner)
            for msg in messages:
                self.chat_area.insert(tk.END, f"{msg['sender']} to {msg['recipient']}: {msg['message']}\n")
        self.chat_area.config(state='disabled')

    def update_existing_discussions(self):
        existing_discussions = get_existing_discussions(self.current_user)
        self.user_listbox.delete(0, tk.END)
        for user in existing_discussions:
            self.user_listbox.insert(tk.END, user)
