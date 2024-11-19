# gui/welcome.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Pillow library for image handling

class WelcomeScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Bienvenido")
        self.geometry("800x600")
        self.resizable(False, False)

        # Load background image
        self.background_image = Image.open("background.jpg")
        self.background_image = self.background_image.resize((800, 600))
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create label with background image
        self.background_label = tk.Label(self, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Welcome message
        self.welcome_label = tk.Label(self, text="BIENVENIDO AL SISTEMA DE GESTIÓN DE HOTEL",
                                      font=("Helvetica", 24, "bold"), bg='white')
        self.welcome_label.place(relx=0.5, rely=0.1, anchor='center')

        # 'INICIAR' button
        iniciar_button = ttk.Button(self, text="INICIAR", command=self.on_iniciar)
        iniciar_button.place(relx=0.5, rely=0.6, anchor='center')

        # Make the window modal
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_iniciar(self):
        self.destroy()  # Close the welcome screen

    def on_close(self):
        # Prevent closing the welcome screen without pressing 'INICIAR'
        pass
