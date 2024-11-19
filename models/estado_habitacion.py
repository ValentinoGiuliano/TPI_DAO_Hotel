# models/estado_habitacion.py

from abc import ABC, abstractmethod

class EstadoHabitacion(ABC):
    @abstractmethod
    def reservar(self, habitacion):
        pass

    @abstractmethod
    def liberar(self, habitacion):
        pass

class DisponibleState(EstadoHabitacion):
    def reservar(self, habitacion):
        habitacion.cambiar_estado(OcupadaState())

    def liberar(self, habitacion):
        print(f"Habitación {habitacion.numero} ya está disponible.")

class OcupadaState(EstadoHabitacion):
    def reservar(self, habitacion):
        print(f"Habitación {habitacion.numero} ya está ocupada.")

    def liberar(self, habitacion):
        habitacion.cambiar_estado(DisponibleState())
