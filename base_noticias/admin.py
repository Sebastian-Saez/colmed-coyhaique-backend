from django.contrib import admin
from .models import Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'resumen_contenido','destacada','contenido','fecha_modificacion','autor','imagen','video','link','activo')
    list_filter = ['titulo', 'destacada','activo']