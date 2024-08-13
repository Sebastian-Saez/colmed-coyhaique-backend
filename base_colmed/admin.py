from django.contrib import admin
from .models import Perfil, Beneficio, Plaza, Evento

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('tipo_perfil', 'activo')

@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'fecha_alta', 'fecha_baja', 'fecha_modificacion','usuario_modificacion')

@admin.register(Plaza)
class PlazaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'detalle', 'fecha_modificacion')

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion','fecha_inicio','fecha_fin','id_evento_google','autor')

