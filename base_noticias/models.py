from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Noticia(models.Model):
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    resumen_contenido = models.TextField(max_length=200, default="", blank=True)
    destacada = models.BooleanField(default=False, null=True, blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="noticias_creadas")
    #imagen = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='noticias/', null=True, blank=True)
    video = models.TextField(null=True, blank=True)
    link = models.JSONField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
