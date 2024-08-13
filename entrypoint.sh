#!/bin/sh

# Espera a que PostgreSQL esté listo
echo "Inicio de espera de PostgreSQL..."
#!/bin/sh

# Verifica si se está utilizando PostgreSQL
if [ "$DATABASE" = "postgres" ]
then
    echo "Esperando a PostgreSQL..."

    # Espera hasta que PostgreSQL esté listo
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL está listo"
fi

# Ejecuta las migraciones al iniciar (si es necesario)
python manage.py migrate --no-input

# Ejecuta el comando dado por defecto (inicia el servidor Django)
exec "$@"

