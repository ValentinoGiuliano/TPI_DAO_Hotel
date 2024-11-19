# gui/reportes.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from database import DatabaseConnection
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ReportesTab:
    def __init__(self, notebook):
        self.frame = ttk.Frame(notebook)
        self.setup_reportes_tab()

    def setup_reportes_tab(self):
        ttk.Label(self.frame, text="Reportes", font=("Helvetica", 16)).pack(pady=10)

        # Frame para listar reservas en un periodo
        periodo_frame = ttk.LabelFrame(self.frame, text="Listar Reservas en un Periodo")
        periodo_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(periodo_frame, text="Fecha Inicio (DD-MM-AAAA):").grid(row=0, column=0, padx=5, pady=5)
        self.fecha_inicio_entry = ttk.Entry(periodo_frame)
        self.fecha_inicio_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(periodo_frame, text="Fecha Fin (DD-MM-AAAA):").grid(row=1, column=0, padx=5, pady=5)
        self.fecha_fin_entry = ttk.Entry(periodo_frame)
        self.fecha_fin_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(periodo_frame, text="Generar Reporte", command=self.generar_reporte_reservas).grid(row=2, column=0, columnspan=2, pady=10)

        # Frame para reporte de ingresos
        ingresos_frame = ttk.LabelFrame(self.frame, text="Reporte de Ingresos por Habitaciones")
        ingresos_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(ingresos_frame, text="Generar Reporte de Ingresos", command=self.generar_reporte_ingresos).pack(pady=10)

        # Frame para reporte de ocupación
        ocupacion_frame = ttk.LabelFrame(self.frame, text="Reporte de Ocupación Promedio por Tipo de Habitación")
        ocupacion_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(ocupacion_frame, text="Generar Reporte de Ocupación", command=self.generar_reporte_ocupacion).pack(pady=10)

    def generar_reporte_reservas(self):
        fecha_inicio = self.fecha_inicio_entry.get()
        fecha_fin = self.fecha_fin_entry.get()

        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%d-%m-%Y")
            fecha_fin_dt = datetime.strptime(fecha_fin, "%d-%m-%Y")
            if fecha_inicio_dt > fecha_fin_dt:
                messagebox.showerror("Error", "La fecha de inicio debe ser anterior o igual a la fecha de fin.")
                return
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use DD-MM-AAAA.")
            return

        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT r.ID, c.Nombre || ' ' || c.Apellido, h.Numero, h.Tipo, r.FechaEntrada, r.FechaSalida
                FROM Reserva r
                JOIN Cliente c ON r.ClienteDNI = c.DNI
                JOIN Habitacion h ON r.HabitacionNumero = h.Numero
                WHERE r.FechaEntrada BETWEEN ? AND ?
            """, (fecha_inicio_dt.strftime("%Y-%m-%d"), fecha_fin_dt.strftime("%Y-%m-%d")))
            reservas = cursor.fetchall()

        if not reservas:
            messagebox.showinfo("Reporte de Reservas", "No se encontraron reservas en el periodo especificado.")
            return

        # Mostrar el reporte en una nueva ventana
        reporte_window = tk.Toplevel()
        reporte_window.title("Reporte de Reservas")
        reporte_window.geometry("800x400")

        tree = ttk.Treeview(reporte_window, columns=("ID", "Cliente", "Habitacion", "Tipo", "Fecha Entrada", "Fecha Salida"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Cliente", text="Cliente")
        tree.heading("Habitacion", text="Habitación")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Fecha Entrada", text="Fecha Entrada")
        tree.heading("Fecha Salida", text="Fecha Salida")

        for reserva in reservas:
            tree.insert('', 'end', values=reserva)

        tree.pack(fill='both', expand=True)

        # Opción para guardar en PDF
        ttk.Button(reporte_window, text="Guardar en PDF", command=lambda: self.guardar_reporte_reservas_pdf(reservas)).pack(pady=10)

    def guardar_reporte_reservas_pdf(self, reservas):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(30, 750, "Reporte de Reservas")
            c.drawString(30, 735, f"Fecha: {datetime.now().strftime('%d-%m-%Y')}")
            y = 700
            for reserva in reservas:
                text = f"ID: {reserva[0]}, Cliente: {reserva[1]}, Habitación: {reserva[2]}, Tipo: {reserva[3]}, Entrada: {reserva[4]}, Salida: {reserva[5]}"
                c.drawString(30, y, text)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            messagebox.showinfo("Éxito", "Reporte guardado en PDF exitosamente.")

    def generar_reporte_ingresos(self):
        db = DatabaseConnection()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT h.Numero, h.Tipo, h.PrecioPorNoche, COUNT(r.ID) as NumReservas, 
                SUM((julianday(r.FechaSalida) - julianday(r.FechaEntrada)) * h.PrecioPorNoche) as Ingresos
                FROM Habitacion h
                LEFT JOIN Reserva r ON h.Numero = r.HabitacionNumero
                GROUP BY h.Numero
            """)
            ingresos = cursor.fetchall()

        if not ingresos:
            messagebox.showinfo("Reporte de Ingresos", "No hay datos de ingresos disponibles.")
            return

        # Generar gráfico con Matplotlib
        numeros = [ing[0] for ing in ingresos]
        ingresos_vals = [ing[4] if ing[4] else 0 for ing in ingresos]

        plt.figure(figsize=(10, 6))
        plt.bar(numeros, ingresos_vals, color='skyblue')
        plt.xlabel('Número de Habitación')
        plt.ylabel('Ingresos')
        plt.title('Ingresos por Habitación')
        plt.tight_layout()
        plt.show()

        # Opción para guardar en PDF
        save_pdf = messagebox.askyesno("Guardar Reporte", "¿Desea guardar el reporte en PDF?")
        if save_pdf:
            self.guardar_reporte_ingresos_pdf(ingresos)

    def guardar_reporte_ingresos_pdf(self, ingresos):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(30, 750, "Reporte de Ingresos por Habitaciones")
            c.drawString(30, 735, f"Fecha: {datetime.now().strftime('%d-%m-%Y')}")
            y = 700
            for ingreso in ingresos:
                ingresos_totales = ingreso[4] if ingreso[4] else 0
                text = f"Habitación: {ingreso[0]}, Tipo: {ingreso[1]}, Ingresos: ${ingresos_totales:.2f}"
                c.drawString(30, y, text)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            messagebox.showinfo("Éxito", "Reporte guardado en PDF exitosamente.")

    def generar_reporte_ocupacion(self):
        db = DatabaseConnection()
        with db.cursor() as cursor:
            # Obtener tipos de habitación
            cursor.execute("SELECT DISTINCT Tipo FROM Habitacion")
            tipos = [row[0] for row in cursor.fetchall()]

            ocupacion_data = []
            for tipo in tipos:
                # Obtener el promedio de personas por reserva para el tipo de habitación
                cursor.execute("""
                    SELECT AVG(r.CantidadPersonas)
                    FROM Reserva r
                    JOIN Habitacion h ON r.HabitacionNumero = h.Numero
                    WHERE h.Tipo = ?
                """, (tipo,))
                promedio_personas = cursor.fetchone()[0] or 0
                ocupacion_data.append((tipo, promedio_personas))

        if not ocupacion_data:
            messagebox.showinfo("Reporte de Ocupación", "No hay datos de ocupación disponibles.")
            return

        # Generar gráfico de barras con Matplotlib
        tipos = [data[0] for data in ocupacion_data]
        promedios = [data[1] for data in ocupacion_data]

        plt.figure(figsize=(10, 6))
        plt.bar(tipos, promedios, color='skyblue')
        plt.xlabel('Tipo de Habitación')
        plt.ylabel('Promedio de Personas por Reserva')
        plt.title('Ocupación Promedio por Tipo de Habitación')
        plt.tight_layout()
        plt.show()

        # Opción para guardar en PDF
        save_pdf = messagebox.askyesno("Guardar Reporte", "¿Desea guardar el reporte en PDF?")
        if save_pdf:
            self.guardar_reporte_ocupacion_pdf(ocupacion_data)



    def guardar_reporte_ocupacion_pdf(self, ocupacion_data):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(30, 750, "Reporte de Ocupación Promedio por Tipo de Habitación")
            c.drawString(30, 735, f"Fecha: {datetime.now().strftime('%d-%m-%Y')}")
            y = 700
            for tipo, promedio in ocupacion_data:
                text = f"Tipo de Habitación: {tipo}, Promedio de Personas por Reserva: {promedio:.2f}"
                c.drawString(30, y, text)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            messagebox.showinfo("Éxito", "Reporte guardado en PDF exitosamente.")

