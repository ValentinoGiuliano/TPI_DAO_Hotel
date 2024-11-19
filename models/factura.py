# models/factura.py

class Factura:
    def __init__(self, id, cliente_dni, reserva_id, fecha_emision, total):
        self.id = id
        self.cliente_dni = cliente_dni
        self.reserva_id = reserva_id
        self.fecha_emision = fecha_emision
        self.total = total

    def __repr__(self):
        return f"Factura(ID={self.id}, ClienteDNI={self.cliente_dni}, ReservaID={self.reserva_id}, FechaEmision={self.fecha_emision}, Total={self.total})"
