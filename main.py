# main.py

from gui.app import HotelApp
from database import DatabaseConnection

if __name__ == "__main__":
    db = DatabaseConnection()
    db.actualizar_estado_habitaciones()  # Actualizar estados al iniciar
    app = HotelApp()
    app.mainloop()
