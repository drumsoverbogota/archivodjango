from django.db import models

# Create your models here.
class Conciertos(models.Model):
    nombre = models.TextField()
    nombrecorto = models.CharField(max_length=30)
    fecha_grabacion = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    imagen = models.FileField(blank=True, null=True)
    imagen_thumbnail = models.FileField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    visible = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'conciertos'

    def __str__(self):
        return self.nombre