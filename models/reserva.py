# models/reserva.py
class Reserva:
    def __init__(self, id_reserva, cliente_dni, habitacion_numero, fecha_entrada, fecha_salida, cantidad_personas):
        self.id_reserva = id_reserva
        self.cliente_dni = cliente_dni
        self.habitacion_numero = habitacion_numero
        self.fecha_entrada = fecha_entrada
        self.fecha_salida = fecha_salida
        self.cantidad_personas = cantidad_personas

    def __repr__(self):
        return f"Reserva(ID={self.id_reserva}, ClienteDNI={self.cliente_dni}, HabitacionNumero={self.habitacion_numero})"
