# gui/app.py

import tkinter as tk
from tkinter import ttk
from .clientes import ClientesTab
from .habitaciones import HabitacionesTab
from .empleados import EmpleadosTab
from .reportes import ReportesTab
from .facturas import FacturasTab  # Importar la nueva pestaña de facturas
from .welcome import WelcomeScreen

class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Ocultar la ventana principal inicialmente

        # Mostrar pantalla de bienvenida
        self.welcome_screen = WelcomeScreen(self)
        self.wait_window(self.welcome_screen)  # Esperar hasta que la pantalla de bienvenida se cierre

        # Configurar la ventana principal
        self.title("Sistema de Gestión de Hotel")
        self.geometry("800x600")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True)

        # Tabs
        self.clientes_tab = ClientesTab(self.notebook)
        self.habitaciones_tab = HabitacionesTab(self.notebook)
        self.empleados_tab = EmpleadosTab(self.notebook)
        self.reportes_tab = ReportesTab(self.notebook)
        self.facturas_tab = FacturasTab(self.notebook)  # Añadir la pestaña de facturas

        # Add tabs to notebook
        self.notebook.add(self.clientes_tab.frame, text='Clientes')
        self.notebook.add(self.habitaciones_tab.frame, text='Habitaciones y Reservas')
        self.notebook.add(self.empleados_tab.frame, text='Empleados')
        self.notebook.add(self.reportes_tab.frame, text='Reportes')
        self.notebook.add(self.facturas_tab.frame, text='Facturas')  # Añadir la pestaña al notebook

        self.deiconify()  # Mostrar la ventana principal
