import re
from pathlib import Path
import pdfplumber
from django.core.management.base import BaseCommand
from base_medicos.models import Medico, Especialidad, RegistroSuperintendencia, Institucion, OrdenProfesional
from datetime import datetime

class Command(BaseCommand):
    help = "Procesa los registros en archivos PDF para poblar Especialidad y RegistroSuperintendencia"

    def handle(self, *args, **kwargs):
        carpeta = Path('data/registro_superintendencia')
        archivos_pdf = carpeta.glob('*.pdf')

        for archivo in archivos_pdf:
            self.stdout.write(f"\nProcesando archivo: {archivo.name}")
            texto = self.extraer_texto_pdf(archivo)            
            if not texto:
                self.stdout.write(f"No se pudo extraer texto del archivo: {archivo.name}")
                continue

            datos = self.extraer_datos(texto)

            if not datos:
                self.stdout.write(f"Error procesando el archivo: {archivo.name}")
                continue

            self.procesar_datos(datos)

    def extraer_texto_pdf(self, archivo):
        texto = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                texto += page.extract_text()
        return texto

    def extraer_datos(self, texto):
        try:
            rut = re.search(r'RUN:\s*([\d\.\-]+)', texto).group(1)
            nacionalidad = re.search(r'Nacionalidad:\s*([^\n]+)', texto).group(1)
            numero_registro = re.search(r'figura, bajo el N° (\d+)', texto).group(1)
            fecha_registro = re.search(r'Fecha de registro:\s*(\d{2}/\d{2}/\d{4})', texto).group(1)
            fecha_nacimiento = re.search(r'Fecha nacimiento:\s*(\d{2}/\d{2}/\d{4})', texto).group(1)
            titulos_profesionales = self.extraer_profesiones(texto)
            especialidades = self.extraer_especialidades(texto)            
            return {
                'rut': rut,
                'numero_registro': numero_registro,
                'fecha_registro': fecha_registro,
                'fecha_nacimiento': fecha_nacimiento,
                'nacionalidad': nacionalidad,
                'titulos_profesionales': titulos_profesionales,
                'especialidades': especialidades
            }
        except Exception as e:
            self.stdout.write(f"Error al extraer datos: {e}")
            return None

    def extraer_especialidades(self, texto):
        """
        Extrae las especialidades de la sección "Especialidad Certificada" en el texto del PDF,
        manejando descripciones que pueden abarcar múltiples líneas y considerando variaciones
        en la frase "otorgado por" o "otorgado por la" para el nombre de la institución.
        """
        especialidades = []
        try:
            # Localizar la sección de especialidades certificadas
            inicio = texto.find("Especialidad Certificada:")
            if inicio == -1:
                return especialidades  # No se encontró la sección, retornar lista vacía
    
            fin = texto.find("Otorgado en", inicio)
            if fin == -1:
                fin = len(texto)  # Si no encuentra "Otorgado en", asumir que llega al final del texto
    
            # Extraer el bloque de texto relevante para las especialidades
            especialidades_texto = texto[inicio:fin].splitlines()

            i = 0
            while i < len(especialidades_texto):
                linea = especialidades_texto[i].strip()
                # Identificar líneas que comienzan con un guion
                if linea.startswith("-"):
                    # Obtener el nombre de la especialidad (remover el guion inicial)
                    nombre_especialidad = linea.lstrip("-").strip()
                    descripcion = ""
    
                    # Recorrer las líneas siguientes para construir la descripción completa
                    i += 1
                    while i < len(especialidades_texto):
                        siguiente_linea = especialidades_texto[i].strip()
                        # Detenerse si encuentra otra especialidad o el fin de la sección
                        if siguiente_linea.startswith("-") or "Otorgado en" in siguiente_linea:
                            break
                        descripcion += siguiente_linea + " "
                        i += 1

                    # Extraer la institución usando variantes de "otorgado por"
                    institucion_match = re.search(
                        r'otorgado por(?: la)? (.*?)(?:,| emitido)', descripcion)
                    institucion = institucion_match.group(1).strip() if institucion_match else "No especificada"
    
                    # Extraer la primera fecha en formato DD/MM/AAAA
                    fecha_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', descripcion)
                    fecha_certificacion = fecha_match.group(0) if fecha_match else "No especificada"
    
                    # Agregar especialidad a la lista
                    especialidades.append({
                        'nombre': nombre_especialidad,
                        'descripcion': descripcion.strip(),
                        'institucion': institucion,
                        'fecha_certificacion': fecha_certificacion
                    })
                else:
                    i += 1
        except Exception as e:
            self.stdout.write(f"Error al extraer especialidades: {e}")
        
        return especialidades
    
    def extraer_profesiones(self, texto):
        """
        Extrae los titulos profesionales de la sección "Orden Profesional" en el texto del PDF,
        manejando descripciones que pueden abarcar múltiples líneas y considerando variaciones
        en la frase "otorgado por" o "otorgado por la" para el nombre de la institución.
        """
        profesiones = []
        try:
            # Localizar la sección de profesiones certificadas
            inicio = texto.find("Orden Profesional:")
            if inicio == -1:
                return profesiones  # No se encontró la sección, retornar lista vacía

            fin = texto.find("Especialidad Certificada:", inicio)
            if fin == -1:
                fin = texto.find("Otorgado en", inicio)
                if fin == -1:
                    fin = len(texto)  # Si no encuentra "Otorgado en", asumir que llega al final del texto

            # Extraer el bloque de texto relevante para las profesiones
            profesiones_texto = texto[inicio:fin].splitlines()
            i = 0
            while i < len(profesiones_texto):
                linea = profesiones_texto[i].strip()
                # Identificar líneas que comienzan con un guion
                if linea.startswith("-"):
                    # Obtener el nombre de la profesion (remover el guion inicial)
                    nombre_titulo = linea.lstrip("-").strip()
                    descripcion = ""

                    # Recorrer las líneas siguientes para construir la descripción completa
                    i += 1
                    while i < len(profesiones_texto):
                        siguiente_linea = profesiones_texto[i].strip()
                        # Detenerse si encuentra otra especialidad o el fin de la sección
                        if siguiente_linea.startswith("-") or "Especialidad Certificada:" in siguiente_linea or "Otorgado en" in siguiente_linea:
                            break
                        descripcion += siguiente_linea + " "
                        i += 1

                    # Extraer la institución usando variantes de "otorgado por"
                    institucion_match = re.search(
                        r'otorgado por(?: la)? (.*?)(?:,| emitido)', descripcion)
                    institucion = institucion_match.group(1).strip() if institucion_match else "No especificada"

                    # Extraer la primera fecha en formato DD/MM/AAAA
                    fecha_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', descripcion)
                    fecha_certificacion = fecha_match.group(0) if fecha_match else "No especificada"

                    # Agregar especialidad a la lista
                    profesiones.append({
                        'nombre': nombre_titulo,
                        'descripcion': descripcion.strip(),
                        'institucion': institucion,
                        'fecha_certificacion': fecha_certificacion
                    })
                else:
                    i += 1
        except Exception as e:
            self.stdout.write(f"Error al extraer profesiones: {e}")

        return profesiones

    def procesar_datos(self, datos):
        """
        Procesa los datos extraídos del PDF para poblar la base de datos, verificando la existencia de registros
        y actualizando/creando nuevos según sea necesario.
        """
        try:
            # Consultar o crear al médico basado en el RUT
            medico = Medico.objects.filter(rut=datos['rut']).first()
            if not medico:
                self.stdout.write(f"Alerta: No se encontró el médico con RUT: {datos['rut']}.")
                return

            # Convertir fechas al formato esperado
            fecha_registro = self.convertir_fecha(datos['fecha_registro'])
            fecha_nacimiento = self.convertir_fecha(datos['fecha_nacimiento'])

            if not fecha_registro or not fecha_nacimiento:
                self.stdout.write(f"Error: Fechas inválidas para el RUT: {datos['rut']}.")
                return

            # Consultar o crear RegistroSuperintendencia
            registro, created = RegistroSuperintendencia.objects.update_or_create(
                numero_registro=datos['numero_registro'],
                defaults={
                    'fecha_registro': fecha_registro,
                    'fecha_nacimiento': fecha_nacimiento,
                    'nacionalidad': datos['nacionalidad'],
                }
            )

            # Procesar órdenes profesionales
            for orden_data in datos['titulos_profesionales']:
                institucion, _ = Institucion.objects.get_or_create(nombre=orden_data['institucion'])
                orden_existente = OrdenProfesional.objects.filter(
                    nombre=orden_data['nombre'],
                    institucion_certificadora=institucion
                ).first()

                if not orden_existente:
                    orden_profesional = OrdenProfesional.objects.create(
                        nombre=orden_data['nombre'],
                        descripcion=orden_data['descripcion'],
                        fecha_certificacion=self.convertir_fecha(orden_data['fecha_certificacion']),
                        institucion_certificadora=institucion
                    )
                    registro.ordenes_profesionales.add(orden_profesional)

            # Procesar especialidades
            for especialidad_data in datos['especialidades']:
                institucion, _ = Institucion.objects.get_or_create(nombre=especialidad_data['institucion'])
                especialidad_existente = Especialidad.objects.filter(
                    nombre=especialidad_data['nombre'],
                    institucion_certificadora=institucion
                ).first()

                if not especialidad_existente:
                    especialidad = Especialidad.objects.create(
                        nombre=especialidad_data['nombre'],
                        descripcion=especialidad_data['descripcion'],
                        fecha_certificacion=self.convertir_fecha(especialidad_data['fecha_certificacion']),
                        institucion_certificadora=institucion
                    )
                    registro.especialidades.add(especialidad)

            # Asociar el RegistroSuperintendencia al Médico
            medico.registro_superintendencia = registro
            medico.save()

            self.stdout.write(f"Datos procesados exitosamente para el RUT: {datos['rut']}")

        except Exception as e:
            self.stdout.write(f"Error al procesar datos: {e}")

    def convertir_fecha(self, fecha_str):
        """
        Convierte una fecha en formato DD/MM/YYYY a YYYY-MM-DD.
        Si la conversión falla, devuelve None.
        """
        try:
            return datetime.strptime(fecha_str, "%d/%m/%Y").date()
        except ValueError:
            self.stdout.write(f"Error al convertir la fecha: {fecha_str}")
            return None