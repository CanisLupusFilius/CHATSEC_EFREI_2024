import tkinter as tk
from tkinter import messagebox
from utils import verify_login

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Login Page", font=("Helvetica", 18))
        label.pack(pady=10, padx=10)
        
        username_label = tk.Label(self, text="Username")
        username_label.pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        
        password_label = tk.Label(self, text="Password")
        password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.pack(pady=5)
        
        back_button = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage"))
        back_button.pack(pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if verify_login(username, password):
            messagebox.showinfo("Login Info", "Successfully logged in!")
            self.controller.current_user = username
            self.controller.show_frame("ChatPage")
        else:
            messagebox.showerror("Login Error", "Invalid credentials!")
