from django.contrib import admin
from .models import Medico

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ('user','contacto','icm','fecha_nacimiento','fecha_titulo','moroso','cuotas_totales','registro_superintendencia','rut','directiva')