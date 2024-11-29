from django.contrib import admin
from .models import Medico, Afiliacion

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('user_first_name','user_last_name','user_email','contacto','condicion_vital','icm','fecha_nacimiento','fecha_titulo','registro_superintendencia','rut','directiva')
    list_filter = ['condicion_vital','directiva']

    # Método para mostrar el primer nombre del usuario
    def user_first_name(self, obj):
        return obj.user.first_name if obj.user else None
    user_first_name.short_description = 'Nombre'

    # Método para mostrar el apellido del usuario
    def user_last_name(self, obj):
        return obj.user.last_name if obj.user else None
    user_last_name.short_description = 'Apellido'

    # Método para mostrar el email del usuario
    def user_email(self, obj):
        return obj.user.email if obj.user else None
    user_email.short_description = 'Email'

@admin.register(Afiliacion)
class AfiliacionAdmin(admin.ModelAdmin):
    list_display = ('medico','entidad','estado_pago','tipo_cuota','condicion_afiliado','anio_ucp','mes_ucp','estamento','num_ultima_cuota','lugar_descuento','fecha_inscripcion')
    list_filter = ['estado_pago','tipo_cuota','condicion_afiliado','fecha_inscripcion']