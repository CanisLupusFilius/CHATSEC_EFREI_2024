import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure_gui()
        self.create_widgets()

    def configure_gui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        label = tk.Label(self, text="Home Page", font=("Helvetica", 18))
        label.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        login_button = tk.Button(self, text="Go to Login Page", command=lambda: self.controller.show_frame("LoginPage"))
        login_button.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        signup_button = tk.Button(self, text="Go to Signup Page", command=lambda: self.controller.show_frame("SignupPage"))
        signup_button.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
