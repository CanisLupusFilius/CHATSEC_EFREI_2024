import tkinter as tk
from tkinter import messagebox
from utils import register_user

class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Signup Page", font=("Helvetica", 18))
        label.pack(pady=10, padx=10)
        
        username_label = tk.Label(self, text="Username")
        username_label.pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        
        password_label = tk.Label(self, text="Password")
        password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        signup_button = tk.Button(self, text="Sign Up", command=self.signup)
        signup_button.pack(pady=5)
        
        back_button = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage"))
        back_button.pack(pady=5)
    
    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if register_user(username, password):
            messagebox.showinfo("Signup Info", f"Account created for {username}!")
        else:
            messagebox.showerror("Signup Error", "Username already exists!")
