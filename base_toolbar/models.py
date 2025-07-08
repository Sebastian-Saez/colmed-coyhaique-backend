from django.db import models

class MisionVision(models.Model):
    mision = models.TextField(blank=True, null=True)
    vision = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Misión y Visión"

class NormativaItem(models.Model):
    titulo   = models.CharField(max_length=255, blank=True,null=True)
    contenido = models.TextField(blank=True,null=True)
    link   = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.titulo
    
class DirectivaMember(models.Model):
    cargo   = models.CharField(max_length=255, blank=True, null=True)
    persona = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.cargo}: {self.persona}"
    
class Departamento(models.Model):
    titulo               = models.CharField(max_length=255, blank=True, null=True)
    descripcion_general  = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo

class AgrupacionRegional(models.Model):
    titulo      = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo
    
class Capitulo(models.Model):
    titulo    = models.CharField(max_length=255, blank=True, null=True)
    contenido = models.TextField(blank=True, null=True)
    link      = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.titulo
    
class TribunalEtica(models.Model):
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Tribunal de Ética"
    
class TribunalMember(models.Model):
    tribunal = models.ForeignKey(TribunalEtica, related_name="directiva", on_delete=models.CASCADE)
    cargo    = models.CharField(max_length=255)
    persona  = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.cargo}: {self.persona}"
    
class PaymentInfo(models.Model):
    # encabezados
    titulo               = models.CharField(max_length=255, blank=True, null=True)
    subtitulo            = models.CharField(max_length=255, blank=True)
    descripcion_general  = models.TextField(blank=True)
    detalle_cuotas       = models.TextField(blank=True)

    # cuotas
    notas                = models.JSONField(default=list, blank=True, null=True)        # ["nota1", "nota2", …]
    tipos_cuotas         = models.JSONField(default=list, blank=True, null=True)        # [{tipo_cuota, descripcion}, …]
    valores_cuotas       = models.JSONField(default=list, blank=True, null=True)        # tabla grande
    detalle_fsg          = models.JSONField(default=list, blank=True, null=True)        # tabla pequeña
    # reafiliación
    reafiliacion_titulo       = models.CharField(max_length=255, blank=True)
    reafiliacion_descripcion  = models.TextField(blank=True)
    valores_reafiliacion      = models.JSONField(default=list, blank=True, null=True)   # tabla

    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Información de Pagos"
    
class ColegiarseInfo(models.Model):
    # bloques/etiquetas + contenidos
    quienesTitulo             = models.CharField(max_length=255, blank=True)
    quienes                   = models.TextField(blank=True)

    comoTitulo                = models.CharField(max_length=255, blank=True)
    procedimiento             = models.TextField(blank=True)
    linkInscripcion           = models.CharField(max_length=500,blank=True, null=True)

    infoPreviaTitulo          = models.CharField(max_length=255, blank=True)
    documentos                = models.TextField(blank=True)

    medicosChileTitulo        = models.CharField(max_length=255, blank=True)
    medicosChileContenido     = models.TextField(blank=True)

    medicosExtranjeroTitulo   = models.CharField(max_length=255, blank=True)
    medicosExtranjeroContenido= models.TextField(blank=True)

    queHaceTitulo             = models.CharField(max_length=255, blank=True)
    queHaceContenido          = models.TextField(blank=True)

    porqueTitulo              = models.CharField(max_length=255, blank=True)
    porqueContenido           = models.TextField(blank=True)

    deberesTitulo             = models.CharField(max_length=255, blank=True)
    deberesContenido          = models.TextField(blank=True)
    derechosContenido         = models.TextField(blank=True)

    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Cómo colegiarse"

class CasaMedicoInfo(models.Model):
    descripcion = models.TextField(blank=True, null=True)
    habitaciones = models.JSONField(default=list, blank=True, null=True)  # [{nombre, descripcion}, …]
    detalles     = models.JSONField(default=list, blank=True, null=True)  # ["detalle1", "detalle2", …]

    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Casa del Médico"