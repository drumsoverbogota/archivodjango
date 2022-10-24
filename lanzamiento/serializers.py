from random import choices
from rest_framework import serializers

from archivo.models import generar_nombrecorto
from utils.image_utilities import upload_image
from archivo.models import Lanzamiento
from archivo.models import Banda
from archivo.models import FORMATOS


class Bandas(serializers.ModelSerializer):
    class Meta:
        model = Banda
        fields = ['nombre']

class LanzamientosSerializer(serializers.Serializer):

    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField()
    bandas = Bandas(many=True, read_only=True)
    referencia = serializers.CharField(allow_blank=True, required=False)
    formato = serializers.ChoiceField(choices=FORMATOS)
    anho = serializers.CharField(allow_blank=True, required=False)
    notas = serializers.CharField(allow_blank=True, required=False)
    link = serializers.CharField(allow_blank=True, required=False)
    imagen = serializers.FileField(allow_empty_file=True, required=False)
    tracklist = serializers.CharField(allow_blank=True, required=False)
    creditos = serializers.CharField(allow_blank=True, required=False)
    notas = serializers.CharField(allow_blank=True, required=False)
    link = serializers.CharField(allow_blank=True, required=False)
    link_youtube = serializers.CharField(allow_blank=True, required=False)
    indice_referencia = serializers.CharField(allow_blank=True, required=False)
    nota_digitalizacion = serializers.CharField(allow_blank=True, required=False)
    lanzamiento = serializers.BooleanField()
    disponible = serializers.BooleanField()
    portadas = serializers.BooleanField()
    disco_digitalizado = serializers.BooleanField()



    def create(self, validated_data):

        nueva_entrada = Lanzamiento(**validated_data)

        try:
            id_concierto = Lanzamiento.objects.latest('id').id + 1
        except:
            id_concierto = 1
        nombrecorto = generar_nombrecorto(nueva_entrada.nombre, Lanzamiento)

        nueva_entrada.id = id_concierto
        nueva_entrada.nombrecorto = nombrecorto

        nueva_entrada = upload_image(nueva_entrada=nueva_entrada)

        nueva_entrada.save()
        return nueva_entrada 
