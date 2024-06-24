import tkinter as tk
from Pages.home import HomePage
from Pages.login import LoginPage
from Pages.signup import SignupPage
from Pages.chatpage import ChatPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Application")
        self.geometry("400x300")
        self.frames = {}
        self.current_user = None
        
        for F in (HomePage, LoginPage, SignupPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("HomePage")
    
    def show_frame(self, page_name):
        frame = self.frames.get(page_name)
        if page_name == "ChatPage":
            frame = ChatPage(parent=self, controller=self, current_user=self.current_user)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
