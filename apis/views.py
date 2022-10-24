from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.renderers import JSONRenderer

from django.db.models import Q

import json

# import local data
from conciertos.serializers import ConciertosSerializer
from lanzamiento.serializers import LanzamientosSerializer
from banda.serializers import BandasSerializer
from conciertos.models import Conciertos
from archivo.models import Lanzamiento
from archivo.models import Banda


# create a viewset
class ConciertosViewSet(viewsets.ModelViewSet):
	
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	parser_classes = [MultiPartParser]
	
	# define queryset
	queryset = Conciertos.objects.all()
	
	# specify serializer to be used
	serializer_class = ConciertosSerializer


class LanzamientosViewSet(viewsets.ModelViewSet):
	
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	parser_classes = [MultiPartParser]
	
	# define queryset
	queryset = Lanzamiento.objects.all()
	
	# specify serializer to be used
	serializer_class = LanzamientosSerializer

	#renderer_classes = [JSONRenderer]
	@action(detail=True, methods=['post'])
	def asignar(self, request, *args, **kwargs):

		bandas = request.data.get("bandas")
		id_lanzamiento = kwargs.get("pk")
		ids_asignar = []
		nombres_bandas_encontradas = []
		nombres_bandas_no_encontradas = []
		if bandas and id_lanzamiento:
			bandas = [ _.strip() for _ in bandas.split(",")]

			for nombre in bandas:
				resultado_query = Banda.objects.filter(
					Q(nombre__icontains=nombre) |
					Q(otros__icontains=nombre)
				)

				for banda in resultado_query:
					ids_asignar.append(banda.id)
					nombres_bandas_encontradas.append(banda.nombre)
					break
				else:
					nombres_bandas_no_encontradas.append(nombre)

			lanzamiento = Lanzamiento.objects.get(id=id_lanzamiento)
			for id_banda in ids_asignar:
				lanzamiento.bandas.add(Banda.objects.get(id=id_banda))
			lanzamiento.save()

		banda_response = {
			'found': nombres_bandas_encontradas,
			'not_found': nombres_bandas_no_encontradas
		}
		return Response(banda_response)


class BandaViewSet(viewsets.ModelViewSet):
	
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	parser_classes = [MultiPartParser]
	
	# define queryset
	queryset = Banda.objects.all()
	
	# specify serializer to be used
	serializer_class = BandasSerializer


		