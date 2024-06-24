import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from ttkthemes import ThemedTk
from Front.Pages.home import HomePage
from Front.Pages.login import LoginPage
from Front.Pages.signup import SignupPage
from Front.Pages.chatpage import ChatPage

class App(ThemedTk):
    def __init__(self):
        super().__init__(theme="equilux")
        self.title("CHATSEC")
        self.geometry("900x600")  # Set the initial size of the window
        self.minsize(800, 600)
        self.frames = {}
        self.current_user = None  # To store the current logged-in user

        # Create a container frame to hold all other frames
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for F in (HomePage, LoginPage, SignupPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        if page_name == "ChatPage":
            frame = ChatPage(parent=self.frames["HomePage"].master, controller=self, current_user=self.current_user)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        else:
            frame = self.frames[page_name]
        frame.tkraise()
        self.geometry("900x600")  # Ensure the window size is always set correctly

if __name__ == "__main__":
    app = App()
    app.mainloop()
