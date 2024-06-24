import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Home Page", font=("Helvetica", 18))
        label.pack(pady=10, padx=10)
        
        login_button = tk.Button(self, text="Go to Login Page", command=lambda: controller.show_frame("LoginPage"))
        login_button.pack()
        
        signup_button = tk.Button(self, text="Go to Signup Page", command=lambda: controller.show_frame("SignupPage"))
        signup_button.pack()
