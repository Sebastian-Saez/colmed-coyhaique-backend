from django.db import models
from django.contrib.auth.models import User
from base_colmed.models import Plaza, Entidad, LugarDescuento, Estamento

TIPOS_ESTADO_PAGO  = [
    ('al_dia', 'AL DIA'),
    ('moroso', 'MOROSO'),
    ('moroso12', 'MOROSO12'),
    ('liberado', 'LIBERADO'),
    ('casado_medico', 'CASADO CON MEDICO'),
    ('falmed_senior_liberado', 'FALMED SENIOR LIBERADO'),
    ('liberado_rescate', 'LIBERADO POR RESCATE'),
    ('liberado_directorio_falmed', 'LIBERADO DIRECTORIO FALMED'),
    ('recien_inscrito', 'RECIEN INSCRITO'),
    ('proceso_a_desafiliar', 'PROCESO A DESAFILIAR'),
    ('no_aplica', 'No aplica')
]

TIPOS_DIRECTIVA = [
    ('presidente', 'Presidente'),
    ('presidenta', 'Presidenta'),
    ('vicepresidente', 'VicePresidente'),
    ('vicepresidenta', 'VicePresidenta'),
    ('secretaria', 'Secretaria'),
    ('secretario', 'Secretario'),
    ('tesorera', 'Tesorera'),
    ('tesorero', 'Tesorero'),
    ('consejero', 'Consejero'),
    ('consejera', 'Consejera'),
    ('', '------')
]

TIPOS_ESTADO_AFILIACION  = [
    ('afiliado', 'AFILIADO'),
    ('afiliado_pendiente', 'AFILIADO PENDIENTE'),
    ('condecoracion_honor', 'CONDECORACION DE HONOR'),
    ('desafiliado', 'DESAFILIADO'),
    ('renunciado', 'RENUNCIADO'),
    ('renunciado_dir', 'RENUNCIADO DIR'),
    ('expulsado', 'EXPULSADO'),
    ('inscripcion_rechazada', 'INSCRIPCION RECHAZADA'),
    ('no_inscrito', 'NO INSCRITO'),
    ('reaf_pend_aprob_mesa', 'REAF. PEND. APROB. MESA'),
    ('reaf_pend_aprob_smrio_etico', 'REN. PEND. APRB. SMRIO. ETICO'),
    ('reafiliacion_rechazada', 'REAFILIACION RECHAZADA'),
    ('reinscrito', 'REINSCRITO'),
    ('no_aplica', 'No aplica')
]

#Registro Superintendencia
class Institucion (models.Model):
    nombre = models.CharField(max_length=255)
    fecha_modificacion = models.DateTimeField(auto_now=True)

class OrdenProfesional (models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    fecha_certificacion = models.DateField()
    institucion_certificadora = models.ForeignKey('Institucion',related_name='universidad', blank=True, null=True, on_delete=models.SET_NULL)


class Especialidad(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    fecha_certificacion = models.DateField()
    institucion_certificadora = models.ForeignKey('Institucion',related_name='institucion', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.nombre

class RegistroSuperintendencia(models.Model):
    numero_registro = models.CharField(max_length=20, unique=True)
    fecha_registro = models.DateField()
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=20, default="")
    ordenes_profesionales = models.ManyToManyField('OrdenProfesional', related_name='ordenes_profesionales')
    especialidades = models.ManyToManyField('Especialidad', related_name='especialidades')
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.numero_registro

class Medico(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    rut = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Ahora permite nulos y vacíos
    icm = models.BigIntegerField(unique=True, null=True, blank=True)  # Ahora permite nulos y vacíos
    contacto = models.CharField(max_length=255, blank=True, null=True, default="")
    direccion = models.CharField(max_length=255, null=True, blank=True)
    comuna = models.CharField(max_length=255, null=True, blank=True)
    condicion_vital = models.CharField(max_length=255, blank=True, null=True, default="")    
    fecha_nacimiento = models.DateField(null=True, blank=True)  # Ahora permite nulos y vacíos
    fecha_titulo = models.DateField(null=True, blank=True)  # Ahora permite nulos y vacíos
    #regional = models.CharField(max_length=100, null=True, blank=True)
    #fecha_inscripcion_col = models.DateField(null=True, blank=True)  # Ahora permite nulos y vacíos
    #moroso = models.CharField(max_length=50, choices=TIPOS_ESTADO_PAGO, default='no_informado')
    #condicion_colmed = models.CharField(max_length=50, choices=TIPOS_ESTADO_AFILIACION, default='no_colegiado')
    #cuotas_totales = models.BigIntegerField(null=True, blank=True)
    registro_superintendencia = models.ForeignKey('RegistroSuperintendencia', related_name='registro_superintendencia',null=True, blank=True, on_delete=models.SET_NULL)
    directiva = models.CharField(max_length=255, null=True, blank=True, choices=TIPOS_DIRECTIVA, default='')        
    plaza = models.ForeignKey(Plaza, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user} ({self.icm})"

class Afiliacion(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    entidad = models.ForeignKey(Entidad, on_delete=models.CASCADE)
    tipo_cuota = models.CharField(max_length=50, null=True, blank=True, default='')
    condicion_afiliado = models.CharField(max_length=50, choices=TIPOS_ESTADO_AFILIACION, default='no_aplica')
    estado_pago = models.CharField(max_length=50, choices=TIPOS_ESTADO_PAGO, default='no_aplica')
    anio_ucp = models.IntegerField(null=True, blank=True)
    mes_ucp = models.IntegerField(null=True, blank=True)
    estamento = models.ForeignKey(Estamento, null=True, blank=True, on_delete=models.SET_NULL)
    num_ultima_cuota = models.IntegerField(null=True, blank=True)
    lugar_descuento = models.ForeignKey(LugarDescuento, null=True, blank=True, on_delete=models.SET_NULL)
    #fecha_ultima_cuota = models.DateField(null=True, blank=True)
    fecha_inscripcion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.medico} - {self.entidad.nombre_entidad}"

class Cuota(models.Model):
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField()
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

    def __str__(self):
        return f'Cuota {self.monto} - {self.fecha}'
    

