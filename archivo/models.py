from django.core.files.uploadedfile import InMemoryUploadedFile

from django.db import models

from django.db.models.signals import post_delete
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


from PIL import Image

from archivodjango.settings import MEDIA_ROOT
from io import BytesIO

import logging
import os
import re
import sys

logger = logging.getLogger(__name__)

lista_formatos = ['CD', 'Digipack','12"','10"','7"','Flexi','Cassette','Digital','Mini CD','DVD','Otros','Bootleg']

FORMATOS = (
    list(
        zip(
            [str(x) for x in range(1,len(lista_formatos)+1)],
            lista_formatos
        )
    )
)

def resize(max_width, width, height):
    wpercent = (max_width/float(width))
    hsize = int((float(height)*float(wpercent)))
    return (max_width, hsize)


def generar_nombrecorto(nombre, model):

    nombrecorto = nombre.lower()
    nombrecorto = re.sub('[^A-Za-z0-9]', '', nombrecorto)
    nombrecorto = nombrecorto[0:27]
        
    no_existe = True
    contador = 0

    while no_existe:
        try:
            sufijo = ''
            if contador != 0:
                sufijo = str(contador)
            objetos = model.objects.get(nombrecorto=nombrecorto + sufijo)
            contador += 1
        except Exception as e:
            nombrecorto = nombrecorto + sufijo
            no_existe = False
    return nombrecorto

class Banda(models.Model):
    nombre = models.CharField(max_length=100)
    nombrecorto = models.CharField(unique=True, max_length=30)
    otros = models.TextField(blank=True, null=True)
    integrantes = models.TextField(blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    imagen = models.FileField(blank=True, null=True)
    imagen_thumbnail = models.FileField(blank=True, null=True)
    extranjera = models.BooleanField()
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)
    lanzamientos = models.ManyToManyField('Lanzamiento', through='BandaLanzamiento', blank=True)

    class Meta:
        managed = False
        db_table = 'banda'

    def __str__(self):
        return str(self.id) + ' - ' +self.nombre


class BandaLanzamiento(models.Model):
    banda = models.ForeignKey('Banda', on_delete=models.CASCADE)
    lanzamiento = models.ForeignKey('Lanzamiento', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'banda_lanzamiento'

    def __str__(self):
        return self.banda.nombre + ' - ' + self.lanzamiento.nombre
    

class Lanzamiento(models.Model):
    nombre = models.TextField()
    nombrecorto = models.CharField(unique=True, max_length=30)
    referencia = models.TextField(blank=True, null=True)
    formato = models.CharField(max_length=8, blank=False, null=True, choices=FORMATOS)
    anho = models.TextField(blank=True, null=True)
    tracklist = models.TextField(blank=True, null=True)
    creditos = models.TextField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    link_youtube = models.TextField(blank=True, null=True)
    indice_referencia = models.TextField(blank=True, null=True)
    imagen = models.FileField(blank=True, null=True)
    imagen_thumbnail = models.FileField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)
    lanzamiento = models.BooleanField()
    visible = models.BooleanField()
    disponible = models.BooleanField()
    portadas = models.BooleanField()
    disco_digitalizado = models.BooleanField()
    nota_digitalizacion = models.TextField(blank=True)
    bandas = models.ManyToManyField('Banda', through='BandaLanzamiento', blank=True)

    class Meta:
        managed = False
        db_table = 'lanzamiento'

    def __str__(self):
        return self.nombre

class Publicacion(models.Model):
    nombre = models.TextField()
    nombrecorto = models.CharField(max_length=30)
    fecha = models.TextField(blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    indice_referencia = models.TextField(blank=True, null=True)
    imagen = models.FileField(blank=True, null=True)
    imagen_thumbnail = models.FileField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)
    visible = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'publicacion'

    def __str__(self):
        return self.nombre


#https://matthiasomisore.com/uncategorized/django-delete-file-when-object-is-deleted/
@receiver(post_delete, sender=Banda)
@receiver(post_delete, sender=Lanzamiento)
@receiver(post_delete, sender=Publicacion)
def submission_delete(sender, instance, **kwargs):
    logger.debug("Borrando imagen y thumbnail...")
    try:
        instance.imagen.delete(False) 
        instance.imagen_thumbnail.delete(False)
    except Exception as e:
        logger.error("No se pudo borrar el archivo, error:" + str(e))
    else:
        logger.debug("Borrado exitoso")
