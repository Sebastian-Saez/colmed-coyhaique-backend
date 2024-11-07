from datetime import datetime

def convertir_fecha(fecha_str):
    """
    Convierte una fecha en formato dd-mm-aaaa a aaaa-mm-dd.
    Retorna None si el formato es incorrecto o la fecha está vacía.
    """
    
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y").date()
    except (ValueError, TypeError):
        return None
