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
    ('admin_eventos', 'Administrador de Eventos y Comunicaciones'),
    ('admin_sitio', 'Administrador del Sitio'),
]

TIPOS_CUOTAS  = [
    ('aps_2019', 'APS 2019'),
    ('entera_9', 'Entera+9'),
    ('entera_39', 'Entera39'),
    ('media_joven', 'Media Joven'),
    ('no_informado', 'No informado')
]

class Perfil(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="perfiles")
    tipo_perfil = models.CharField(max_length=50, choices=TIPOS_PERFILES, default='visitante')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo_perfil} ({self.user.username})"

class Beneficio(models.Model):
    titulo = models.CharField(max_length=255, null=True, blank=True, default="")
    descripcion = models.TextField(blank=True, null=True)
    fecha_alta = models.DateField(null=True, blank=True)
    fecha_baja = models.DateField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario_modificacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="beneficios_modificados")

    def __str__(self):
        return self.titulo

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
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    id_evento_google = models.CharField(max_length=255, null=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="eventos_creados")
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    
    def __str__(self):
        return self.titulo
    
class PublicidadMedica(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    link = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="publicidades_medicas_creadas")
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
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