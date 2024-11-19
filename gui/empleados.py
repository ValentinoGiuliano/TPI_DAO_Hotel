# gui/empleados.py

import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseConnection
from models.empleado import Empleado

class EmpleadosTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.setup_empleados_tab()

    def setup_empleados_tab(self):
        # Botones de la interfaz
        ttk.Button(self.frame, text="Registrar Empleado", command=self.registrar_empleado).pack(pady=10)
        ttk.Button(self.frame, text="Consultar Empleados", command=self.consultar_empleados).pack(pady=10)
        ttk.Button(self.frame, text="Asignar Habitación", command=self.asignar_habitacion_window).pack(pady=10)
        ttk.Button(self.frame, text="Ver y Eliminar Asignaciones", command=self.ver_eliminar_asignaciones).pack(pady=10)

    # Método para registrar empleado
    def registrar_empleado(self):
        registrar_empleado_window = tk.Toplevel()
        registrar_empleado_window.geometry("400x400")
        registrar_empleado_window.title("Registrar Empleado")

        dni_entry = self.create_labeled_entry(registrar_empleado_window, "DNI:")
        nombre_entry = self.create_labeled_entry(registrar_empleado_window, "Nombre:")
        apellido_entry = self.create_labeled_entry(registrar_empleado_window, "Apellido:")
        ttk.Label(registrar_empleado_window, text="Cargo:").pack(pady=5)
        cargo_combo = ttk.Combobox(registrar_empleado_window, values=["Recepcionista", "Limpieza", "Gerente", "Mantenimiento"])
        cargo_combo.pack(pady=5)
        sueldo_entry = self.create_labeled_entry(registrar_empleado_window, "Sueldo:")

        ttk.Button(registrar_empleado_window, text="Guardar", command=lambda: self.guardar_empleado(
            dni_entry.get(), nombre_entry.get(), apellido_entry.get(), cargo_combo.get(), sueldo_entry.get()
        )).pack(pady=10)

    def guardar_empleado(self, dni, nombre, apellido, cargo, sueldo):
        if not dni or not nombre or not apellido or not cargo or not sueldo:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            dni = int(dni)
            sueldo = float(sueldo)
        except ValueError:
            messagebox.showerror("Error", "DNI y Sueldo deben ser valores numéricos.")
            return

        empleado = Empleado(dni, nombre, apellido, cargo, sueldo)
        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM Empleado WHERE DNI = ?", (empleado.dni,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Ya existe un empleado con este DNI.")
                return
            cursor.execute("INSERT INTO Empleado (DNI, Nombre, Apellido, Cargo, Sueldo) VALUES (?, ?, ?, ?, ?)",
                           (empleado.dni, empleado.nombre, empleado.apellido, empleado.cargo, empleado.sueldo))
        messagebox.showinfo("Éxito", "Empleado registrado correctamente.")

    def create_labeled_entry(self, parent, label_text, initial_value=""):
        ttk.Label(parent, text=label_text).pack(pady=5)
        entry = ttk.Entry(parent)
        entry.insert(0, initial_value)
        entry.pack(pady=5)
        return entry

    # Método para abrir la ventana de asignación de habitación
    def asignar_habitacion_window(self):
        asignar_window = tk.Toplevel()
        asignar_window.title("Asignar Habitación a Empleado")
        asignar_window.geometry("300x200")

        empleado_dni_entry = self.create_labeled_entry(asignar_window, "DNI del Empleado:")
        habitacion_numero_entry = self.create_labeled_entry(asignar_window, "Número de Habitación:")

        ttk.Button(asignar_window, text="Asignar", command=lambda: self.asignar_habitacion(
            empleado_dni_entry.get(), habitacion_numero_entry.get())).pack(pady=10)

    # Método para asignar habitación a empleado
    def asignar_habitacion(self, empleado_dni, habitacion_numero):
        if not empleado_dni or not habitacion_numero:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            empleado_dni = int(empleado_dni)
            habitacion_numero = int(habitacion_numero)
        except ValueError:
            messagebox.showerror("Error", "El DNI y el número de habitación deben ser numéricos.")
            return

        db = DatabaseConnection()
        with db.cursor() as cursor:
            # Verificar que el empleado exista
            cursor.execute("SELECT DNI FROM Empleado WHERE DNI = ?", (empleado_dni,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "El empleado no existe.")
                return

            # Verificar que la habitación exista
            cursor.execute("SELECT Numero FROM Habitacion WHERE Numero = ?", (habitacion_numero,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "La habitación no existe.")
                return

            # Verificar que el empleado no tenga más de 5 asignaciones
            cursor.execute("""
                SELECT COUNT(*) FROM EmpleadoHabitacion
                WHERE EmpleadoDNI = ?
            """, (empleado_dni,))
            asignaciones_count = cursor.fetchone()[0]
            if asignaciones_count >= 5:
                messagebox.showerror("Error", "El empleado ya tiene 5 asignaciones.")
                return

            # Registrar la asignación
            cursor.execute("INSERT INTO EmpleadoHabitacion (EmpleadoDNI, HabitacionNumero) VALUES (?, ?)",
                           (empleado_dni, habitacion_numero))
            db.commit()
            messagebox.showinfo("Éxito", "Asignación registrada correctamente.")

    # Método para ver y eliminar asignaciones
    def ver_eliminar_asignaciones(self):
        asignaciones_window = tk.Toplevel()
        asignaciones_window.title("Asignaciones de Empleados")
        asignaciones_window.geometry("800x400")

        asignaciones_tree = ttk.Treeview(asignaciones_window, columns=("EmpleadoDNI", "EmpleadoNombre", "HabitacionNumero"), show='headings')
        asignaciones_tree.heading("EmpleadoDNI", text="DNI Empleado")
        asignaciones_tree.heading("EmpleadoNombre", text="Nombre Empleado")
        asignaciones_tree.heading("HabitacionNumero", text="Número de Habitación")

        asignaciones_tree.column("EmpleadoDNI", width=100)
        asignaciones_tree.column("EmpleadoNombre", width=200)
        asignaciones_tree.column("HabitacionNumero", width=100)

        asignaciones_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Botón para eliminar asignación
        ttk.Button(asignaciones_window, text="Eliminar Asignación Seleccionada", command=lambda: self.eliminar_asignacion(asignaciones_tree)).pack(pady=10)

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT eh.EmpleadoDNI, e.Nombre || ' ' || e.Apellido, eh.HabitacionNumero
                FROM EmpleadoHabitacion eh
                JOIN Empleado e ON eh.EmpleadoDNI = e.DNI
            """)
            asignaciones = cursor.fetchall()
            for asignacion in asignaciones:
                asignaciones_tree.insert("", "end", values=asignacion)

    # Método para eliminar una asignación
    def eliminar_asignacion(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione una asignación para eliminar.")
            return
        asignacion = tree.item(selected_item)
        empleado_dni = asignacion['values'][0]
        habitacion_numero = asignacion['values'][2]

        confirm = messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar la asignación del empleado {empleado_dni} a la habitación {habitacion_numero}?")
        if confirm:
            db = DatabaseConnection()
            with db.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM EmpleadoHabitacion
                    WHERE EmpleadoDNI = ? AND HabitacionNumero = ?
                """, (empleado_dni, habitacion_numero))
                db.commit()
            messagebox.showinfo("Éxito", "Asignación eliminada correctamente.")
            tree.delete(selected_item)

    # Método para consultar empleados
    def consultar_empleados(self):
        consultar_empleados_window = tk.Toplevel()
        consultar_empleados_window.geometry("800x400")
        consultar_empleados_window.title("Consultar Empleados")

        empleados_tree = ttk.Treeview(consultar_empleados_window, columns=("DNI", "Nombre", "Apellido", "Cargo", "Sueldo"), show='headings')
        empleados_tree.heading("DNI", text="DNI")
        empleados_tree.heading("Nombre", text="Nombre")
        empleados_tree.heading("Apellido", text="Apellido")
        empleados_tree.heading("Cargo", text="Cargo")
        empleados_tree.heading("Sueldo", text="Sueldo")

        empleados_tree.column("DNI", width=80)
        empleados_tree.column("Nombre", width=100)
        empleados_tree.column("Apellido", width=100)
        empleados_tree.column("Cargo", width=100)
        empleados_tree.column("Sueldo", width=80)

        empleados_tree.pack(fill='both', expand=True, padx=10, pady=10)

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("SELECT DNI, Nombre, Apellido, Cargo, Sueldo FROM Empleado")
            empleados = cursor.fetchall()
            for empleado in empleados:
                empleados_tree.insert("", "end", values=empleado)
