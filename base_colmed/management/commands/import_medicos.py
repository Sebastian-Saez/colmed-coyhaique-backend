import os
import io
import pandas as pd
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import F, Value, Func,Count
from collections import defaultdict

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload


from base_colmed.models import Entidad, Estamento, LugarDescuento, Plaza, Perfil
from base_medicos.models import Medico, Afiliacion
from backend_colmed.settings import GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_DRIVE_SR

class Command(BaseCommand):
    help = "Importa o actualiza registros de médicos del Colegio Médico Aysén desde un Excel Sistema de Recaudación"

    def add_arguments(self, parser):
        parser.add_argument(
            "--excel-out",
            type=str,
            default="medicos_temporal.xlsx",
            help="Nombre del archivo Excel temporal que se guardará localmente."
        )

    def handle(self, *args, **options):
        
        drive_dir = GOOGLE_DRIVE_SR # Directorio desde la variable de entorno
        if not drive_dir:
            raise CommandError("No se encontró la variable de entorno GOOGLE_DRIVE_SR (ID de la carpeta).")
        
        service_account_json = GOOGLE_SERVICE_ACCOUNT_JSON

        if not service_account_json or not os.path.isfile(service_account_json):
            raise CommandError("No se encontró el JSON de credenciales en la variable GOOGLE_SERVICE_ACCOUNT_JSON.")
        
        local_tmp_dir = getattr(settings, "LOCAL_TMP_DIR", None)

        if not local_tmp_dir:
            # Si no existe la variable, usar un directorio por defecto
            self.stdout.write(self.style.WARNING(
                "settings.LOCAL_TMP_DIR no está definido, usando '/tmp' como fallback."
            ))
            local_tmp_dir = "/tmp"

        # Crear el directorio si no existe
        os.makedirs(local_tmp_dir, exist_ok=True)
        excel_filename = options["excel_out"]
        local_xlsx_path = os.path.join(local_tmp_dir, excel_filename)

        #SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
        SCOPES = ["https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_file(
            service_account_json, scopes=SCOPES
        )
        drive_service = build("drive", "v3", credentials=creds)

        # 3) Listar archivos en la carpeta, filtrar XLSX, orden por modifiedTime desc
        query = (
            f"'{drive_dir}' in parents "
            "and trashed=false "
            "and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
        )

        try:
            response = drive_service.files().list(
                q=query,
                orderBy="modifiedTime desc",
                pageSize=1,  # sólo queremos el más reciente
                fields="files(id, name, modifiedTime)"
            ).execute()
        except Exception as e:
            raise CommandError(f"Error al listar archivos en carpeta {drive_dir}: {e}")
        
        files = response.get("files", [])
        if not files:
            raise CommandError("No se encontraron archivos XLSX en la carpeta de Drive especificada.")
        

        # Tomar el primero => el más reciente
        newest_file = files[0]
        file_id = newest_file["id"]
        file_name = newest_file["name"]
        self.stdout.write(self.style.WARNING(
            f"Archivo más reciente encontrado: {file_name} (ID={file_id})."
        ))


        # 4) Descargar el archivo
        self.descargar_archivo(drive_service, file_id, local_xlsx_path)
        self.stdout.write(self.style.SUCCESS(f"Archivo descargado localmente: {local_xlsx_path}."))

        # 5) Procesar con pandas
        try:
            df = pd.read_excel(local_xlsx_path, dtype=str)
        except Exception as e:
            self._eliminar_archivo(local_xlsx_path)
            raise CommandError(f"Error al leer el Excel: {e}")
        
        # Lógica de importación
        total_filas = 0
        num_creados = 0
        num_actualizados = 0
        num_errores = 0
        errores = []
        
        for idx, row in df.iterrows():
            total_filas += 1
            try:
                icm_val = row.get("Icm")  # Columna 'Icm'
                rut_val = row.get("Rut")  # Col 'Rut' con DV, ej: '12345678-9'
                # remove DV => '12345678'
                rut_sin_dv = self.limpiar_rut(rut_val)

                # nombre_val = row.get("Nombre", "")
                # a_paterno_val = row.get("A. Paterno", "")
                # a_materno_val = row.get("A. Materno", "")
                nombre_val = str(row.get("Nombre", "")).strip() if pd.notna(row.get("Nombre")) else ""
                a_paterno_val = str(row.get("A. Paterno", "")).strip() if pd.notna(row.get("A. Paterno")) else ""
                a_materno_val = str(row.get("A. Materno", "")).strip() if pd.notna(row.get("A. Materno")) else ""
                # Otras columnas
                fecha_nac_str = row.get("Fecha Nacimiento", "")
                fecha_titulo_str = row.get("Fecha Titulo", "")
                condicion_vital_val = row.get("CondicionVital", "")
                email_val = row.get("E-Mail", "")
                celular_val = row.get("Celular", "")
                direccion_val = row.get("Dirección", "")
                comuna_val = row.get("Comuna", "")
                

                icm_int = self.parse_icm(icm_val)
                if not icm_int and not rut_val:
                    raise ValueError("No se encontró ICM ni Rut en la fila")

                # Buscar medico
                medico = None
                # Prioridad: buscar por ICM
                if icm_val and pd.notna(icm_val):
                    medico = Medico.objects.filter(icm=icm_int).first()
                
                
                if not medico and rut_val:
                    # medico = Medico.objects.filter(rut=rut_val).first()
                    medico = Medico.objects.annotate(
                        rut_sin_dv_db=Func(
                            F('rut'),
                            Value('-[^-]+$'),  # Expresión regex que elimina el DV
                            Value(''),
                            function='regexp_replace'
                        )
                    ).filter(rut_sin_dv_db=rut_sin_dv).first()
                    
                    
                creado = False
                # Crear user si no existe
                if not medico:
                    #Crear un user con username => 'icm_XXXX' o 'rut_XXXXX'
                    # if icm_val and pd.notna(icm_val):
                    #     username_def = f"icm_{int(float(icm_val))}"
                    # else:
                    #     username_def = f"rut_{rut_val}"
                    
                    nombre_completo = nombre_val+'_'+a_paterno_val+'_'+a_materno_val
                    #nombre_completo = self.obtener_nombre_usuario(row)
                
                    # Ajustes para garantizar unicidad
                    base_user = nombre_completo
                    counter = 1
                    while User.objects.filter(username=nombre_completo).exists():
                        base_user = f"{nombre_completo}_{counter}"
                        counter += 1
                
                    user_obj = User.objects.create_user(
                        username=nombre_completo,
                        password="changeme123"
                    )

                    # Crear perfil “visitante”
                    Perfil.objects.create(user=user_obj, tipo_perfil='visitante', activo=True)
                    medico = Medico.objects.create(
                        user=user_obj,
                        icm=icm_int,
                        rut=rut_val
                    )

                    creado = True
                    # self.stdout.write(
                    #     f"[DRY-RUN] Fila {idx+2}: Crear un nuevo User y Medico -> "
                    #     f"ICM={icm_int} RUT(sin DV)={rut_sin_dv}, NOMBRE={nombre_val}, APELLIDOS={a_paterno_val} {a_materno_val}"
                    # )
                    num_creados += 1
                else:
                    
                    user_obj = medico.user  # En caso de actualizaciones
                    if medico.user:
                        perfil, creado_perfil = Perfil.objects.get_or_create(
                            user=medico.user,
                            defaults={'tipo_perfil': 'visitante', 'activo': True}
                        )
                    if not creado_perfil:
                        # Si ya existía, asegurarse de que tiene los valores correctos
                        if perfil.tipo_perfil != 'visitante' or not perfil.activo:
                            perfil.tipo_perfil = 'visitante'
                            perfil.activo = True
                            perfil.save()
                    # self.stdout.write(
                    #     f"[DRY-RUN] Fila {idx+2}: Actualizar datos de Medico (ID={medico.id}), "
                    #     f"User={medico.user.username if medico.user else '(sin user)'}"
                    # )
                    num_actualizados += 1

                # Actualizar User
                # Nombre => user.first_name, Apellidos => user.last_name
                # Por ejemplo, conjugar "Nombre" + "A. Paterno" + "A. Materno"
                if isinstance(nombre_val, str):
                    nombre_val = nombre_val.strip()
                else:
                    nombre_val = ""
                # Combinar apellidos
                apellidos = (a_paterno_val or "") + " " + (a_materno_val or "")
                user_obj.first_name = nombre_val
                user_obj.last_name = apellidos.strip()

                if email_val and pd.notna(email_val):
                    user_obj.email = str(email_val).strip()
                user_obj.save()

                # # Actualizar Medico
                updated_medico = False
                if icm_int:
                    if medico.icm != icm_int:
                        medico.icm = icm_int
                        updated_medico = True
                if celular_val and pd.notna(celular_val):
                    if medico.contacto != celular_val:
                        medico.contacto = celular_val
                        updated_medico = True
                if direccion_val and pd.notna(direccion_val):
                    if medico.direccion != direccion_val:
                        medico.direccion = direccion_val
                        updated_medico = True
                if comuna_val and pd.notna(comuna_val):
                    if medico.comuna != comuna_val:
                        medico.comuna = comuna_val
                        updated_medico = True
                if condicion_vital_val and pd.notna(condicion_vital_val):
                    if medico.condicion_vital != condicion_vital_val:
                        medico.condicion_vital = condicion_vital_val
                        updated_medico = True

                # # Fechas
                fecha_nac = self.parse_fecha(fecha_nac_str)
                if fecha_nac and medico.fecha_nacimiento != fecha_nac:
                    medico.fecha_nacimiento = fecha_nac
                    updated_medico = True
                fecha_titulo = self.parse_fecha(fecha_titulo_str)
                if fecha_titulo and medico.fecha_titulo != fecha_titulo:
                    medico.fecha_titulo = fecha_titulo
                    updated_medico = True

                if updated_medico:
                    medico.save()

                if creado:
                    num_creados += 1
                else:
                    num_actualizados += 1
                self.procesar_afiliaciones(medico, row)
                # pass
                campos_cambiados = []
                campos_cambiados.append(f"nombre_user='{nombre_val}'")
                campos_cambiados.append(f"apellidos_user='{a_paterno_val} {a_materno_val}'")
                campos_cambiados.append(f"email_user='{email_val}'")
                campos_cambiados.append(f"contacto='{celular_val}'")
                campos_cambiados.append(f"direccion='{direccion_val}'")
                campos_cambiados.append(f"comuna='{comuna_val}'")
                campos_cambiados.append(f"condicion_vital='{condicion_vital_val}'")

                fecha_nac = self.parse_fecha(fecha_nac_str)
                fecha_titulo = self.parse_fecha(fecha_titulo_str)
                if fecha_nac:
                    campos_cambiados.append(f"fecha_nacimiento={fecha_nac}")
                if fecha_titulo:
                    campos_cambiados.append(f"fecha_titulo={fecha_titulo}")

                # self.stdout.write(f"    Se modificarían estos campos: {', '.join(campos_cambiados)}")
            except Exception as ex:

                num_errores += 1
                errores.append(f"Fila {idx+2}: {ex}")

        # 6) Generar archivo de estadísticas
        now = datetime.datetime.now()
        stats_filename = f"estadisticas_{now.strftime('%d_%m_%Y')}.txt"
        stats_path = os.path.join(local_tmp_dir, stats_filename)
        

        with open(stats_path, "w", encoding="utf-8") as f:
            f.write(f"Fecha proceso: {now}\n")
            f.write(f"Total filas procesadas: {total_filas}\n")
            f.write(f"Creados: {num_creados}\n")
            f.write(f"Actualizados: {num_actualizados}\n")
            f.write(f"Errores: {num_errores}\n\n")
            if errores:
                f.write("-- Detalle de errores --\n")
                for e in errores:
                    f.write(str(e) + "\n")

        self.stdout.write(self.style.SUCCESS(
            f"Importación finalizada. Filas={total_filas}, "
            f"Creados={num_creados}, Actualizados={num_actualizados}, "
            f"Errores={num_errores}. Stats: {stats_path}"
        ))

        # self.eliminar_usuarios_duplicados()
        self.subir_archivo_a_drive(
            drive_service=drive_service,
            local_path=stats_path,
            drive_parent_id=drive_dir,    # el ID de la carpeta
            nombre_en_drive=stats_filename
        )
        # 7) Eliminar XLSX local
        self._eliminar_archivo(local_xlsx_path)
        self._eliminar_archivo(stats_path)
        

    def obtener_nombre_usuario(self, row):
        """
        Construye el nombre de usuario evitando valores nulos o vacíos.
        """
        nombre = str(row.get("Nombre", "")).strip() if pd.notna(row.get("Nombre")) else ""
        a_paterno = str(row.get("A. Paterno", "")).strip() if pd.notna(row.get("A. Paterno")) else ""
        a_materno = str(row.get("A. Materno", "")).strip() if pd.notna(row.get("A. Materno")) else ""

        # Filtrar valores vacíos para evitar "_None_" o "__"
        partes_nombre = [parte for parte in [nombre, a_paterno, a_materno] if parte]

        if partes_nombre:
            return "_".join(partes_nombre)
        else:
            return "usuario_desconocido"

    def eliminar_usuarios_duplicados(self):
        """
        Elimina usuarios con perfil 'visitante' que no están relacionados con un médico.
        """
        
        # Filtrar usuarios con perfil 'visitante'
        usuarios_sin_perfil = User.objects.annotate(num_perfiles=Count('perfiles')).filter(num_perfiles=0)
        
        if not usuarios_sin_perfil.exists():            
            return


        # Eliminar usuarios identificados
        usuarios_sin_perfil.delete()
        


    def subir_archivo_a_drive(self, drive_service, local_path, drive_parent_id, nombre_en_drive):
        """
        Sube un archivo local (local_path) a Google Drive,
        en la carpeta con ID = drive_parent_id, con nombre = nombre_en_drive.
        """
        

        file_metadata = {
            "name": nombre_en_drive,
            "parents": [drive_parent_id],
        }
        media = MediaFileUpload(local_path, mimetype="text/plain")  # Ajustar MIME si quieres
        archivo_subido = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        self.stdout.write(self.style.SUCCESS(
            f"Archivo de estadísticas subido a Drive con ID={archivo_subido.get('id')}"
        ))

    def parse_icm(self, icm_val):
        """Convierte un valor (str/float) en un int (ICM). Devuelve None si no es posible."""
        if not icm_val:
            return None
        try:
            return int(icm_val)
        except ValueError:
            return None
        
    def limpiar_rut(self, rut_str):
        """
        Rut viene con DV, por ej "12345678-9". 
        Queremos quedarnos con la parte antes del '-'.
        """
        if not rut_str or pd.isna(rut_str):
            return None
        rut_str = rut_str.replace('.', '').replace(' ', '').upper()
        if '-' in rut_str:
            # ej: "12345678-9"
            parts = rut_str.split('-')
            return parts[0]  # "12345678"
        return rut_str

    def parse_fecha(self, fecha_str):
        """
        Convierte strings como "01-01-1900  0:00:00" o "01-01-1970" 
        en un objeto date, si es válido.
        """
        try:
            # Si ya es un datetime, simplemente extraer la fecha
            if isinstance(fecha_str, (datetime.datetime, datetime.date)):
                return fecha_str.date()

            # Intentar convertir a datetime usando pandas
            fecha = pd.to_datetime(str(fecha_str), errors='coerce')

            # Verificar si la conversión fue exitosa
            if pd.notnull(fecha) and fecha.date() != datetime.date(1900, 1, 1):
                return fecha.date()
        except Exception as e:
            print(f"[ERROR] No se pudo convertir la fecha: {fecha_str} - Error: {e}")

        return None


    # (Opcional) Ejemplo de procesar afiliaciones
    def procesar_afiliaciones(self, medico, row):
        """
        Ejemplo de cómo manejar la lógica de 'Estado Pago Col', 'Año ucp Col', etc.
        Requiere adaptarse a tus columnas reales.
        """

        def obtener_valor_estado_pago(valor_excel):
            valor_excel = valor_excel.strip().upper()
            estado_pago_choices = Afiliacion._meta.get_field('estado_pago').choices
            for key, display in estado_pago_choices:
                if display.upper() == valor_excel:
                    return key
            return None  

        
        afiliaciones_info = [
            {
                'entidad_sigla': 'COLMED',
                'codigo_socio_col': 'C. Socio Col',
                'estado_pago_col': 'Estado Pago Col',
                'anio_ucp_col': 'Año ucp Col',
                'mes_ucp_col': 'Mes ucp Col',
                'estamento_col': 'Estamento Col',
                'cod_estamento_col': 'codEstamentoCol',
                'num_cuota_col': 'NumCuotaCol',
                'lugar_descuento_col': 'Lugar Descuento Col',
                'tipo_cuota': 'F. Cuota Col',
                'fecha_inscripcion_col': 'F. inscripcion Col',
            },
            {
                'entidad_sigla': 'FSG',
                'codigo_socio_col': 'C. Socio FSG',
                'estado_pago_col': 'Estado Pago FSG',
                'anio_ucp_col': 'Año ucp FSG',
                'mes_ucp_col': 'Mes ucp FSG',
                'estamento_col': 'Estamento FSG',
                'cod_estamento_col': 'codEstamentoFSG',
                'num_cuota_col': 'NumCuotaFsg',
                'lugar_descuento_col': 'Lugar Descuento FSG',
                'tipo_cuota': 'F. Cuota FSG',
                'fecha_inscripcion_col': 'F. inscripcion FSG',
            },
            {
                'entidad_sigla': 'FALMED',
                'codigo_socio_col': 'C. Socio Falmed',
                'estado_pago_col': 'Estado Pago Falmed',
                'anio_ucp_col': 'Año ucp Falmed',
                'mes_ucp_col': 'Mes ucp Falmed',
                'estamento_col': 'Estamento Falmed',
                'cod_estamento_col': 'codEstamentoFalmed',
                'num_cuota_col': 'NumCuotaFalmed',
                'lugar_descuento_col': 'Lugar Descuento Falmed',
                'tipo_cuota': 'F. Cuota Falmed',
                'fecha_inscripcion_col': 'F. inscripcion Falmed',
            },
            {
                'entidad_sigla': 'CLUB CAMPO',
                'codigo_socio_col': 'C. Socio Club',
                'estado_pago_col': 'Estado Pago Club',
                'anio_ucp_col': 'Año ucp Club',
                'mes_ucp_col': 'Mes ucp Club',
                'estamento_col': 'Estamento Club',
                'cod_estamento_col': 'codEstamentoClub',
                'num_cuota_col': 'NumCuotaClub',
                'lugar_descuento_col': 'Lugar Descuento Club',
                'tipo_cuota': 'F. Cuota Club',
                'fecha_inscripcion_col': 'F. inscripcion Club',
            },
            {
                'entidad_sigla': 'FATMED',
                'codigo_socio_col': 'C. Socio Fatmed',
                'estado_pago_col': 'Estado Pago Fatmed',
                'anio_ucp_col': 'Año ucp Fatmed',
                'mes_ucp_col': 'Mes ucp Fatmed',
                'estamento_col': 'Estamento Fatmed',
                'cod_estamento_col': 'codEstamentoFatmed',
                'num_cuota_col': 'NumCuotaFatmed',
                'lugar_descuento_col': 'Lugar Descuento Fatmed',
                'tipo_cuota': 'F. Cuota Fatmed',
                'fecha_inscripcion_col': 'F. inscripcion Fatmed',
            },
        ]

        for afi_data in afiliaciones_info:
            sigla = afi_data['entidad_sigla']
            entidad = Entidad.objects.filter(sigla=sigla).first()

            # Obtener valores del archivo
            #estado_pago = obtener_valor_estado_pago(row.get(afi_data['estado_pago_col'], ''))
            estado_pago = obtener_valor_estado_pago(str(row.get(afi_data['estado_pago_col'], "")).strip() if pd.notna(row.get(afi_data['estado_pago_col'], '')) else "")
            #anio_ucp = row.get(afi_data['anio_ucp_col'])
            anio_ucp = str(row.get(afi_data['anio_ucp_col'], ""))
            #mes_ucp = row.get(afi_data['mes_ucp_col'])
            mes_ucp = str(row.get(afi_data['mes_ucp_col'], ""))
            #estamento_nombre = row.get(afi_data['estamento_col'])
            estamento_nombre = str(row.get(afi_data['estamento_col'], ""))
            #cod_estamento = row.get(afi_data['cod_estamento_col'])
            cod_estamento = str(row.get(afi_data['cod_estamento_col'], ""))
            #num_ultima_cuota = row.get(afi_data['num_cuota_col'])
            num_ultima_cuota = str(row.get(afi_data['num_cuota_col'], ""))
            #lugar_descuento_nombre = row.get(afi_data['lugar_descuento_col'])
            lugar_descuento_nombre = str(row.get(afi_data['lugar_descuento_col'], ""))
            #tipo_cuota = row.get(afi_data['tipo_cuota'])
            tipo_cuota = str(row.get(afi_data['tipo_cuota'], ""))
            #condicion_afiliado = row.get(afi_data['codigo_socio_col'])
            condicion_afiliado = str(row.get(afi_data['codigo_socio_col'], ""))

            fecha_inscripcion = self.parse_fecha(row.get(afi_data['fecha_inscripcion_col']))

            # No crear afiliación si no hay fecha de inscripción o entidad
            if not fecha_inscripcion or not entidad:
                continue

            afiliacion, created = Afiliacion.objects.get_or_create(
                medico=medico,
                entidad=entidad,
                defaults={'fecha_inscripcion': fecha_inscripcion}
            )

            updated = False
            if not created:
                if afiliacion.fecha_inscripcion != fecha_inscripcion:
                    afiliacion.fecha_inscripcion = fecha_inscripcion
                    updated = True

            if estado_pago:
                afiliacion.estado_pago = estado_pago
                updated = True

            if condicion_afiliado:
                afiliacion.condicion_afiliado = condicion_afiliado
                updated = True

            if anio_ucp and pd.notna(anio_ucp):
                afiliacion.anio_ucp = int(anio_ucp)
                updated = True

            if mes_ucp and pd.notna(mes_ucp):
                afiliacion.mes_ucp = int(mes_ucp)
                updated = True

            if estamento_nombre and pd.notna(estamento_nombre):
                estamento, _ = Estamento.objects.get_or_create(
                    nombre_estamento=estamento_nombre.strip(),
                    defaults={'codigo_estamento': cod_estamento}
                )
                afiliacion.estamento = estamento
                updated = True

            if num_ultima_cuota and pd.notna(num_ultima_cuota):
                afiliacion.num_ultima_cuota = int(num_ultima_cuota)
                updated = True

            if lugar_descuento_nombre and pd.notna(lugar_descuento_nombre):
                lugar_descuento, _ = LugarDescuento.objects.get_or_create(
                    nombre_lugar=lugar_descuento_nombre.strip()
                )
                afiliacion.lugar_descuento = lugar_descuento
                updated = True

            if tipo_cuota and pd.notna(tipo_cuota):
                afiliacion.tipo_cuota = tipo_cuota
                updated = True

            if updated:
                afiliacion.save()




    def descargar_archivo(self, drive_service, file_id, local_path):
        """
        Descarga un archivo de Google Drive (XLSX) a local_path
        """
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()

    def _eliminar_archivo(self, path):
        """
        Borra el archivo local si existe
        """
        try:
            if os.path.isfile(path):
                os.remove(path)
                self.stdout.write(self.style.WARNING(f"Archivo temporal eliminado: {path}"))
        except Exception as e:
            self.stderr.write(f"No se pudo eliminar {path}: {e}")