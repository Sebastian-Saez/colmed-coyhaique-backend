from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Medico, Cuota, Afiliacion, TIPOS_ESTADO_PAGO, TIPOS_DIRECTIVA, Especialidad,Institucion,RegistroSuperintendencia, OrdenProfesional
from .serializers import MedicoSerializer, CuotaSerializer, AfiliacionSerializer, InstitucionSerializer, EspecialidadSerializer, RegistroSuperintendenciaSerializer, OrdenProfesionalSerializer
from django.db.models import Q
from django.db.models.functions import Lower
from .utils import convertir_fecha
import re
import os
import tempfile
import string
from pathlib import Path
import pdfplumber
from django.http import JsonResponse
from datetime import datetime
#from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from backend_colmed.settings import GOOGLE_DRIVE_SUPER, GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_DRIVE_SR

GOOGLE_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer

    @action(detail=False, methods=['get'], url_path='directiva')
    def obtener_directiva(self, request):
        """
        Endpoint para obtener la lista de médicos que son parte de la directiva.
        Los resultados están ordenados en el siguiente orden: 
        Presidente, Vicepresidente, Secretario, Tesorero, Consejero.
        """
        # Definir el orden de la directiva según los choices definidos en el modelo (omitimos el valor vacío)
        orden_directiva = [directiva[0] for directiva in TIPOS_DIRECTIVA if directiva[0] != '']
        
        # Crear una lista vacía para almacenar los médicos en el orden de la jerarquía
        medicos_directiva_list = []

        # Construir la lista de médicos en el orden especificado
        for cargo in orden_directiva:
            medicos_cargo = Medico.objects.filter(directiva=cargo).order_by('user__first_name')
            medicos_directiva_list.extend(medicos_cargo)

        # Serializar los resultados
        serializer = self.get_serializer(medicos_directiva_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='filtro_data_medicos')
    def filtro_data_medicos(self, request):
        # """
        # Endpoint para filtrar médicos por fechas de nacimiento o titulación.
        # Devuelve todos los médicos si no se proporciona ningún filtro.
        # Acepta fechas en formato dd-mm-aaaa y las convierte a aaaa-mm-dd.
        # """
        # # Obtener y convertir filtros desde el cuerpo de la solicitud (POST)
        # fecha_nacimiento_inicio = convertir_fecha(request.data.get('fecha_nacimiento_inicio'))
        # fecha_nacimiento_fin = convertir_fecha(request.data.get('fecha_nacimiento_fin'))
        # fecha_titulo_inicio = convertir_fecha(request.data.get('fecha_titulo_inicio'))
        # fecha_titulo_fin = convertir_fecha(request.data.get('fecha_titulo_fin'))
        # fecha_inscripcion_inicio = convertir_fecha(request.data.get('fecha_inscripcion_inicio'))
        # fecha_inscripcion_fin = convertir_fecha(request.data.get('fecha_inscripcion_fin'))

        #  # Obtener los filtros de afiliaciones y estados de pago
        # afiliaciones = request.data.get('afiliaciones', [])
        # estados_pago = request.data.get('estados_pago', [])
        
        # # Construcción de filtros dinámicos
        # filters = Q()
        # aplicar_distinct = False

        # # Filtrar por rango de fecha de nacimiento, si está especificado
        # if fecha_nacimiento_inicio or fecha_nacimiento_fin:
        #     if fecha_nacimiento_inicio:
        #         filters &= Q(fecha_nacimiento__gte=fecha_nacimiento_inicio)
        #     if fecha_nacimiento_fin:
        #         filters &= Q(fecha_nacimiento__lte=fecha_nacimiento_fin)
        
        # # Filtrar por rango de fecha de titulación, si está especificado
        # if fecha_titulo_inicio or fecha_titulo_fin:
        #     if fecha_titulo_inicio:
        #         filters &= Q(fecha_titulo__gte=fecha_titulo_inicio)
        #     if fecha_titulo_fin:
        #         filters &= Q(fecha_titulo__lte=fecha_titulo_fin)

        # # -- Fechas de inscripción (implica que el médico tiene afiliación colmed)
        # if fecha_inscripcion_inicio or fecha_inscripcion_fin:
        #     # Forzamos médicos con afiliación no nula
        #     filters &= Q(afiliacion__isnull=False)
        #     aplicar_distinct = True

        #     if fecha_inscripcion_inicio:
        #         filters &= Q(afiliacion__fecha_inscripcion__gte=fecha_inscripcion_inicio)
        #     if fecha_inscripcion_fin:
        #         filters &= Q(afiliacion__fecha_inscripcion__lte=fecha_inscripcion_fin)


        # tipos_estado_pago_keys = [estado[0] for estado in TIPOS_ESTADO_PAGO]
        # estados_validos = [estado for estado in estados_pago if estado in tipos_estado_pago_keys]

        # if estados_validos:
        #     print("ingreso estados_pago")
        #     # Filtrar en la misma sentencia la entidad = "COLMED" + estado_pago
        #     # => Implica forzar afiliacion != null
        #     filters &= Q(
        #         afiliacion__entidad__sigla="COLMED",
        #         afiliacion__estado_pago__in=estados_validos
        #     )
        #     aplicar_distinct = True

        # # 4. Filtro por afiliaciones
        # #    - "colmed" => medico con afiliacion, sin importar el estado, si no se mando 'estados'
        # #    - "no_colegiado" => medico afiliacion null
        # #    - si llega ambos => traer todos en cuanto a afiliacion
        # #    PERO si ya filtramos por 'estados', prevalece la afiliacion colmed.
        # contiene_colmed = "colmed" in afiliaciones
        # contiene_no_colegiado = "no_colegiado" in afiliaciones

        # # -- Caso si no hay 'estados_validos', podemos filtrar con la logica usual
        # if not estados_validos:
        #     print("Ingreo a not estados_pago")
        #     if contiene_colmed and not contiene_no_colegiado:
        #         # medico con afiliacion != null (puede ser colmed u otra)
        #         # si deseas forzar que sea EXACTO la entidad colmed => Q(afiliacion__entidad__sigla="COLMED")
        #         filters &= Q(afiliacion__isnull=False)
        #         aplicar_distinct = True
        #     elif contiene_no_colegiado and not contiene_colmed:
        #         # medico sin afiliacion
        #         filters &= Q(afiliacion__isnull=True)
        #     elif contiene_colmed and contiene_no_colegiado:
        #         # si hay ambos => no filtrar por afiliacion
        #         pass
        #     else:
        #         # afiliaciones vacio => no filtras por afiliacion
        #         pass
        # else:
        #     # ya se filtró por "colmed" y "estado_pago", no haria falta mas logica de no_colegiado
        #     # sin embargo, si la lista tambien dice "no_colegiado", eso es contradictorio con 'states'
        #     # se ignora => focalizado en colmed con 'states'
        #     pass

        # # contiene_colmed = "colmed" in afiliaciones
        # # contiene_no_colegiado = "no_colegiado" in afiliaciones

        # # if contiene_colmed and not contiene_no_colegiado:
        # #     # Solo 'colmed' => filtrar con afiliacion
        # #     filters &= Q(afiliacion__isnull=False)
        # #     aplicar_distinct = True
        # # elif contiene_no_colegiado and not contiene_colmed:
        # #     # Solo 'no_colegiado' => filtrar sin afiliacion
        # #     filters &= Q(afiliacion__isnull=True)
        # # elif contiene_colmed and contiene_no_colegiado:
        # #     # Si hay ambos => traer todos en cuanto a afiliacion (no se filtra nada aquí)
        # #     pass

        # # # Filtros por estados de pago, solo con estados válidos
        # # tipos_estado_pago_keys = [estado[0] for estado in TIPOS_ESTADO_PAGO]
        # # estados_validos = [estado for estado in estados_pago if estado in tipos_estado_pago_keys]
        # # if estados_validos:
        # #     filters &= Q(afiliacion__estado_pago__in=estados_validos)
            
        # # Si no se proporciona ningún filtro, devuelve todos los médicos
        # if filters:
        #     print("ingresa aca")
        #     medicos_filtrados = Medico.objects.filter(filters)
        #     if aplicar_distinct:
        #         print("ingresa aca2")
        #         medicos_filtrados = medicos_filtrados.distinct()
        # else:
        #     print("ingresa aca22")
        #     medicos_filtrados = Medico.objects.all()

        # serializer = self.get_serializer(medicos_filtrados, many=True)

        # print(" TOTAL DE REGISTRS",len(medicos_filtrados))
        # return Response(serializer.data)
        """
        Endpoint para filtrar médicos por:
          - Rango de fecha de nacimiento (fecha_nacimiento_inicio/fin)
          - Rango de fecha de titulación (fecha_titulo_inicio/fin)
          - Rango de fecha de inscripción (fecha_inscripcion_inicio/fin)
            *Sólo aplica a la afiliación COLMED*
          - Afiliaciones -> array con "colmed", "no_colegiado" o ambos (o vacío)
          - Estados de pago -> array con valores como "moroso", "al_dia", etc. (o vacío)
    
        Si 'afiliaciones' está vacío => se interpretan todos (colmed y no_colegiado).
        Si 'estados_pago' está vacío => no filtra por estado.
        La unión de 'colmed' + 'estados_pago' se interpreta como "colmed con esos estados".
        Si a la vez se pide 'no_colegiado', se une con OR a "afiliacion__isnull=True".
        """

        # --- 1) Convertir Fechas desde la solicitud ---
        fecha_nacimiento_inicio = convertir_fecha(request.data.get('fecha_nacimiento_inicio'))
        fecha_nacimiento_fin   = convertir_fecha(request.data.get('fecha_nacimiento_fin'))
        fecha_titulo_inicio    = convertir_fecha(request.data.get('fecha_titulo_inicio'))
        fecha_titulo_fin       = convertir_fecha(request.data.get('fecha_titulo_fin'))
        fecha_inscripcion_inicio = convertir_fecha(request.data.get('fecha_inscripcion_inicio'))
        fecha_inscripcion_fin    = convertir_fecha(request.data.get('fecha_inscripcion_fin'))

        # --- 2) Leer afiliaciones y estados ---
        afiliaciones = request.data.get('afiliaciones', [])
        estados_pago = request.data.get('estados_pago', [])

        # Convertir a lista si vienen strings sueltos
        if isinstance(afiliaciones, str):
            afiliaciones = [afiliaciones]
        if isinstance(estados_pago, str):
            estados_pago = [estados_pago]

        # Filtrar estados de pago válidos
        tipos_estado_pago_keys = [estado[0] for estado in TIPOS_ESTADO_PAGO]
        estados_validos = [e for e in estados_pago if e in tipos_estado_pago_keys]

        # --- 3) Construir Q principal ---
        filters = Q()
        aplicar_distinct = False

        # --- 3.1) Filtro por Fechas de nacimiento ---
        if fecha_nacimiento_inicio:
            filters &= Q(fecha_nacimiento__gte=fecha_nacimiento_inicio)
        if fecha_nacimiento_fin:
            filters &= Q(fecha_nacimiento__lte=fecha_nacimiento_fin)

        # --- 3.2) Filtro por Fechas de título ---
        if fecha_titulo_inicio:
            filters &= Q(fecha_titulo__gte=fecha_titulo_inicio)
        if fecha_titulo_fin:
            filters &= Q(fecha_titulo__lte=fecha_titulo_fin)

        # --- 3.3) Filtro por Fechas de inscripción (únicamente para COLMED) ---
        # Si se pide filtrar por fecha_inscripcion, forzamos que exista afiliacion COLMED
        if fecha_inscripcion_inicio or fecha_inscripcion_fin:
            aplicar_distinct = True
            colmed_inscrip_filter = Q(afiliacion__entidad__sigla="COLMED")
            if fecha_inscripcion_inicio:
                colmed_inscrip_filter &= Q(afiliacion__fecha_inscripcion__gte=fecha_inscripcion_inicio)
            if fecha_inscripcion_fin:
                colmed_inscrip_filter &= Q(afiliacion__fecha_inscripcion__lte=fecha_inscripcion_fin)

            filters &= colmed_inscrip_filter

        # --- 4) Filtro por estados de pago (sólo aplica a COLMED) ---
        # Si hay estados_validos => se filtra a medicos con afiliacion COLMED + estado in [estados_validos]
        filtro_colmed_estado = Q()
        if estados_validos:
            filtro_colmed_estado = Q(
                afiliacion__entidad__sigla="COLMED",
                afiliacion__estado_pago__in=estados_validos
            )
            aplicar_distinct = True

        # --- 5) Filtro por afiliaciones ---
        #   - colmed => afiliacion__entidad__sigla="COLMED"
        #   - no_colegiado => afiliacion__isnull=True
        #   - vacío => "colmed + no_colegiado" => no filtrar (o sea, traer todos),
        #       pero si hay 'estados_validos', se combina en un OR con no_colegiado.

        contiene_colmed = "colmed" in afiliaciones
        contiene_no_colegiado = "no_colegiado" in afiliaciones
        # Si está vacío, es equivalente a "colmed + no_colegiado"
        # de modo que no filtraríamos nada adicional, *salvo* si además llegaron estados_validos
        # (en cuyo caso, queremos la unión: colmed con dichos estados + no_colegiado).
        lista_vacia_afiliaciones = (len(afiliaciones) == 0)

        # Construimos un Q para la parte "colmed"
        filtro_only_colmed = Q(afiliacion__entidad__sigla="COLMED")
        # Construimos un Q para la parte "no_colegiado"
        filtro_only_no_colegiado = Q(afiliacion__isnull=True)

        if contiene_colmed and not contiene_no_colegiado:
            # Solo colmed
            if estados_validos:
                # colmed con esos estados
                filters &= filtro_colmed_estado
            else:
                # colmed sin restricción de estado
                filters &= filtro_only_colmed
            aplicar_distinct = True

        elif contiene_no_colegiado and not contiene_colmed:
            # Solo no_colegiado
            # Si hay estados_validos, es una contradicción => no_colegiado no tiene estados
            # => filtrar Q(afiliacion__isnull=True) (puede terminar en 0 si piden un state)
            filters &= filtro_only_no_colegiado

        elif contiene_colmed and contiene_no_colegiado:
            # colmed + no_colegiado => union
            # Si hay estados_validos => union (colmed con esos estados) OR (no_colegiado)
            # Si no hay estados_validos => union (colmed) OR (no_colegiado) => "todos"
            if estados_validos:
                or_filters = filtro_colmed_estado | filtro_only_no_colegiado
                filters &= or_filters
            else:
                or_filters = filtro_only_colmed | filtro_only_no_colegiado
                filters &= or_filters
            aplicar_distinct = True

        else:
            # afiliaciones está vacío => "colmed + no_colegiado" => todos
            # si además hay estados_validos => se hace union colmed con esos estados OR no_colegiado
            if estados_validos:
                # OR => (colmed con esos estados) | no_colegiado
                or_filters = filtro_colmed_estado | filtro_only_no_colegiado
                filters &= or_filters
                aplicar_distinct = True
            else:
                # sin estados => no filtra nada por afiliaciones => se deja tal cual
                pass

        # --- 6) Aplicar Filtros y retornar ---
        qs = Medico.objects.filter(filters)
        if aplicar_distinct:
            qs = qs.distinct()

        serializer = self.get_serializer(qs, many=True)
        
        return Response(serializer.data)
    
    
    #Todos los médicos con alguna afiliación
    @action(detail=False, methods=['get'])
    def con_afiliacion(self, request):
        medicos_con_afiliacion = Medico.objects.filter(afiliacion__isnull=False).distinct()
        serializer = self.get_serializer(medicos_con_afiliacion, many=True)
        return Response(serializer.data)
    
    #Todos los médicos sin afiliación
    @action(detail=False, methods=['get'])
    def sin_afiliacion(self, request):
        medicos_sin_afiliacion = Medico.objects.filter(afiliacion__isnull=True)
        serializer = self.get_serializer(medicos_sin_afiliacion, many=True)
        return Response(serializer.data)

    #Las afiliaciones de un médico en específico
    @action(detail=False, methods=['get'])
    def afiliaciones(self, request, pk=None):
        medico = request.query_params.get('medico')
        afiliaciones = Afiliacion.objects.filter(medico=medico)
        serializer = AfiliacionSerializer(afiliaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_afiliacion(self, request):
        entidades = request.query_params.getlist('entidad')
        if not entidades:
            return Response({"detail": "Debe proporcionar al menos una entidad en los parámetros de consulta."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar médicos que tienen afiliaciones con las entidades especificadas
        medicos_filtrados = Medico.objects.filter(
            afiliacion__entidad__sigla__in=entidades
        ).distinct()
        
        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def medico_app(self, request, pk=None):
        usuario = request.query_params.get('usuario')
        
        medico = Medico.objects.get(user__id=usuario)
        
        
        serializer = self.get_serializer(medico)
        return Response(serializer.data)    
    

    @action(detail=False, methods=['post'], url_path='por_afiliacion')
    def por_afiliacion(self, request):
        """
        Endpoint para filtrar médicos por Afiliación.
        Si no se proporciona ninguna afiliación, devuelve todos los médicos.
        """
        afiliaciones = request.data.get('afiliaciones', [])

        if not afiliaciones:
            medicos_filtrados = Medico.objects.all()
        else:
            medicos_filtrados = Medico.objects.filter(afiliacion__isnull=False).distinct()

        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='por_estados_pago')
    def por_estados_pago(self, request):
        """
        Endpoint para filtrar médicos por estados de pago.
        Si no se proporciona ningún estado de pago, devuelve todos los médicos.
        """
        # Obtener lista de estados desde el cuerpo de la solicitud
        estados = request.data.get('estados', [])
        tipos_estado_pago_keys = [estado[0] for estado in TIPOS_ESTADO_PAGO]
        # Validar los estados de pago y filtrar solo los válidos
        estados_validos = [estado for estado in estados if estado in tipos_estado_pago_keys]
        
        
        # Si no se proporciona ningún estado válido, devolver todos los médicos
        if not estados_validos:
            medicos_filtrados = Medico.objects.all()
        else:
            # Filtrar médicos por los estados válidos
            medicos_filtrados = Medico.objects.filter(
                afiliacion__estado_pago__in=estados_validos
            ).distinct()
        
        serializer = self.get_serializer(medicos_filtrados, many=True)
        return Response(serializer.data)

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    serializer_class = CuotaSerializer

#Registro Superintendencia
class InstitucionViewSet(viewsets.ModelViewSet):
    queryset = Institucion.objects.all()
    serializer_class = InstitucionSerializer

    @action(detail=False, methods=['get'])
    def instituciones_certificadoras(self, request, pk=None):
        instituciones = (Institucion.objects.annotate(nombre_lower=Lower('nombre')).values('nombre_lower','fecha_modificacion').distinct())
        data_transformada = []
        for inst in instituciones:
            data_transformada.append({
                'nombre': string.capwords(inst['nombre_lower']),
                'fecha_modificacion': inst['fecha_modificacion']
            })
        return Response(data_transformada)

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer

class OrdenProfesionalViewSet(viewsets.ModelViewSet):
    queryset = OrdenProfesional.objects.all()
    serializer_class = OrdenProfesionalSerializer
    
class RegistroSuperintendenciaViewSet(viewsets.ModelViewSet):
    queryset = RegistroSuperintendencia.objects.all()
    serializer_class = RegistroSuperintendenciaSerializer

    @action(detail=False, methods=['get'])
    def certificado_medico(self, request, pk=None):
        id_registro_medico = request.query_params.get('registro')        
        certificado_superintendencia = RegistroSuperintendencia.objects.get(id=id_registro_medico)
        serializer = RegistroSuperintendenciaSerializer(certificado_superintendencia)
        return Response(serializer.data)

class ProcesarRegistrosSR(APIView):
    def post(self, request):
        
        if request.method != "POST" or "file" not in request.FILES:
            return JsonResponse({"error": "No se envió un archivo válido"}, status=400)
        
        file = request.FILES["file"]
        
        

        # Validar la extensión del archivo
        if not (file.name.endswith(".xlsx") or file.name.endswith(".xls")):
            return JsonResponse({"error": "Formato de archivo no soportado. Debe ser .xlsx o .xls"}, status=400)


    
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            drive_service = GoogleDriveService()
            file_id = drive_service.upload_excel_file(temp_file_path, file.name, GOOGLE_DRIVE_SR)

            # Eliminar el archivo temporal después de la subida
            os.remove(temp_file_path)


                        
            return JsonResponse({"message": "Archivo subido con éxito", "file_id": file_id})

        except Exception as e:
            return Response(
                {"detail": f"Error al procesar archivos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Solicitud de registros Superintendencia
class ProcesarRegistrosSuperintendenciaAPIView(APIView):
    """
    Endpoint para procesar registros desde archivos PDF ubicados en una carpeta específica.
    """
    def convertir_fecha(self, fecha_str):
        """
        Convierte una fecha en formato DD/MM/YYYY a YYYY-MM-DD.
        Si la conversión falla, devuelve None.
        """
        try:
            return datetime.strptime(fecha_str, "%d/%m/%Y").date()
        except ValueError:
            return None

    def procesar_archivo(self, archivo):
        """
        Procesa un archivo PDF y devuelve un diccionario con los resultados del procesamiento.
        """
        resultados = {"archivo": archivo.name, "estatus": "exitoso", "alertas": []}
        try:
            texto = self.extraer_texto_pdf(archivo)
            if not texto:
                resultados["estatus"] = "fallido"
                resultados["alertas"].append(f"No se pudo extraer texto del archivo: {archivo.name}")
                return resultados

            datos = self.extraer_datos(texto)
            if not datos:
                resultados["estatus"] = "fallido"
                resultados["alertas"].append(f"No se pudieron extraer datos del archivo: {archivo.name}")
                return resultados

            medico = Medico.objects.filter(rut=datos['rut']).first()
            if not medico:
                resultados["estatus"] = "fallido"
                resultados["alertas"].append(f"RUT no encontrado: {datos['rut']}")
                return resultados

            # Convertir fechas
            fecha_registro = self.convertir_fecha(datos['fecha_registro'])
            fecha_nacimiento = self.convertir_fecha(datos['fecha_nacimiento'])

            if not fecha_registro or not fecha_nacimiento:
                resultados["estatus"] = "fallido"
                resultados["alertas"].append(f"Fechas inválidas para el RUT: {datos['rut']}")
                return resultados

            # Procesar RegistroSuperintendencia
            registro, created = RegistroSuperintendencia.objects.update_or_create(
                numero_registro=datos['numero_registro'],
                defaults={
                    'fecha_registro': fecha_registro,
                    'fecha_nacimiento': fecha_nacimiento,
                    'nacionalidad': datos['nacionalidad'],
                }
            )

            # Procesar Órdenes Profesionales
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

            # Procesar Especialidades
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

            # Asociar RegistroSuperintendencia al Médico
            medico.registro_superintendencia = registro
            medico.save()

        except Exception as e:
            resultados["estatus"] = "fallido"
            resultados["alertas"].append(f"Error inesperado: {str(e)}")

        return resultados

    def extraer_texto_pdf(self, archivo):
        texto = ""
        with pdfplumber.open(archivo) as pdf:
            for page in pdf.pages:
                texto += page.extract_text()
        return texto

    def extraer_datos(self, texto):
        """
        Extrae los datos clave del texto del PDF.
        """
        try:
            rut = re.search(r'RUN:\s*([\d\.\-]+)', texto).group(1)
            nacionalidad = re.search(r'Nacionalidad:\s*([^\n]+)', texto).group(1)
            numero_registro = re.search(r'figura, bajo el N° (\d+)', texto).group(1)
            fecha_registro = re.search(r'Fecha de registro:\s*(\d{2}/\d{2}/\d{4})', texto).group(1)
            fecha_nacimiento = re.search(r'Fecha nacimiento:\s*(\d{2}/\d{2}/\d{4})', texto).group(1)
            titulos_profesionales = []  # Implementar si es necesario
            especialidades = []  # Implementar si es necesario
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
            return None

    def post(self, request):
        """
        Procesa los archivos PDF descargados desde Google Drive.
        """
        
        folder_id = GOOGLE_DRIVE_SUPER

        if not folder_id:
            return Response(
                {"detail": "La variable de entorno GOOGLE_DRIVE_SUPER no está configurada."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Inicializar servicio de Google Drive
        try:
            drive_service = GoogleDriveService()
            archivos = drive_service.listar_archivos(folder_id)

            if not archivos:
                return Response(
                    {"detail": "No se encontraron archivos en la carpeta especificada."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Crear directorio temporal
            temp_dir = Path("temp_drive_files")
            temp_dir.mkdir(exist_ok=True)

            # Procesar archivos
            resultados = []
            for archivo in archivos:
                destination = temp_dir / archivo["name"]
                drive_service.descargar_archivo(archivo["id"], destination)

                # Procesar el archivo
                resultado = self.procesar_archivo(destination)
                resultados.append(resultado)

                # Eliminar archivo local después del procesamiento
                destination.unlink()

            return Response(resultados, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error al procesar archivos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleDriveService:

    def __init__(self, credentials_json_path=None):
        """
        credentials_json_path: ruta al archivo .json con las credenciales de la cuenta de servicio
        """
        if not credentials_json_path:
            credentials_json_path = GOOGLE_SERVICE_ACCOUNT_JSON

        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_json_path, 
            scopes=GOOGLE_DRIVE_SCOPES
        )
        self.drive_service = build("drive", "v3", credentials=self.credentials)

    def upload_excel_file(self, file_path, file_name, folder_id):
        """
        Método para recibir un archivo Excel desde una solicitud y guardarlo en Google Drive.
        request: objeto de solicitud que contiene el archivo.
        """
        try:
            file_metadata = {
                "name": file_name,
                "parents": [folder_id]
            }

            media = MediaFileUpload(file_path, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            uploaded_file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

            return uploaded_file.get("id")

        except Exception as e:
            print(f"Error al subir el archivo a Google Drive: {str(e)}")
            raise

    def listar_archivos(self, folder_id):
        """
        Lista los archivos en la carpeta especificada de Google Drive.
        """
        query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        return results.get("files", [])

    def descargar_archivo(self, file_id, destination):
        """
        Descarga un archivo de Google Drive y lo guarda temporalmente.
        """
        request = self.drive_service.files().get_media(fileId=file_id)
        with open(destination, "wb") as f:
            #downloader = build.http.MediaIoBaseDownload(f, request)
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()