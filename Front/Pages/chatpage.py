import tkinter as tk
from tkinter import ttk
import sys
sys.path.append(".")
from Backend.discussions import get_discussions_for_user, send_message as backend_send_message, get_messages, get_discussion_by_participants, encrypt_message, create_discussion
from Backend.users import get_user_list, get_user_id_from_username

class ChatPage(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user

        self.create_widgets()
        self.update_existing_discussions()

    def create_widgets(self):
        left_frame = tk.Frame(self)
        self.notebook = ttk.Notebook(self)

        user_list_label = tk.Label(left_frame, text="Existing Discussions", font=("Helvetica", 16))
        self.user_listbox = tk.Listbox(left_frame)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_user_select)
        new_chat_button = tk.Button(left_frame, text="New Chat", command=self.create_new_chat_tab)
        logout_button = tk.Button(left_frame, text="Logout", command=lambda: self.controller.show_frame("HomePage"))

        user_list_label.pack(fill="x")
        self.user_listbox.pack(fill="both", expand=True)
        new_chat_button.pack(fill="x")
        logout_button.pack(fill="x")

        left_frame.pack(side=tk.LEFT, fill='y')
        self.notebook.pack(side=tk.RIGHT, fill='both', expand=True)

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

    def start_chat(self, selected_user):
        if selected_user:
            self.create_chat_tab(selected_user)
            self.notebook.select(self.notebook.index("end")-1)

    def create_chat_tab(self, chat_partner):
        if any(self.notebook.tab(tab, option="text") == chat_partner for tab in self.notebook.tabs()):
            return  # Prevent opening multiple tabs for the same chat

        tab = tk.Frame(self.notebook)
        chat_area = tk.Text(tab, state='disabled', wrap='word')
        chat_area.pack(fill="both", expand=True)

        message_entry_frame = tk.Frame(tab)
        message_entry = tk.Entry(message_entry_frame)
        message_entry.pack(side=tk.LEFT, fill="x", expand=True)
        send_button = tk.Button(message_entry_frame, text="Send", command=lambda: self.send_message(message_entry, chat_partner, chat_area))
        send_button.pack(side=tk.RIGHT)
        message_entry_frame.pack(fill="x")

        self.notebook.add(tab, text=chat_partner)  # Set the chat partner's name directly as the tab text

        # Add a close button within the tab content area instead of the tab label
        close_button = tk.Button(tab, text="X", command=lambda: self.close_tab(tab))
        close_button.pack(side="top", anchor="e")

    def close_tab(self, tab):
        self.notebook.forget(tab)
        tab.destroy()

    def on_user_select(self, event):
        selection = self.user_listbox.curselection()
        if selection:
            selected_user = self.user_listbox.get(selection[0])
            self.create_chat_tab(selected_user)

    def update_existing_discussions(self):
        self.user_listbox.delete(0, tk.END)
        existing_discussions = self.get_existing_discussions(self.current_user)
        for discussion in existing_discussions:
            self.user_listbox.insert(tk.END, discussion)

    def get_existing_discussions(self, current_user):
        user_id = get_user_id_from_username(current_user)
        discussions = get_discussions_for_user(user_id)
        return [d['partner_name'] for d in discussions]