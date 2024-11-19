# gui/clientes.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseConnection
from models.cliente import Cliente

class ClientesTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.setup_clientes_tab()

    def setup_clientes_tab(self):
        ttk.Button(self.frame, text="Registrar Cliente", command=self.registrar_cliente).pack(pady=10)
        ttk.Button(self.frame, text="Consultar Clientes", command=self.consultar_clientes).pack(pady=10)

    def registrar_cliente(self):
        registrar_cliente_window = tk.Toplevel()
        registrar_cliente_window.geometry("400x400")
        registrar_cliente_window.title("Registrar Cliente")

        dni_entry = self.create_labeled_entry(registrar_cliente_window, "DNI:")
        nombre_entry = self.create_labeled_entry(registrar_cliente_window, "Nombre:")
        apellido_entry = self.create_labeled_entry(registrar_cliente_window, "Apellido:")
        direccion_entry = self.create_labeled_entry(registrar_cliente_window, "Dirección:")
        telefono_entry = self.create_labeled_entry(registrar_cliente_window, "Teléfono:")
        email_entry = self.create_labeled_entry(registrar_cliente_window, "Email:")

        ttk.Button(registrar_cliente_window, text="Guardar", command=lambda: self.guardar_cliente(
            dni_entry.get(), nombre_entry.get(), apellido_entry.get(),
            direccion_entry.get(), telefono_entry.get(), email_entry.get()
        )).pack(pady=10)

    def create_labeled_entry(self, parent, label_text, initial_value=""):
        ttk.Label(parent, text=label_text).pack(pady=5)
        entry = ttk.Entry(parent)
        entry.insert(0, initial_value)
        entry.pack(pady=5)
        return entry

    def guardar_cliente(self, dni, nombre, apellido, direccion, telefono, email):
        if not dni or not nombre or not apellido:
            messagebox.showerror("Error", "DNI, Nombre y Apellido son obligatorios.")
            return
        try:
            dni = int(dni)
        except ValueError:
            messagebox.showerror("Error", "DNI debe ser un valor numérico.")
            return

        cliente = Cliente(dni, nombre, apellido, direccion, telefono, email)
        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Cliente WHERE DNI = ?", (cliente.dni,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Ya existe un cliente con este DNI.")
                return
            cursor.execute("INSERT INTO Cliente (DNI, Nombre, Apellido, Direccion, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?)",
                           (cliente.dni, cliente.nombre, cliente.apellido, cliente.direccion, cliente.telefono, cliente.email))
        messagebox.showinfo("Éxito", "Cliente registrado correctamente.")

    def consultar_clientes(self):
        consultar_clientes_window = tk.Toplevel()
        consultar_clientes_window.geometry("800x400")
        consultar_clientes_window.title("Consultar Clientes")

        clientes_tree = ttk.Treeview(consultar_clientes_window, columns=("DNI", "Nombre", "Apellido", "Direccion", "Telefono", "Email"), show='headings')
        clientes_tree.heading("DNI", text="DNI")
        clientes_tree.heading("Nombre", text="Nombre")
        clientes_tree.heading("Apellido", text="Apellido")
        clientes_tree.heading("Direccion", text="Dirección")
        clientes_tree.heading("Telefono", text="Teléfono")
        clientes_tree.heading("Email", text="Email")

        clientes_tree.column("DNI", width=80)
        clientes_tree.column("Nombre", width=100)
        clientes_tree.column("Apellido", width=100)
        clientes_tree.column("Direccion", width=150)
        clientes_tree.column("Telefono", width=100)
        clientes_tree.column("Email", width=150)

        clientes_tree.pack(fill='both', expand=True, padx=10, pady=10)

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Cliente")
            clientes = cursor.fetchall()
            for cliente_data in clientes:
                clientes_tree.insert("", "end", values=cliente_data)
