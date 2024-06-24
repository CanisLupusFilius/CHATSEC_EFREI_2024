import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.configure_gui()
        self.create_widgets()
        self.bind("<Configure>", self.on_resize)

    def configure_gui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        # Load the background image
        self.background_image = Image.open("./Ressources/background_home.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create a Canvas to display the image
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Add the image to the canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        # Create text directly on the canvas
        self.text_id = self.canvas.create_text(400, 100, text="CHATSEC", font=("Helvetica", 18), fill="white", anchor="center")

        # Create a frame for buttons and place it on the canvas
        button_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window(400, 200, anchor="center", window=button_frame)

        # Add buttons to the frame
        login_button = ttk.Button(button_frame, text="Go to Login Page", command=lambda: self.controller.show_frame("LoginPage"))
        login_button.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        signup_button = ttk.Button(button_frame, text="Go to Signup Page", command=lambda: self.controller.show_frame("SignupPage"))
        signup_button.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        # Ensure the frame uses all available space
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)

    def on_resize(self, event):
        # Resize the image to fit within the window dimensions
        width, height = event.width, event.height
        resized_image = self.background_image.resize((width, height), Image.ANTIALIAS)
        self.background_photo = ImageTk.PhotoImage(resized_image)

        # Update the background image
        self.canvas.itemconfig(self.canvas.find_withtag("background"), image=self.background_photo)

# Create the main application window
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Home Page Example")
        self.geometry("800x600")
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        frame = HomePage(parent=container, controller=self)
        self.frames["HomePage"] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# Run the application
if __name__ == "__main__":
    app = App()
    app.mainloop()
