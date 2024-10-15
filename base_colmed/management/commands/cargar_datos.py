import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from base_medicos.models import Medico
from base_colmed.models import Plaza, Beneficio
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Analiza los archivos CSV, cruza información y muestra cómo se verían los datos en la BD sin insertarlos.'

    def handle(self, *args, **kwargs):
        data_path = '/data'
        archivos = [
            'COLEGIADOS-COLMED(Recuperado automáticamente)-Hoja2.csv',
            'COLEGIADOS-COLMED(Recuperado automáticamente)-correos.csv',
            'COLEGIADOS-COLMED(Recuperado automáticamente)-Hoja4.csv',
            'COLEGIADOS-COLMED(Recuperado automáticamente)-A-Z.csv',

            'COLEGIADOS-COLMED-Hoja2.csv',
            'COLEGIADOS-COLMED-Hoja1.csv',

            'BASE-ley15076.csv',
            'BASE-ley 19664.csv',
            'BASE-ESTABLECIMIENTO.csv',
            'BASE-H.PUERTOCISNES.csv',
            'BASE-H.COCHRANE.csv',
            'BASE-H.CHILECHICO.csv',
            'BASE-HRC.csv',
            'BASE-PUERTO AYSEN.csv',

            'BASE SSA MARZO24-ley15076.csv',
            'BASE SSA MARZO24-ley 19664.csv',
            'BASE SSA MARZO24-ESTABLECIMIENTO.csv',
            'BASE SSA MARZO24-H.PUERTOCISNES.csv',
            'BASE SSA MARZO24-H.COCHRANE.csv',
            'BASE SSA MARZO24-H.CHILECHICO.csv',
            'BASE SSA MARZO24-HRC.csv',
            'BASE SSA MARZO24-PUERTO AYSEN.csv',

            'LIBERADOS.csv',

            'COLMED - LIBERADOS-Hoja2.csv',
            'COLMED - LIBERADOS-CORREOS.csv',

            'MGZ-todos.csv',

            'MGZ.csv',

            'MOROSOS-COLMED-Hoja2.csv',
            'MOROSOS-COLMED-CORREOS.csv',
        ]
        
        for archivo in archivos:
            file_path = os.path.join(data_path, archivo)
            self.stdout.write(f"Analizando {archivo}...")
            self.procesar_archivo(file_path)

    def procesar_archivo(self, file_path):
        """
        Procesa el archivo CSV y muestra un 'print' de cómo se verían los datos
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch_size = 100
            batch = []

            for idx, row in enumerate(reader):
                batch.append(row)

                # Procesar en lotes de 100 filas
                if len(batch) == batch_size:
                    self.procesar_lote(batch, file_path)
                    batch = []

            # Procesar el lote restante
            if batch:
                self.procesar_lote(batch, file_path)

    def procesar_lote(self, batch, file_path):
        """
        Procesa un lote de datos, cruza información y genera 'print' con los resultados del análisis.
        """
        for row in batch:
            # Dependiendo del archivo, determinar si se están procesando Médicos, Plazas o Beneficios
            if 'Icm' in row:
                self.procesar_medico(row, file_path)
            elif 'Plaza' in row:
                self.procesar_plaza(row, file_path)
            elif 'descripcion' in row:
                self.procesar_beneficio(row, file_path)

    def procesar_medico(self, row, file_path):
        """
        Procesa y valida la información de un médico, incluyendo la relación con plazas y beneficios.
        """
        icm = row.get('Icm', '').strip()
        rut = row.get('Rut', '').strip()
        nombre = row.get('Nombre', '').strip().capitalize()
        paterno = row.get('A. Paterno', '').strip().capitalize()
        materno = row.get('A. Materno', '').strip().capitalize()
        email = row.get('E-Mail', '').strip().lower()
        celular = row.get('Celular', '').strip() or 'Sin celular'
        fecha_nacimiento = self.normalizar_fecha(row.get('Fecha Nacimiento'))
        fecha_titulo = self.normalizar_fecha(row.get('Fecha Título'))

        # Buscar si el médico ya existe
        medico = Medico.objects.filter(icm=icm).first()

        if not medico:
            print(f"Simulación de nuevo Médico:")
            print(f"  ICM: {icm}")
            print(f"  Rut: {rut}")
            print(f"  Nombre Completo: {nombre} {paterno} {materno}")
            print(f"  Email: {email}")
            print(f"  Celular: {celular}")
            print(f"  Fecha Nacimiento: {fecha_nacimiento}")
            print(f"  Fecha Título: {fecha_titulo}")
        else:
            print(f"Médico ya existente: {medico}")

        # Buscar relación con plaza
        plaza_nombre = row.get('Plaza', '').strip()
        if plaza_nombre:
            plaza = Plaza.objects.filter(nombre=plaza_nombre).first()
            if not plaza:
                print(f"  No se encontró la plaza '{plaza_nombre}', creando simulación de nueva plaza.")
            else:
                print(f"  Médico relacionado con la plaza '{plaza_nombre}'.")

        # Aquí podría cruzarse información adicional de beneficios o cuotas si está presente
        print("-" * 50)

    def procesar_plaza(self, row, file_path):
        """
        Procesa y valida la información de plazas, cruzando datos entre archivos cuando sea necesario.
        """
        nombre_plaza = row.get('Plaza', '').strip()
        codigo_plaza = row.get('Estab', '').strip()

        # Buscar plaza por nombre o código
        plaza = Plaza.objects.filter(nombre=nombre_plaza).first()
        if not plaza and codigo_plaza:
            plaza = Plaza.objects.filter(codigo=codigo_plaza).first()

        if not plaza:
            print(f"Simulación de nueva Plaza:")
            print(f"  Nombre: {nombre_plaza}")
            print(f"  Código: {codigo_plaza}")
        else:
            print(f"Plaza ya existente: {plaza}")

        print("-" * 50)

    def procesar_beneficio(self, row, file_path):
        """
        Procesa y valida la información de beneficios.
        """
        descripcion = row.get('descripcion', '').strip()

        # Buscar si el beneficio ya existe
        beneficio = Beneficio.objects.filter(descripcion=descripcion).first()

        if not beneficio:
            print(f"Simulación de nuevo Beneficio:")
            print(f"  Descripción: {descripcion}")
        else:
            print(f"Beneficio ya existente: {beneficio}")

        print("-" * 50)

    def normalizar_fecha(self, fecha_str):
        """
        Convierte la fecha de DD-MM-AAAA HH:MM:SS a YYYY-MM-DD
        """
        if not fecha_str:
            return None
        try:
            return datetime.strptime(fecha_str, '%d-%m-%Y %H:%M:%S').date()
        except ValueError:
            try:
                return datetime.strptime(fecha_str, '%d-%m-%Y').date()
            except ValueError:
                return None
