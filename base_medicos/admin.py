from django.contrib import admin
from .models import Medico, Afiliacion, RegistroSuperintendencia, Institucion, Especialidad, OrdenProfesional, MedicoAppMovil

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('user_first_name','user_last_name','user_email','contacto','numero_registro_superintendencia','condicion_vital','icm','fecha_nacimiento','fecha_titulo','rut','directiva')
    list_filter = ['condicion_vital','directiva']

    # Método para mostrar el primer nombre del usuario
    def user_first_name(self, obj):
        return obj.user.first_name if obj.user else None
    user_first_name.short_description = 'Nombre'

    # Método para mostrar el primer nombre del usuario
    def numero_registro_superintendencia(self, obj):
        return obj.registro_superintendencia.numero_registro if obj.registro_superintendencia else None
    numero_registro_superintendencia.short_description = 'Numero de Registro'

    # Método para mostrar el apellido del usuario
    def user_last_name(self, obj):
        return obj.user.last_name if obj.user else None
    user_last_name.short_description = 'Apellido'

    # Método para mostrar el email del usuario
    def user_email(self, obj):
        return obj.user.email if obj.user else None
    user_email.short_description = 'Email'

@admin.register(MedicoAppMovil)
class MedicoAppMovilAdmin(admin.ModelAdmin):
    list_display = ('user_first_name','user_last_name','user_email','email','fecha_inscripcion','fcm_token')
    list_filter = ['email', 'fecha_inscripcion']

    def user_first_name(self, obj):
        return obj.medico.user.first_name if obj.medico else None
    user_first_name.short_description = 'Nombre'

    def user_last_name(self, obj):
        return obj.medico.user.last_name if obj.medico else None
    user_last_name.short_description = 'Apellido'

    def user_email(self, obj):
        return obj.medico.user.email if obj.medico else None
    user_email.short_description = 'Email Usuario'

@admin.register(Afiliacion)
class AfiliacionAdmin(admin.ModelAdmin):
    list_display = ('medico','entidad','estado_pago','tipo_cuota','condicion_afiliado','anio_ucp','mes_ucp','estamento','num_ultima_cuota','lugar_descuento','fecha_inscripcion')
    list_filter = ['estado_pago','tipo_cuota','condicion_afiliado','fecha_inscripcion']

@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ('nombre','fecha_modificacion')

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre','descripcion','fecha_certificacion','institucion')
    list_filter = ['nombre']

    def institucion(self, obj):
        return obj.institucion_certificadora.nombre if obj.universidad_titulo else None
    institucion.short_description = 'Nombre'

@admin.register(OrdenProfesional)
class OrdenProfesionalAdmin(admin.ModelAdmin):
    list_display = ('nombre','descripcion','fecha_certificacion','institucion')
    list_filter = ['nombre']

    def institucion(self, obj):
        return obj.institucion_certificadora.nombre if obj.universidad_titulo else None
    institucion.short_description = 'Nombre'

@admin.register(RegistroSuperintendencia)
class RegistroSuperintendenciaAdmin(admin.ModelAdmin):
    list_display = ('numero_registro','nacionalidad','fecha_nacimiento','fecha_registro','detalle_especialidades','detalle_titulos')
    list_filter = ['numero_registro', 'nacionalidad']    

    # Método para mostrar las especialidades
    def detalle_especialidades(self, obj):
        return ", ".join([esp.nombre for esp in obj.especialidades.all()]) if obj.especialidades.exists() else None
    detalle_especialidades.short_description = 'Especialidades'

    def detalle_titulos(self, obj):
        return ", ".join([esp.nombre for esp in obj.ordenes_profesionales.all()]) if obj.ordenes_profesionales.exists() else None
    detalle_titulos.short_description = 'OrdenProfesional'