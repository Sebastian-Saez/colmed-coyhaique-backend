from django.contrib import admin
from .models import Medico, Afiliacion

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('user','contacto','condicion_vital','icm','fecha_nacimiento','fecha_titulo','registro_superintendencia','rut','directiva')
    list_filter = ['condicion_vital','directiva']

@admin.register(Afiliacion)
class AfiliacionAdmin(admin.ModelAdmin):
    list_display = ('medico','entidad','estado_pago','tipo_cuota','condicion_afiliado','anio_ucp','mes_ucp','estamento','num_ultima_cuota','lugar_descuento','fecha_inscripcion')
    list_filter = ['estado_pago','tipo_cuota','condicion_afiliado','fecha_inscripcion']