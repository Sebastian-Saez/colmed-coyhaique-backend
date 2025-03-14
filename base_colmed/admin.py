from django.contrib import admin
from .models import Perfil, Beneficio, Plaza, Evento, Estamento, Entidad, LugarDescuento, PublicidadMedica, Convenio, ConveniosConfig, ContactoInteres, LinkInteres

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user','tipo_perfil', 'activo')

@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion', 'fecha_alta', 'fecha_baja', 'fecha_modificacion','usuario_modificacion')

@admin.register(Plaza)
class PlazaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'detalle', 'fecha_modificacion')

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion','fecha_inicio','fecha_fin','id_evento_google','autor','privado','activo')
    
@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion','ref','tipo','created_at','updated_at')

@admin.register(LinkInteres)
class LinkInteresAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion','url','orden', 'clave')
    list_filter = ['orden']

@admin.register(ContactoInteres)
class ContactoInteresAdmin(admin.ModelAdmin):
    list_display = ('nombre','cargo','email','telefono','privado')
    list_filter = ['privado']

@admin.register(ConveniosConfig)
class ConveniosConfigAdmin(admin.ModelAdmin):
    list_display = ('todos_convenios_link',)

@admin.register(PublicidadMedica)
class PublicidadMedicaAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion','link','autor','activo')

@admin.register(Entidad)
class EntidadAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad','sigla')

@admin.register(Estamento)
class EstamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre_estamento','descripcion_estamento','codigo_estamento')



