# models/empleado.py
class Empleado:
    def __init__(self, dni, nombre, apellido, cargo, sueldo):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.cargo = cargo
        self.sueldo = sueldo

    def __repr__(self):
        return f"Empleado(DNI={self.dni}, Nombre={self.nombre}, Apellido={self.apellido}, Cargo={self.cargo}, Sueldo={self.sueldo})"
