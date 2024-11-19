# gui/facturas.py

import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseConnection
from datetime import datetime

class FacturasTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.setup_facturas_tab()

    def setup_facturas_tab(self):
        ttk.Button(self.frame, text="Consultar Facturas", command=self.consultar_facturas).pack(pady=10)

    def consultar_facturas(self):
        consultar_facturas_window = tk.Toplevel()
        consultar_facturas_window.geometry("800x400")
        consultar_facturas_window.title("Consultar Facturas")

        facturas_tree = ttk.Treeview(consultar_facturas_window, columns=("ID", "Cliente", "ReservaID", "FechaEmision", "Total"), show='headings')
        facturas_tree.heading("ID", text="ID")
        facturas_tree.heading("Cliente", text="Cliente")
        facturas_tree.heading("ReservaID", text="Reserva ID")
        facturas_tree.heading("FechaEmision", text="Fecha de Emisión")
        facturas_tree.heading("Total", text="Total")

        facturas_tree.column("ID", width=50)
        facturas_tree.column("Cliente", width=150)
        facturas_tree.column("ReservaID", width=80)
        facturas_tree.column("FechaEmision", width=100)
        facturas_tree.column("Total", width=80)

        facturas_tree.pack(fill='both', expand=True, padx=10, pady=10)

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT f.ID, c.Nombre || ' ' || c.Apellido, f.ReservaID, f.FechaEmision, f.Total
                FROM Factura f
                JOIN Cliente c ON f.ClienteDNI = c.DNI
                ORDER BY f.FechaEmision DESC
            """)
            facturas = cursor.fetchall()
            for factura in facturas:
                facturas_tree.insert("", "end", values=factura)
