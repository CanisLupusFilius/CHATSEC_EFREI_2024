import tkinter as tk
from utils import get_user_list, send_message, get_messages_for_user

class ChatPage(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user
        
        label = tk.Label(self, text="Chat Page", font=("Helvetica", 18))
        label.pack(pady=10, padx=10)
        
        self.chat_area = tk.Text(self, state='disabled')
        self.chat_area.pack(pady=10)
        
        self.recipient_var = tk.StringVar(self)
        self.recipient_var.set("Select recipient")
        
        self.recipient_menu = tk.OptionMenu(self, self.recipient_var, *get_user_list())
        self.recipient_menu.pack(pady=5)
        
        self.message_entry = tk.Entry(self)
        self.message_entry.pack(pady=5)
        
        send_button = tk.Button(self, text="Send", command=self.send_message)
        send_button.pack(pady=5)
        
        logout_button = tk.Button(self, text="Logout", command=lambda: controller.show_frame("HomePage"))
        logout_button.pack(pady=5)
        
        self.update_messages()
    
    def send_message(self):
        recipient = self.recipient_var.get()
        message = self.message_entry.get()
        if recipient != "Select recipient" and message:
            send_message(self.current_user, recipient, message)
            self.update_messages()
            self.message_entry.delete(0, tk.END)
    
    def update_messages(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        messages = get_messages_for_user(self.current_user)
        for msg in messages:
            self.chat_area.insert(tk.END, f"{msg['sender']} to {msg['recipient']}: {msg['message']}\n")
        self.chat_area.config(state='disabled')
