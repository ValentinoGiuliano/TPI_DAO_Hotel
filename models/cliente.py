# models/cliente.py
class Cliente:
    def __init__(self, dni, nombre, apellido, direccion='', telefono='', email=''):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def __repr__(self):
        return f"Cliente(DNI={self.dni}, Nombre={self.nombre}, Apellido={self.apellido})"
