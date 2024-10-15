from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base_colmed.models import Plaza, Entidad, Estamento, LugarDescuento
from base_medicos.models import Medico, Afiliacion
import pandas as pd
import os
from django.conf import settings
from datetime import datetime

class Command(BaseCommand):
    help = 'Carga datos desde colmed_aysen_unificado_actualizado.xlsx al nuevo modelo de base de datos'

    def handle(self, *args, **options):
        # Ruta al archivo Excel
        data_dir = os.path.join(settings.BASE_DIR, 'data')
        excel_file = os.path.join(data_dir, 'colmed_aysen_unificado_actualizado.xlsx')

        # Verificar si el archivo existe
        if not os.path.exists(excel_file):
            self.stderr.write(f'El archivo {excel_file} no existe.')
            return

        # Leer el archivo Excel en un DataFrame de pandas
        try:
            df = pd.read_excel(excel_file, dtype=str)
        except Exception as e:
            self.stderr.write(f'Error al leer el archivo Excel: {e}')
            return

        self.stdout.write('Cargando Plazas y Estamentos...')
        # Cargar Plazas
        plazas_info = {
            1101: 'DIRECCIÓN SERVICIO SALUD',
            1102: 'SALUD RURAL',
            1106: 'HOSPITAL COYHAIQUE',
            1116: 'HOSPITAL PUERTO AYSÉN',
            1117: 'HOSPITAL DR. LEOPOLDO ORTEGA RODRÍGUEZ',
            1118: 'HOSPITAL LORD COCHRANE',
            1119: 'HOSPITAL DR. JORGE IBAR',
            1120: 'CONSULTORIO DR. ALEJANDRO GUTIERREZ',
            1121: 'CONSULTORIO VÍCTOR DOMINGO SILVA',
        }

        for codigo, nombre in plazas_info.items():
            plaza, created = Plaza.objects.get_or_create(codigo=codigo)
            if created or plaza.nombre != nombre:
                plaza.nombre = nombre
                plaza.save()
                self.stdout.write(f'{"Creada" if created else "Actualizada"} Plaza código {codigo}: {nombre}')

        # Cargar Estamentos
        estamentos_info = {
            209: 'COLEGIO',
            210: 'FSG',
            211: 'CLUB CAMPO',
            212: 'FALMED',
            6533: 'FATMED',
        }

        for codigo, nombre in estamentos_info.items():
            estamento, created = Estamento.objects.get_or_create(codigo_estamento=str(codigo))
            if created or estamento.nombre_estamento != nombre:
                estamento.nombre_estamento = nombre
                estamento.save()
                self.stdout.write(f'{"Creado" if created else "Actualizado"} Estamento código {codigo}: {nombre}')

        self.stdout.write('Plazas y Estamentos cargados.')

        self.stdout.write('Procesando Médicos...')

        # Crear las entidades si no existen
        entidades_info = [
            {'nombre_entidad': 'Colegio Médico', 'sigla': 'COLMED'},
            {'nombre_entidad': 'Fundación de Asistencia Legal del Colegio Médico de Chile', 'sigla': 'FALMED'},
            {'nombre_entidad': 'Fundación de Asistencia Tributaria del Colegio Médico de Chile', 'sigla': 'FATMED'},
            {'nombre_entidad': 'Club de Campo', 'sigla': 'CLUB CAMPO'},
            {'nombre_entidad': 'Fondo Solidaridad Gremial', 'sigla': 'FSG'},
        ]

        entidades = {}
        for entidad_data in entidades_info:
            entidad, created = Entidad.objects.get_or_create(
                sigla=entidad_data['sigla'],
                defaults={'nombre_entidad': entidad_data['nombre_entidad']}
            )
            entidades[entidad.sigla] = entidad
            if created:
                self.stdout.write(f'Creada Entidad: {entidad.nombre_entidad}')

        def normalizar_rut(rut):
            if not rut:
                return None
            rut = rut.replace('.', '').replace(' ', '')
            rut = rut.upper()
            return rut

        for index, row in df.iterrows():
            rut = row.get('RUT')
            nombre_completo = row.get('NOMBRE COMPLETO')
            email = row.get('CORREO ELECTRÓNICO')
            celular = row.get('CELULAR')
            direccion = row.get('DIRECCIÓN')
            comuna = row.get('COMUNA')
            estab = row.get('ESTAB')
            plaza_nombre = row.get('PLAZA')
            contacto = celular
            direccion_full = ''
            plaza = self.validar_plaza(plaza_nombre, estab)

            rut_normalizado = normalizar_rut(rut)

            if not rut_normalizado or not nombre_completo:
                self.stdout.write(f'Fila {index + 2} omitida: RUT o NOMBRE COMPLETO faltante o inválido.')
                continue

            # Obtener otros campos adicionales
            icm = row.get('ICM')
            fecha_nacimiento = self.parse_fecha(row.get('FECHA NACIMIENTO'))
            fecha_titulo = self.parse_fecha(row.get('FECHA TITULO'))
            condicion_vital = row.get('CONDICIONVITAL')

            if pd.notnull(rut) and pd.notnull(nombre_completo):
                # Preparar datos del Usuario
                password = str(rut_normalizado).strip()
                nombre_completo = nombre_completo.strip()
                name_parts = nombre_completo.split()
                # Ajustar nombres y apellidos según cantidad de palabras
                if len(name_parts) >= 2:
                    last_name = ' '.join(name_parts[:2])
                    first_name = ' '.join(name_parts[2:])
                else:
                    last_name = name_parts[0]
                    first_name = ''

                # Asignar username
                if pd.notnull(email) and email.strip():
                    username = email.strip()
                else:
                    username = nombre_completo.replace(' ', '_')

                # Asegurar unicidad del username
                original_username = username
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1

                user_qs = User.objects.filter(username__iexact=username)
                if user_qs.exists():
                    user = user_qs.first()
                    created = False
                    self.stdout.write(f'Usuario {username} ya existe.')
                else:
                    user = User(username=username)
                    created = True

                user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                if pd.notnull(email):
                    user.email = email.strip()
                user.save()
                if created:
                    self.stdout.write(f'Creado Usuario {username}.')
                else:
                    self.stdout.write(f'Actualizado Usuario {username}.')

                # Procesar Medico
                try:
                    medico = Medico.objects.get(rut=rut_normalizado)
                    # Medico existe
                    self.stdout.write(f'Medico con RUT {rut_normalizado} ya existe.')
                    updated = False
                    if medico.user != user:
                        medico.user = user
                        updated = True
                    if contacto and medico.contacto != contacto:
                        medico.contacto = contacto
                        updated = True
                    if direccion and medico.direccion != direccion:
                        medico.direccion = direccion
                        updated = True
                    if comuna and medico.comuna != comuna:
                        medico.comuna = comuna
                        updated = True
                    if pd.notnull(condicion_vital) and medico.condicion_vital != condicion_vital:
                        medico.condicion_vital = condicion_vital
                        updated = True
                    if plaza and medico.plaza != plaza:
                        medico.plaza = plaza
                        updated = True
                    # Actualizar otros campos
                    if pd.notnull(icm):
                        try:
                            icm_value = int(icm)
                            if medico.icm != icm_value:
                                medico.icm = icm_value
                                updated = True
                        except ValueError:
                            self.stdout.write(f'Valor ICM inválido en fila {index + 2}')

                    if fecha_nacimiento and medico.fecha_nacimiento != fecha_nacimiento:
                        medico.fecha_nacimiento = fecha_nacimiento
                        updated = True
                    if fecha_titulo and medico.fecha_titulo != fecha_titulo:
                        medico.fecha_titulo = fecha_titulo
                        updated = True
                    if updated:
                        medico.save()
                        self.stdout.write(f'Actualizado Medico con RUT {rut}.')
                except Medico.DoesNotExist:
                    self.stdout.write(f'Medico con RUT {rut} no existe. Ingresando...')
                    # Crear nuevo Medico
                    medico = Medico(user=user, rut=rut_normalizado)
                    medico.plaza = plaza
                    medico.contacto = contacto
                    medico.direccion = direccion
                    medico.comuna = comuna
                    medico.condicion_vital = condicion_vital
                    # Asignar otros campos
                    if pd.notnull(icm):
                        try:
                            medico.icm = int(icm)
                        except ValueError:
                            medico.icm = None
                            self.stdout.write(f'Valor ICM inválido en fila {index + 2}')
                    if fecha_nacimiento:
                        medico.fecha_nacimiento = fecha_nacimiento
                    if fecha_titulo:
                        medico.fecha_titulo = fecha_titulo
                    medico.save()
                    self.stdout.write(f'Creado Medico con RUT {rut}.')

                # Procesar Afiliaciones
                self.procesar_afiliaciones(medico, row, entidades)

            else:
                self.stdout.write(f'Fila {index + 2} omitida: RUT o NOMBRE COMPLETO faltante.')

        self.stdout.write('Carga de datos completada.')

    def validar_plaza(self, plaza_nombre, estab):
        # Procesar Plazas
        if pd.notnull(estab) and pd.notnull(plaza_nombre):
            # ESTAB corresponde a 'codigo'
            try:
                codigo = int(estab)
                nombre = str(plaza_nombre).strip()
                # Verificar si la Plaza con este código ya existe
                plaza, created = Plaza.objects.get_or_create(codigo=codigo, defaults={'nombre': nombre})
                if not created and plaza.nombre != nombre:
                    plaza.nombre = nombre
                    plaza.save()
                    self.stdout.write(f'Actualizada Plaza código {codigo} con nombre {nombre}.')
                return plaza
            except ValueError:
                self.stdout.write(f'Código de Plaza inválido en fila con ESTAB {estab}')
                return None
        else:
            # ESTAB y PLAZA están vacíos o nulos, no insertar
            return None

    def parse_fecha(self, fecha_str):
        # Convertir una cadena de fecha en objeto datetime.date
        if pd.notnull(fecha_str) and fecha_str != '':
            try:
                fecha = pd.to_datetime(fecha_str, errors='coerce')
                if fecha and fecha.date() != datetime(1900, 1, 1).date():
                    return fecha.date()
            except Exception as e:
                pass
        return None

    def procesar_afiliaciones(self, medico, row, entidades):
        # Función para obtener la clave de estado_pago a partir del valor del Excel
        def obtener_valor_estado_pago(valor_excel):
            valor_excel = valor_excel.strip().upper()
            estado_pago_choices = Afiliacion._meta.get_field('estado_pago').choices
            for key, display in estado_pago_choices:
                if display.upper() == valor_excel:
                    return key
            return None

        # Procesar afiliaciones para las entidades
        # Lista de entidades y los campos correspondientes
        afiliaciones_info = [
            {
                'entidad_sigla': 'COLMED',
                'codigo_socio_col': 'C. SOCIO COL',
                'estado_pago_col': 'ESTADO PAGO COL',
                'anio_ucp_col': 'AÑO UCP COL',
                'mes_ucp_col': 'MES UCP COL',
                'estamento_col': 'ESTAMENTO COL',
                'cod_estamento_col': 'CODESTAMENTOCOL',
                'num_cuota_col': 'NUMCUOTACOL',
                'lugar_descuento_col': 'LUGAR DESCUENTO COL',
                'tipo_cuota': 'F. CUOTA COL',
                'fecha_inscripcion_col': 'F. INSCRIPCION COL',
            },
            {
                'entidad_sigla': 'FSG',
                'codigo_socio_col': 'C. SOCIO FSG',
                'estado_pago_col': 'ESTADO PAGO FSG',
                'anio_ucp_col': 'AÑO UCP FSG',
                'mes_ucp_col': 'MES UCP FSG',
                'estamento_col': 'ESTAMENTO FSG',
                'cod_estamento_col': 'CODESTAMENTOFSG',
                'num_cuota_col': 'NUMCUOTAFSG',
                'lugar_descuento_col': 'LUGAR DESCUENTO FSG',
                'tipo_cuota': 'F. CUOTA FSG',
                'fecha_inscripcion_col': 'F. INSCRIPCION FSG',
            },
            {
                'entidad_sigla': 'FALMED',
                'codigo_socio_col': 'C. SOCIO FALMED',
                'estado_pago_col': 'ESTADO PAGO FALMED',
                'anio_ucp_col': 'AÑO UCP FALMED',
                'mes_ucp_col': 'MES UCP FALMED',
                'estamento_col': 'ESTAMENTO FALMED',
                'cod_estamento_col': 'CODESTAMENTOFALMED',
                'num_cuota_col': 'NUMCUOTAFALMED',
                'lugar_descuento_col': 'LUGAR DESCUENTO FALMED',
                'tipo_cuota': 'F. CUOTA FALMED',
                'fecha_inscripcion_col': 'F. INSCRIPCION FALMED',
            },
            {
                'entidad_sigla': 'CLUB CAMPO',
                'codigo_socio_col': 'C. SOCIO CLUB',
                'estado_pago_col': 'ESTADO PAGO CLUB',
                'anio_ucp_col': 'AÑO UCP CLUB',
                'mes_ucp_col': 'MES UCP CLUB',
                'estamento_col': 'ESTAMENTO CLUB',
                'cod_estamento_col': 'CODESTAMENTOCLUB',
                'num_cuota_col': 'NUMCUOTACLUB',
                'lugar_descuento_col': 'LUGAR DESCUENTO CLUB',
                'tipo_cuota': 'F. CUOTA CLUB',
                'fecha_inscripcion_col': 'F. INSCRIPCION CLUB',
            },
            {
                'entidad_sigla': 'FATMED',
                'codigo_socio_col': 'C. SOCIO FATMED',
                'estado_pago_col': 'ESTADO PAGO FATMED',
                'anio_ucp_col': 'AÑO UCP FATMED',
                'mes_ucp_col': 'MES UCP FATMED',
                'estamento_col': 'ESTAMENTO FATMED',
                'cod_estamento_col': 'CODESTAMENTOFATMED',
                'num_cuota_col': 'NUMCUOTAFATMED',
                'lugar_descuento_col': 'LUGAR DESCUENTO FATMED',
                'tipo_cuota': 'F. CUOTA FATMED',
                'fecha_inscripcion_col': 'F. INSCRIPCION FATMED',
            },
        ]

        for afiliacion_info in afiliaciones_info:
            entidad_sigla = afiliacion_info['entidad_sigla']
            entidad = entidades.get(entidad_sigla)
            fecha_inscripcion_str = row.get(afiliacion_info['fecha_inscripcion_col'])
            fecha_inscripcion = self.parse_fecha(fecha_inscripcion_str)

            # Solo crear afiliación si la fecha de inscripción es válida y distinta de '1900-01-01'
            if fecha_inscripcion:
                # Verificar si ya existe la afiliación
                afiliacion, created = Afiliacion.objects.get_or_create(
                    medico=medico,
                    entidad=entidad,
                    defaults={
                        'fecha_inscripcion': fecha_inscripcion
                    }
                )
                updated = False
                if not created:
                    # Actualizar campos si es necesario
                    if afiliacion.fecha_inscripcion != fecha_inscripcion:
                        afiliacion.fecha_inscripcion = fecha_inscripcion
                        updated = True

                # Asignar otros campos
                condicion_afiliado = row.get(afiliacion_info['codigo_socio_col'])
                estado_pago_excel = row.get(afiliacion_info['estado_pago_col'])

                if pd.notnull(estado_pago_excel) and estado_pago_excel.strip() != '':
                    estado_pago_value = obtener_valor_estado_pago(estado_pago_excel)
                    if estado_pago_value:
                        if afiliacion.estado_pago != estado_pago_value:
                            afiliacion.estado_pago = estado_pago_value
                            updated = True
                    else:
                        self.stdout.write(f'Estado de pago inválido "{estado_pago_excel}" para {medico}')
                else:
                    # Manejar caso de estado_pago nulo o vacío
                    if afiliacion.estado_pago != 'no_aplica':
                        afiliacion.estado_pago = 'no_aplica'
                        updated = True

                anio_ucp = row.get(afiliacion_info['anio_ucp_col'])
                mes_ucp = row.get(afiliacion_info['mes_ucp_col'])
                estamento_nombre = row.get(afiliacion_info['estamento_col'])
                cod_estamento = row.get(afiliacion_info['cod_estamento_col'])
                num_ultima_cuota = row.get(afiliacion_info['num_cuota_col'])
                lugar_descuento_nombre = row.get(afiliacion_info['lugar_descuento_col'])
                tipo_cuota = row.get(afiliacion_info['tipo_cuota'])

                if pd.notnull(condicion_afiliado) and afiliacion.condicion_afiliado != condicion_afiliado:
                    afiliacion.condicion_afiliado = condicion_afiliado
                    updated = True

                if pd.notnull(anio_ucp):
                    try:
                        afiliacion.anio_ucp = int(anio_ucp)
                        updated = True
                    except ValueError:
                        pass
                if pd.notnull(mes_ucp):
                    try:
                        afiliacion.mes_ucp = int(mes_ucp)
                        updated = True
                    except ValueError:
                        pass
                if pd.notnull(estamento_nombre):
                    estamento, _ = Estamento.objects.get_or_create(
                        nombre_estamento=estamento_nombre.strip(),
                        defaults={'codigo_estamento': cod_estamento}
                    )
                    if afiliacion.estamento != estamento:
                        afiliacion.estamento = estamento
                        updated = True
                if pd.notnull(num_ultima_cuota):
                    try:
                        afiliacion.num_ultima_cuota = int(num_ultima_cuota)
                        updated = True
                    except ValueError:
                        pass
                if pd.notnull(lugar_descuento_nombre):
                    lugar_descuento, _ = LugarDescuento.objects.get_or_create(nombre_lugar=lugar_descuento_nombre.strip())
                    if afiliacion.lugar_descuento != lugar_descuento:
                        afiliacion.lugar_descuento = lugar_descuento
                        updated = True
                if pd.notnull(tipo_cuota):
                    afiliacion.tipo_cuota = tipo_cuota
                    updated = True

                if updated:
                    afiliacion.save()
                    self.stdout.write(f'Actualizada Afiliación de {medico} a {entidad.nombre_entidad}.')
                elif created:
                    self.stdout.write(f'Creada Afiliación de {medico} a {entidad.nombre_entidad}.')

    def normalizar_texto(self, texto):
        # Eliminar espacios extra, convertir a mayúsculas, eliminar acentos
        if not isinstance(texto, str):
            return texto
        texto = texto.strip()
        texto = ' '.join(texto.split())
        texto = texto.upper()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        return texto
