from datetime import datetime

def convertir_fecha(fecha_str):
    # """
    # Convierte una fecha en formato dd-mm-aaaa a aaaa-mm-dd.
    # Retorna None si el formato es incorrecto o la fecha está vacía.
    # """
    
    # try:
    #     return datetime.strptime(fecha_str, "%d-%m-%Y").date()
    # except (ValueError, TypeError):
    #     return None
    """
    Convierte una fecha en formato dd-mm-aaaa o dd/mm/aaaa a aaaa-mm-dd.
    Retorna None si el formato es incorrecto o la fecha está vacía.
    """
    if not fecha_str:
        return None

    # Reemplazar barras por guiones si existen
    fecha_str = fecha_str.replace('/', '-')
    # try:
    #     return datetime.strptime(fecha_str, "%d-%m-%Y").date()
    # except (ValueError, TypeError):
    #     return None
    # Intentar yyyy-mm-dd
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    # Intentar dd-mm-yyyy
    try:
        return datetime.strptime(fecha_str, '%d-%m-%Y').date()
    except ValueError:
        pass

    # Ningún formato coincidió
    return None
