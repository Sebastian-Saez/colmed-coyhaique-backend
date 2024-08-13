from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Definimos las opciones para tipo_perfil
TIPOS_PERFILES  = [
    ('visitante', 'Visitante'),
    ('admin_noticias', 'Administrador Noticias'),
    ('admin_colmed', 'Administrador Colmed'),
    ('gestor_informatico', 'Gestor Informático'),
]

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_perfil = models.CharField(max_length=50, choices=TIPOS_PERFILES, default='visitante')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Beneficio(models.Model):
    descripcion = models.CharField(max_length=255)
    fecha_alta = models.DateField(null=True, blank=True)
    fecha_baja = models.DateField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario_modificacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="beneficios_modificados")

    def __str__(self):
        return self.descripcion

class Plaza(models.Model):
    codigo = models.BigIntegerField(unique=True)
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
