# gui/habitaciones.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import DatabaseConnection
from models.habitacion import Habitacion
from models.estado_habitacion import DisponibleState

class HabitacionesTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.setup_habitaciones_tab()

    def setup_habitaciones_tab(self):
        ttk.Button(self.frame, text="Registrar Habitación", command=self.registrar_habitacion).pack(pady=10)
        ttk.Button(self.frame, text="Registrar Reserva", command=self.registrar_reserva).pack(pady=10)
        ttk.Button(self.frame, text="Consultar Disponibilidad", command=self.consultar_disponibilidad).pack(pady=10)
        ttk.Button(self.frame, text="Consultar Reservas", command=self.consultar_reservas).pack(pady=10)

    def registrar_habitacion(self):
        registrar_habitacion_window = tk.Toplevel()
        registrar_habitacion_window.geometry("400x300")
        registrar_habitacion_window.title("Registrar Habitación")

        numero_entry = self.create_labeled_entry(registrar_habitacion_window, "Número de Habitación:")
        ttk.Label(registrar_habitacion_window, text="Tipo:").pack(pady=5)
        tipo_combo = ttk.Combobox(registrar_habitacion_window, values=["simple", "doble", "suite"])
        tipo_combo.pack(pady=5)
        precio_entry = self.create_labeled_entry(registrar_habitacion_window, "Precio por Noche:")

        ttk.Button(registrar_habitacion_window, text="Guardar", command=lambda: self.guardar_habitacion(
            numero_entry.get(), tipo_combo.get(), precio_entry.get()
        )).pack(pady=10)

    def create_labeled_entry(self, parent, label_text, initial_value=""):
        ttk.Label(parent, text=label_text).pack(pady=5)
        entry = ttk.Entry(parent)
        entry.insert(0, initial_value)
        entry.pack(pady=5)
        return entry

    def guardar_habitacion(self, numero, tipo, precio_por_noche):
        if not numero or not tipo or not precio_por_noche:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            numero = int(numero)
            precio_por_noche = float(precio_por_noche)
        except ValueError:
            messagebox.showerror("Error", "Número y Precio deben ser valores numéricos.")
            return

        estado_str = 'disponible'

        # Establecer capacidad según el tipo de habitación
        tipo = tipo.lower()
        if tipo == 'simple':
            capacidad = 1
        elif tipo == 'doble':
            capacidad = 2
        elif tipo == 'suite':
            capacidad = 4  # Puedes ajustar este valor según tus necesidades
        else:
            messagebox.showerror("Error", "Tipo de habitación inválido.")
            return

        habitacion = Habitacion(numero, tipo, estado_str, precio_por_noche, capacidad)

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("SELECT Numero FROM Habitacion WHERE Numero = ?", (numero,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Ya existe una habitación con este número.")
                return
            cursor.execute(
                "INSERT INTO Habitacion (Numero, Tipo, Estado, PrecioPorNoche, Capacidad) VALUES (?, ?, ?, ?, ?)",
                (habitacion.numero, habitacion.tipo, habitacion.estado_str, habitacion.precio_por_noche, habitacion.capacidad)
            )
            db.commit()
        messagebox.showinfo("Éxito", "Habitación registrada correctamente.")

    def registrar_reserva(self):
        registrar_reserva_window = tk.Toplevel()
        registrar_reserva_window.geometry("400x400")
        registrar_reserva_window.title("Registrar Reserva")

        cliente_dni_entry = self.create_labeled_entry(registrar_reserva_window, "DNI del Cliente:")
        habitacion_numero_entry = self.create_labeled_entry(registrar_reserva_window, "Número de Habitación:")
        fecha_entrada_entry = self.create_labeled_entry(registrar_reserva_window, "Fecha de Entrada (DD-MM-AAAA):")
        fecha_salida_entry = self.create_labeled_entry(registrar_reserva_window, "Fecha de Salida (DD-MM-AAAA):")
        cantidad_personas_entry = self.create_labeled_entry(registrar_reserva_window, "Cantidad de Personas:")

        ttk.Button(registrar_reserva_window, text="Guardar", command=lambda: self.guardar_reserva(
            cliente_dni_entry.get(), habitacion_numero_entry.get(), fecha_entrada_entry.get(),
            fecha_salida_entry.get(), cantidad_personas_entry.get()
        )).pack(pady=10)

    def guardar_reserva(self, cliente_dni, habitacion_numero, fecha_entrada, fecha_salida, cantidad_personas):
        # Validaciones previas
        if not cliente_dni or not habitacion_numero or not fecha_entrada or not fecha_salida or not cantidad_personas:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            cliente_dni = int(cliente_dni)
            habitacion_numero = int(habitacion_numero)
            cantidad_personas = int(cantidad_personas)
            fecha_entrada_dt = datetime.strptime(fecha_entrada, "%d-%m-%Y")
            fecha_salida_dt = datetime.strptime(fecha_salida, "%d-%m-%Y")
            fecha_entrada_str = fecha_entrada_dt.strftime("%Y-%m-%d")
            fecha_salida_str = fecha_salida_dt.strftime("%Y-%m-%d")

            today = datetime.now().date()
            if fecha_entrada_dt.date() < today:
                messagebox.showerror("Error", "La fecha de entrada no puede ser anterior a hoy.")
                return

            if fecha_entrada_dt >= fecha_salida_dt:
                messagebox.showerror("Error", "La fecha de entrada debe ser anterior a la fecha de salida.")
                return
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos. Verifique los campos e intente nuevamente.")
            return

        db = DatabaseConnection()
        with db.cursor() as cursor:
            # Verificar que el cliente exista
            cursor.execute("SELECT DNI FROM Cliente WHERE DNI = ?", (cliente_dni,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "El cliente no existe.")
                return

            # Validar que las fechas no se superpongan con reservas existentes para la misma habitación
            cursor.execute("""
                SELECT COUNT(*) FROM Reserva
                WHERE HabitacionNumero = ? AND NOT (? >= FechaSalida OR ? <= FechaEntrada)
            """, (habitacion_numero, fecha_entrada_str, fecha_salida_str))
            overlap_count = cursor.fetchone()[0]
            if overlap_count > 0:
                messagebox.showerror("Error", "La habitación ya está reservada en las fechas seleccionadas.")
                return

            # Obtener detalles de la habitación
            cursor.execute("SELECT Tipo, Estado, PrecioPorNoche, Capacidad FROM Habitacion WHERE Numero = ?", (habitacion_numero,))
            habitacion_data = cursor.fetchone()
            if not habitacion_data:
                messagebox.showerror("Error", "La habitación no existe.")
                return

            habitacion_tipo, habitacion_estado_str, habitacion_precio, habitacion_capacidad = habitacion_data

            if cantidad_personas > habitacion_capacidad:
                messagebox.showerror("Error", "La cantidad de personas excede la capacidad de la habitación.")
                return

            # Crear instancia de Habitacion con su estado actual
            habitacion = Habitacion(habitacion_numero, habitacion_tipo, habitacion_estado_str, habitacion_precio, habitacion_capacidad)

            # Intentar reservar la habitación utilizando el patrón State
            if isinstance(habitacion.estado, DisponibleState):
                habitacion.reservar()
                # Registrar la reserva
                cursor.execute("INSERT INTO Reserva (ClienteDNI, HabitacionNumero, FechaEntrada, FechaSalida, CantidadPersonas) VALUES (?, ?, ?, ?, ?)",
                               (cliente_dni, habitacion_numero, fecha_entrada_str, fecha_salida_str, cantidad_personas))
                # Actualizar el estado de la habitación en la base de datos
                nuevo_estado = 'ocupada'
                cursor.execute("UPDATE Habitacion SET Estado = ? WHERE Numero = ?", (nuevo_estado, habitacion_numero))
                db.commit()
                messagebox.showinfo("Éxito", "Reserva registrada correctamente.")
            else:
                messagebox.showerror("Error", f"La habitación {habitacion_numero} no está disponible.")

    def consultar_disponibilidad(self):
        consultar_disponibilidad_window = tk.Toplevel()
        consultar_disponibilidad_window.geometry("400x300")
        consultar_disponibilidad_window.title("Consultar Disponibilidad")

        fecha_entrada_entry = self.create_labeled_entry(consultar_disponibilidad_window, "Fecha de Entrada (DD-MM-AAAA):")
        fecha_salida_entry = self.create_labeled_entry(consultar_disponibilidad_window, "Fecha de Salida (DD-MM-AAAA):")

        ttk.Button(consultar_disponibilidad_window, text="Consultar", command=lambda: self.mostrar_disponibilidad(
            fecha_entrada_entry.get(), fecha_salida_entry.get()
        )).pack(pady=10)

    def mostrar_disponibilidad(self, fecha_entrada, fecha_salida):
        try:
            # Convertir fechas a formato correcto
            fecha_entrada_dt = datetime.strptime(fecha_entrada, "%d-%m-%Y")
            fecha_salida_dt = datetime.strptime(fecha_salida, "%d-%m-%Y")
            fecha_entrada_str = fecha_entrada_dt.strftime("%Y-%m-%d")
            fecha_salida_str = fecha_salida_dt.strftime("%Y-%m-%d")

            if fecha_entrada_dt >= fecha_salida_dt:
                messagebox.showerror("Error", "La fecha de entrada debe ser anterior a la fecha de salida.")
                return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use DD-MM-AAAA.")
            return

        db = DatabaseConnection()
        with db.cursor() as cursor:
            # Actualizar el estado de las habitaciones antes de consultar disponibilidad
            db.actualizar_estado_habitaciones()

            # Obtener habitaciones que no tienen reservas en el rango de fechas especificado
            cursor.execute("""
                SELECT Numero, Tipo, PrecioPorNoche, Capacidad, Estado FROM Habitacion
                WHERE Numero NOT IN (
                    SELECT HabitacionNumero FROM Reserva
                    WHERE NOT (? >= FechaSalida OR ? <= FechaEntrada)
                )
            """, (fecha_entrada_str, fecha_salida_str))

            habitaciones_disponibles = cursor.fetchall()

        if habitaciones_disponibles:
            # Crear ventana similar a "Consultar Empleados"
            disponibilidad_window = tk.Toplevel()
            disponibilidad_window.title("Habitaciones Disponibles")
            disponibilidad_window.geometry("800x400")

            habitaciones_tree = ttk.Treeview(disponibilidad_window, columns=("Numero", "Tipo", "Precio", "Capacidad", "Estado"), show='headings')
            habitaciones_tree.heading("Numero", text="Número")
            habitaciones_tree.heading("Tipo", text="Tipo")
            habitaciones_tree.heading("Precio", text="Precio por Noche")
            habitaciones_tree.heading("Capacidad", text="Capacidad")
            habitaciones_tree.heading("Estado", text="Estado")

            habitaciones_tree.column("Numero", width=80)
            habitaciones_tree.column("Tipo", width=100)
            habitaciones_tree.column("Precio", width=100)
            habitaciones_tree.column("Capacidad", width=80)
            habitaciones_tree.column("Estado", width=100)

            habitaciones_tree.pack(fill='both', expand=True, padx=10, pady=10)

            for habitacion in habitaciones_disponibles:
                habitaciones_tree.insert("", "end", values=habitacion)
        else:
            messagebox.showinfo("Disponibilidad", "No hay habitaciones disponibles para las fechas seleccionadas.")

    def consultar_reservas(self):
        consultar_reservas_window = tk.Toplevel()
        consultar_reservas_window.geometry("800x400")
        consultar_reservas_window.title("Consultar Reservas")

        reservas_tree = ttk.Treeview(consultar_reservas_window, columns=("ID", "Cliente", "Habitacion", "FechaEntrada", "FechaSalida", "CantidadPersonas"), show='headings')
        reservas_tree.heading("ID", text="ID")
        reservas_tree.heading("Cliente", text="Cliente")
        reservas_tree.heading("Habitacion", text="Habitación")
        reservas_tree.heading("FechaEntrada", text="Fecha Entrada")
        reservas_tree.heading("FechaSalida", text="Fecha Salida")
        reservas_tree.heading("CantidadPersonas", text="Cantidad de Personas")

        reservas_tree.column("ID", width=50)
        reservas_tree.column("Cliente", width=150)
        reservas_tree.column("Habitacion", width=100)
        reservas_tree.column("FechaEntrada", width=100)
        reservas_tree.column("FechaSalida", width=100)
        reservas_tree.column("CantidadPersonas", width=150)

        reservas_tree.pack(fill='both', expand=True, padx=10, pady=10)

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.ID, c.Nombre || ' ' || c.Apellido, h.Numero, r.FechaEntrada, r.FechaSalida, r.CantidadPersonas
                FROM Reserva r
                JOIN Cliente c ON r.ClienteDNI = c.DNI
                JOIN Habitacion h ON r.HabitacionNumero = h.Numero
                ORDER BY r.FechaEntrada DESC
            """)
            reservas = cursor.fetchall()
            for reserva in reservas:
                reservas_tree.insert("", "end", values=reserva)
