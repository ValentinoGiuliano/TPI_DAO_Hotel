# models/habitacion.py

from .estado_habitacion import DisponibleState, OcupadaState

class Habitacion:
    def __init__(self, numero, tipo, estado_str, precio_por_noche, capacidad):
        self.numero = numero
        self.tipo = tipo
        self.precio_por_noche = precio_por_noche
        self.capacidad = capacidad
        self.estado_str = estado_str.lower()
        self.estado = self._get_estado_inicial(self.estado_str)

    def _get_estado_inicial(self, estado_str):
        estado_mapping = {
            'disponible': DisponibleState(),
            'ocupada': OcupadaState(),
        }
        return estado_mapping.get(estado_str, DisponibleState())

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado

    def reservar(self):
        self.estado.reservar(self)

    def liberar(self):
        self.estado.liberar(self)

    def __repr__(self):
        estado_nombre = self.estado.__class__.__name__.replace('State', '')
        return f"Habitacion(Numero={self.numero}, Tipo={self.tipo}, Estado={estado_nombre})"
