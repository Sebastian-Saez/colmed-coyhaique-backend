from django.contrib import admin
from .models import (
    MisionVision, NormativaItem, DirectivaMember,
    Departamento, AgrupacionRegional, Capitulo,
    TribunalEtica, TribunalMember,
    PaymentInfo,ColegiarseInfo, CasaMedicoInfo
)

@admin.register(MisionVision)
class MisionVisionAdmin(admin.ModelAdmin):
    list_display = ('mision','vision')

@admin.register(NormativaItem)
class NormativaItemAdmin(admin.ModelAdmin):
    list_display = ('titulo','contenido','link')
    list_filter = ['titulo',]
    
@admin.register(DirectivaMember)
class DirectivaMemberAdmin(admin.ModelAdmin):
    list_display = ('cargo','persona')
    list_filter = ['cargo','persona']

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion_general')
    list_filter = ['titulo',]

@admin.register(AgrupacionRegional)
class AgrupacionRegionalAdmin(admin.ModelAdmin):
    list_display = ('titulo','descripcion')
    list_filter = ['titulo',]

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('titulo','contenido','link')
    list_filter = ['titulo',]

@admin.register(TribunalEtica)
class TribunalEticaAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)
    
@admin.register(TribunalMember)
class TribunalMemberAdmin(admin.ModelAdmin):
    list_display = ('tribunal_etica','cargo','persona')
    list_filter = ['cargo',]

    def tribunal_etica(self, obj):
        return obj.tribunal.descripcion if obj.tribunal else None
    tribunal_etica.short_description = 'Tribunal de Ética'

# Módulo de SERVICIOS
@admin.register(PaymentInfo)
class PaymentInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'fecha_modificacion')
    list_filter = ['titulo',]
    readonly_fields = ('fecha_modificacion',)


@admin.register(ColegiarseInfo)
class ColegiarseInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'quienesTitulo','comoTitulo','linkInscripcion', 'fecha_modificacion')
    list_filter = ['quienesTitulo',]
    readonly_fields = ('fecha_modificacion',)


@admin.register(CasaMedicoInfo)
class CasaMedicoInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'fecha_modificacion')
    list_filter = ['descripcion',]
    readonly_fields = ('fecha_modificacion',)