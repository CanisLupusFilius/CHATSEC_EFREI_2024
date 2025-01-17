import tkinter as tk
from tkinter import messagebox
import sys
sys.path.append(".")
from Backend.users import login_back

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def create_widgets(self):
        label = tk.Label(self, text="Login Page", font=("Helvetica", 18))
        label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ns")

        username_label = tk.Label(self, text="Username")
        username_label.grid(row=1, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=1, column=1, pady=5, sticky="w")

        password_label = tk.Label(self, text="Password")
        password_label.grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, sticky="w")

        login_button = tk.Button(self, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="n")

        back_button = tk.Button(self, text="Back to Home", command=lambda: self.controller.show_frame("HomePage"))
        back_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="n")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if login_back(username, password):
            messagebox.showinfo("Login Info", "Successfully logged in!")
            self.controller.current_user = username
            self.controller.show_frame("ChatPage")
        else:
            messagebox.showerror("Login Error", "Invalid credentials!")