# Utiliza una imagen oficial de Python slim para mantenerla ligera
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Variables de entorno para optimizar el comportamiento de Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependencias del sistema, incluyendo netcat-openbsd y cliente de PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client netcat-openbsd

# Instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del proyecto en el contenedor
COPY . .

# Establece el entrypoint para manejar la espera de PostgreSQL
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expone el puerto 8000 para el servicio de Django
EXPOSE 8000

# Ejecuta el entrypoint, que luego ejecutará el servidor de Django
ENTRYPOINT ["/app/entrypoint.sh"]

# CMD por defecto para iniciar Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]