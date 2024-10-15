from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
# from base_medicos.models import Medico

# Definimos las opciones para tipo_perfil
TIPOS_PERFILES  = [
    ('visitante', 'Visitante'),
    ('admin_noticias', 'Administrador Noticias'),
    ('admin_colmed', 'Administrador Colmed'),
    ('gestor_informatico', 'Gestor Informático'),
]

TIPOS_CUOTAS  = [
    ('aps_2019', 'APS 2019'),
    ('entera_9', 'Entera+9'),
    ('entera_39', 'Entera39'),
    ('media_joven', 'Media Joven'),
    ('no_informado', 'No informado')
]

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_perfil = models.CharField(max_length=50, choices=TIPOS_PERFILES, default='visitante')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

# class Colegiatura(models.Model):
#     medico = models.OneToOneField(Medico, on_delete=models.CASCADE)  # Relación uno a uno con el modelo Médico
#     lugar_descuento = models.CharField(max_length=255, blank=True, null=True)  # Lugar de descuento por estar colegiado
#     tipo_cuota = models.CharField(max_length=50, choices=TIPOS_CUOTAS, default='no_informado')  # Tipo de cuota
#     fecha_inscripcion_col = models.DateField(null=True, blank=True)  # Fecha de inscripción a la colegiatura
#     fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de actualización automática

#     def __str__(self):
#         return f'Colegiatura de {self.medico.user.get_full_name() if self.medico.user else self.medico.rut}'

#     class Meta:
#         verbose_name = "Colegiatura"
#         verbose_name_plural = "Colegiaturas"


class Beneficio(models.Model):
    descripcion = models.CharField(max_length=255)
    fecha_alta = models.DateField(null=True, blank=True)
    fecha_baja = models.DateField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario_modificacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="beneficios_modificados")

    def __str__(self):
        return self.descripcion

class Plaza(models.Model):
    codigo = models.BigIntegerField(unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    detalle = models.TextField()
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Evento(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    id_evento_google = models.CharField(max_length=255)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="eventos_creados")
    

    def __str__(self):
        return self.titulo

# Nuevo modelo Entidad
class Entidad(models.Model):
    nombre_entidad = models.CharField(max_length=100)
    sigla = models.CharField(max_length=50, default='')
    
    def __str__(self):
        return self.nombre_entidad

# Nuevo modelo Estamento
class Estamento(models.Model):
    nombre_estamento = models.CharField(max_length=255, null=True, blank=True)
    descripcion_estamento = models.CharField(max_length=255, null=True, blank=True)
    codigo_estamento = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.nombre_estamento} ({self.codigo_estamento})'

# Nuevo modelo LugarDescuento
class LugarDescuento(models.Model):
    nombre_lugar = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_lugar