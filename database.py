# database.py

import sqlite3
from contextlib import contextmanager
from tkinter import messagebox
from datetime import datetime, timedelta

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = sqlite3.connect('hotel_management.db')
            cls._instance._cursor = cls._instance._connection.cursor()
            cls._instance._initialize_database()
        return cls._instance

    def _initialize_database(self):
        # Crear tablas si no existen
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS Habitacion (
                Numero INTEGER PRIMARY KEY,
                Tipo TEXT NOT NULL,
                Estado TEXT NOT NULL,
                PrecioPorNoche REAL NOT NULL,
                Capacidad INTEGER NOT NULL
            )
        ''')
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS Cliente (
                DNI INTEGER PRIMARY KEY,
                Nombre TEXT NOT NULL,
                Apellido TEXT NOT NULL,
                Direccion TEXT,
                Telefono TEXT,
                Email TEXT
            )
        ''')
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS Reserva (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ClienteDNI INTEGER,
                HabitacionNumero INTEGER,
                FechaEntrada TEXT NOT NULL,
                FechaSalida TEXT NOT NULL,
                CantidadPersonas INTEGER,
                FOREIGN KEY (ClienteDNI) REFERENCES Cliente(DNI),
                FOREIGN KEY (HabitacionNumero) REFERENCES Habitacion(Numero)
            )
        ''')
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS Empleado (
                DNI INTEGER PRIMARY KEY,
                Nombre TEXT NOT NULL,
                Apellido TEXT NOT NULL,
                Cargo TEXT NOT NULL,
                Sueldo REAL NOT NULL
            )
        ''')
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS EmpleadoHabitacion (
                EmpleadoDNI INTEGER,
                HabitacionNumero INTEGER,
                FechaAsignacion TEXT NOT NULL,
                FOREIGN KEY (EmpleadoDNI) REFERENCES Empleado(DNI),
                FOREIGN KEY (HabitacionNumero) REFERENCES Habitacion(Numero)
            )
        ''')
        self._cursor.execute('''
            CREATE TABLE IF NOT EXISTS Factura (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ClienteDNI INTEGER,
                ReservaID INTEGER,
                FechaEmision TEXT NOT NULL,
                Total REAL NOT NULL,
                FOREIGN KEY (ClienteDNI) REFERENCES Cliente(DNI),
                FOREIGN KEY (ReservaID) REFERENCES Reserva(ID)
            )
        ''')
        self._connection.commit()
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        cursor = self._cursor
        # Verificar si las tablas están vacías
        cursor.execute("SELECT COUNT(*) FROM Cliente")
        clientes_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Empleado")
        empleados_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Habitacion")
        habitaciones_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Reserva")
        reservas_count = cursor.fetchone()[0]

        if clientes_count == 0 and empleados_count == 0 and habitaciones_count == 0 and reservas_count == 0:
            # Insertar datos de muestra
            cursor.execute("INSERT INTO Cliente (DNI, Nombre, Apellido, Direccion, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?)",
                           (12345678, 'Juan', 'Perez', 'Calle Falsa 123', '555-1234', 'juan.perez@example.com'))
            cursor.execute("INSERT INTO Cliente (DNI, Nombre, Apellido, Direccion, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?)",
                           (87654321, 'Maria', 'Gomez', 'Avenida Siempre Viva 742', '555-5678', 'maria.gomez@example.com'))
            # Empleados de muestra
            cursor.execute("INSERT INTO Empleado (DNI, Nombre, Apellido, Cargo, Sueldo) VALUES (?, ?, ?, ?, ?)",
                           (11111111, 'Carlos', 'Lopez', 'Limpieza', 20000))
            cursor.execute("INSERT INTO Empleado (DNI, Nombre, Apellido, Cargo, Sueldo) VALUES (?, ?, ?, ?, ?)",
                           (22222222, 'Ana', 'Martinez', 'Recepcionista', 25000))
            # Habitaciones de muestra
            cursor.execute("INSERT INTO Habitacion (Numero, Tipo, Estado, PrecioPorNoche, Capacidad) VALUES (?, ?, ?, ?, ?)",
                           (101, 'simple', 'disponible', 1000, 1))
            cursor.execute("INSERT INTO Habitacion (Numero, Tipo, Estado, PrecioPorNoche, Capacidad) VALUES (?, ?, ?, ?, ?)",
                           (102, 'doble', 'ocupada', 1500, 2))
            cursor.execute("INSERT INTO Habitacion (Numero, Tipo, Estado, PrecioPorNoche, Capacidad) VALUES (?, ?, ?, ?, ?)",
                           (201, 'suite', 'disponible', 3000, 4))
            # Reservas de muestra
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            tomorrow = today + timedelta(days=1)
            day_after_tomorrow = today + timedelta(days=2)

            cursor.execute("INSERT INTO Reserva (ClienteDNI, HabitacionNumero, FechaEntrada, FechaSalida, CantidadPersonas) VALUES (?, ?, ?, ?, ?)",
                           (12345678, 101, yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), 1))  # Debería liberarse
            cursor.execute("INSERT INTO Reserva (ClienteDNI, HabitacionNumero, FechaEntrada, FechaSalida, CantidadPersonas) VALUES (?, ?, ?, ?, ?)",
                           (87654321, 102, today.strftime('%Y-%m-%d'), day_after_tomorrow.strftime('%Y-%m-%d'), 2))
            # Actualizar estado de habitaciones
            cursor.execute("UPDATE Habitacion SET Estado = 'ocupada' WHERE Numero = ?", (101,))
            cursor.execute("UPDATE Habitacion SET Estado = 'ocupada' WHERE Numero = ?", (102,))
            # Asignaciones empleado-habitación (opcional)
            cursor.execute("INSERT INTO EmpleadoHabitacion (EmpleadoDNI, HabitacionNumero, FechaAsignacion) VALUES (?, ?, ?)",
                           (11111111, 101, today.strftime('%Y-%m-%d')))
            cursor.execute("INSERT INTO EmpleadoHabitacion (EmpleadoDNI, HabitacionNumero, FechaAsignacion) VALUES (?, ?, ?)",
                           (11111111, 102, tomorrow.strftime('%Y-%m-%d')))
            self._connection.commit()

    def actualizar_estado_habitaciones(self):
        """Actualiza el estado de las habitaciones según la fecha actual y las reservas."""
        cursor = self._cursor
        today_str = datetime.now().strftime('%Y-%m-%d')

        # Seleccionar reservas que finalizan hoy o antes y no se ha generado factura
        cursor.execute("""
            SELECT r.ID, r.ClienteDNI, r.HabitacionNumero, h.PrecioPorNoche, r.FechaEntrada, r.FechaSalida
            FROM Reserva r
            JOIN Habitacion h ON r.HabitacionNumero = h.Numero
            WHERE r.FechaSalida <= ? AND r.ID NOT IN (SELECT ReservaID FROM Factura)
        """, (today_str,))
        reservas_para_facturar = cursor.fetchall()

        for reserva in reservas_para_facturar:
            reserva_id, cliente_dni, habitacion_numero, precio_por_noche, fecha_entrada, fecha_salida = reserva

            # Calcular el total
            dias_estadia = (datetime.strptime(fecha_salida, "%Y-%m-%d") - datetime.strptime(fecha_entrada, "%Y-%m-%d")).days
            total = dias_estadia * precio_por_noche

            # Generar la factura
            fecha_emision = today_str
            cursor.execute("INSERT INTO Factura (ClienteDNI, ReservaID, FechaEmision, Total) VALUES (?, ?, ?, ?)",
                           (cliente_dni, reserva_id, fecha_emision, total))

            # Actualizar el estado de la habitación a 'disponible'
            cursor.execute("UPDATE Habitacion SET Estado = 'disponible' WHERE Numero = ?", (habitacion_numero,))

        self._connection.commit()
    def commit(self):
        self._connection.commit()

    def close(self):
        if self._connection:
            self._connection.close()
            self._instance = None

    @contextmanager
    def cursor(self):
        try:
            yield self._cursor
            self.commit()
        except sqlite3.Error as e:
            self._connection.rollback()
            messagebox.showerror("Database Error", str(e))
