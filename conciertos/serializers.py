from rest_framework import serializers

from archivo.models import generar_nombrecorto
from utils.image_utilities import upload_image
from .models import Conciertos


class ConciertosSerializer(serializers.Serializer):

    nombre = serializers.CharField()
    fecha_grabacion = serializers.DateField()
    notas = serializers.CharField(allow_blank=True)
    link = serializers.CharField(allow_blank=True)
    imagen = serializers.FileField(allow_empty_file=True, required=False)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        nueva_entrada = Conciertos(**validated_data)


        try:
            id_concierto = Conciertos.objects.latest('id').id + 1
        except:
            id_concierto = 1
        nombrecorto = generar_nombrecorto(nueva_entrada.nombre, Conciertos)

        nueva_entrada.id = id_concierto
        nueva_entrada.nombrecorto = nombrecorto

        nueva_entrada = upload_image(nueva_entrada=nueva_entrada)

        nueva_entrada.save()
        return nueva_entrada 
        

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.nombrecorto = validated_data.get('nombrecorto', instance.nombrecorto)
        instance.fecha_grabacion = validated_data.get('fecha_grabacion', instance.fecha_grabacion)
        instance.notas = validated_data.get('notas', instance.notas)
        instance.link = validated_data.get('link', instance.link)
        instance.imagen = validated_data.get('imagen', instance.imagen)
        instance.save()
        return instance