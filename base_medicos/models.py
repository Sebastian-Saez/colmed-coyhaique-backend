from django.db import models
from django.contrib.auth.models import User

class Medico(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    contacto = models.CharField(max_length=255)
    icm = models.BigIntegerField(unique=True)
    fecha_nacimiento = models.DateField()
    fecha_titulo = models.DateField()
    moroso = models.BooleanField(null=True, blank=True)
    cuotas_totales = models.BigIntegerField(null=True, blank=True)
    registro_superintendencia = models.BigIntegerField()
    rut = models.CharField(max_length=255)
    directiva = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.contacto} ({self.icm})"

class Cuota(models.Model):
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField()
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

    def __str__(self):
        return f'Cuota {self.monto} - {self.fecha}'
