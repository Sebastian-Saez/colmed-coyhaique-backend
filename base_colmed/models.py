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
    privado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.titulo
    
class Convenio(models.Model):
    TIPO_CHOICES = (
        ('nacional', 'Nacional'),
        ('regional', 'Regional'),
    )
    
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    # Campo para determinar si el convenio es para convenios nacionales o regionales
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    # Enlace opcional (por ejemplo, para los convenios nacionales se puede redirigir a más detalles)
    ref = models.URLField(blank=True, null=True)
    # Si se requiere, se puede almacenar una imagen
    # imagen = models.ImageField(upload_to='convenios/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Convenio'
        verbose_name_plural = 'Convenios'
    
    def __str__(self):
        return self.titulo


class ConveniosConfig(models.Model):
    """
    Modelo de configuración para almacenar datos generales de los convenios,
    como el enlace para 'Todos los convenios'.
    """
    todos_convenios_link = models.URLField(
        help_text="URL para 'Todos los convenios'",
        blank=True,
        null=True
    )

    def __str__(self):
        return "Configuración de Convenios"

    class Meta:
        verbose_name = "Configuración de Convenios"
        verbose_name_plural = "Configuraciones de Convenios"
    
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
    

class LinkInteres(models.Model):
    titulo = models.CharField(max_length=255)
    clave = models.CharField(max_length=30, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    url = models.URLField()
    orden = models.PositiveIntegerField(default=0)  # Para ordenarlos si es necesario

    class Meta:
        ordering = ['orden']
        verbose_name = "Link de Interés"
        verbose_name_plural = "Links de Interés"

    def __str__(self):
        return self.titulo


class ContactoInteres(models.Model):
    nombre = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    privado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contacto de Interés"
        verbose_name_plural = "Contactos de Interés"

    def __str__(self):
        return self.nombre