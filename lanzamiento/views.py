from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render

from django.http import Http404

# Create your views here.

from django.utils import timezone

from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.urls import reverse

from archivo.models import generar_nombrecorto
from utils.image_utilities import resize
from archivo.models import Banda
from archivo.models import BandaLanzamiento
from archivo.models import Lanzamiento
from archivodjango.settings import MEDIA_ROOT
from archivodjango.settings import ENTRADA_BLOG

from .forms import LanzamientoForm
from .forms import OrderForm 

from io import BytesIO
from PIL import Image

import logging
import os
import sys

logger = logging.getLogger(__name__)

class LanzamientoIndexView(ListView):
    template_name = 'lanzamiento/index.html'
    context_object_name = 'lanzamientos'
    paginate_by = 20

    no_disponibles = False
    no_visibles = False
    objectos_pagina = 20
    orden = "ascendente"
    ordenar_por = "nombre"

    def get_queryset(self):

        get_request = self.request.GET.get

        if get_request("no_disponibles") == "true":
            self.no_disponibles = True

        if get_request("no_visibles") == "true":
            self.no_visibles = True

        self.objectos_pagina = get_request("numero", 20)
        self.orden = get_request("orden", "ascendente")
        self.ordenar_por = get_request("ordenar_por", "nombre")

        orden = ""

        if self.orden == "descendente":
            orden = "-"
        else:
            orden = ""

        self.paginate_by = self.objectos_pagina

        filtros = {}

        if not self.no_visibles:
            filtros['visible'] = True
        if not self.no_disponibles:
            filtros['disponible'] = True

        return Lanzamiento.objects.filter(**filtros).order_by(orden + self.ordenar_por)

    def get_context_data(self, **kwargs):

        get_request = self.request.GET.get
        context = super().get_context_data(**kwargs)

        context["no_disponibles"] = self.no_disponibles
        context["visibles"] = self.no_visibles

        iniciales = {
            "numero": self.objectos_pagina,
            "orden": self.orden,
            "ordenar_por": self.ordenar_por
        }

        context["order"] = OrderForm(initial=iniciales)

        return context



class LanzamientoDetailView(TemplateView):
    template_name = 'lanzamiento/detail.html'

    def get_context_data(self, **kwargs):

        nombrecorto = kwargs['nombrecorto']

        context = super().get_context_data(**kwargs)
        try:
            lanzamiento_object = Lanzamiento.objects.get(nombrecorto=nombrecorto)
            context['lanzamiento'] = lanzamiento_object
            context['blog'] = ENTRADA_BLOG
            return context
        except Exception as e:
            raise Http404(f"El lanzamiento con id {nombrecorto} no existe.")

class LanzamientoEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'lanzamiento/edit.html'
    form_class = LanzamientoForm
    model = Lanzamiento
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'

    def form_valid(self, form):

        logger.debug("Formulario válido, tratando de guardar las imagenes")
        nueva_entrada = form.save(commit=False)

        id_lanzamiento = nueva_entrada.id
        nombrecorto = nueva_entrada.nombrecorto

        nueva_entrada.fecha_modificacion = timezone.now()

        imagen = nueva_entrada.imagen

        old_entrada = Lanzamiento.objects.get(id=id_lanzamiento)

        post_request = self.request.POST.get

        try:
            if post_request('imagen') != '':
                logger.debug('La imagen es')
                logger.debug(imagen)
                old_file = old_entrada.imagen
                if old_file:
                    logger.debug("Borrando imagen antigua...")
                    old_nombre, old_extension = os.path.splitext(old_file.name)
                    old_ruta_thumbnail = MEDIA_ROOT + str(id_lanzamiento) + nombrecorto + 'image_small' + old_extension
                    old_ruta = MEDIA_ROOT + str(id_lanzamiento) + nombrecorto + 'image' + old_extension
                    old_file = Lanzamiento.objects.get(id=id_lanzamiento).imagen
                    logger.debug("Ruta imagen antigua: " + old_ruta)
                    logger.debug("Ruta thumbnail antigua: " + old_ruta_thumbnail)
                    if os.path.isfile(old_ruta):
                        try:
                            logger.debug("Tratando de eliminar " + old_ruta)
                            os.remove(old_ruta)
                            logger.debug("Exito!")
                        except OSError as e:
                            logger.error("Error borrando imagen! " + str(e))
                    if os.path.isfile(old_ruta_thumbnail):
                        try:
                            logger.debug("Tratando de eliminar " + old_ruta_thumbnail)
                            os.remove(old_ruta_thumbnail)
                            logger.debug("Exito!")
                        except OSError as e:
                            logger.error("Error borrando thumbnail! " + str(e))

                logger.debug("Guardando imagen...")
                output = BytesIO()
                output_thumbnail = BytesIO()
                nombre, extension = os.path.splitext(str(imagen))
                extension = extension.lower()
                filetype = extension[1:]
                if filetype == 'jpg':
                    filetype = 'jpeg'

                ruta = str(id_lanzamiento) + nombrecorto + 'image' + extension
                ruta_thumbnail = str(id_lanzamiento) + nombrecorto + 'image_small' + extension

                logger.debug("La ruta de la imagen es " + str(ruta))
                logger.debug("La ruta del thumbnail es " + str(ruta_thumbnail))

                im = Image.open(imagen)
                im.thumbnail(resize(800, im.size[0], im.size[1]))
                im.save(output, filetype)

                nueva_entrada.imagen = InMemoryUploadedFile(
                    output,
                    'FileField',
                    ruta,
                    'image/' + filetype,
                    sys.getsizeof(output),
                    None
                )

                im = Image.open(imagen)
                im.thumbnail(resize(200, im.size[0], im.size[1]))
                im.save(output_thumbnail, filetype)

                nueva_entrada.imagen_thumbnail = InMemoryUploadedFile(
                    output_thumbnail,
                    'FileField',
                    ruta_thumbnail,
                    'image/' + filetype,
                    sys.getsizeof(output_thumbnail),
                    None
                )
            else:
                logger.debug('El valor de image-clear')
                logger.debug(post_request('imagen-clear'))
                if post_request('imagen-clear') == 'on':
                    old_entrada.imagen.delete(False)
                    old_entrada.imagen_thumbnail.delete(False)

        except Exception as e:
            logger.error("Error subiendo los archivos!" + str(e))

        nueva_entrada.save()
        form.save_m2m()
        self.success_url = reverse('lanzamiento:detail', kwargs={
                                   'nombrecorto': nueva_entrada.nombrecorto})
        return super().form_valid(form)


class LanzamientoCreateView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'lanzamiento/edit.html'
    form_class = LanzamientoForm
    success_url = '/'    

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        try:
            id_lanzamiento = Lanzamiento.objects.latest('id').id + 1
        except:
            id_lanzamiento = 1
        
        nombrecorto = generar_nombrecorto(nueva_entrada.nombre, Lanzamiento)

        nueva_entrada.id = id_lanzamiento
        nueva_entrada.nombrecorto = nombrecorto

        nueva_entrada.fecha_creacion = timezone.now()
        nueva_entrada.fecha_modificacion = timezone.now()

        imagen = nueva_entrada.imagen

        if imagen:
            output = BytesIO()
            output_thumbnail = BytesIO()

            nombre, extension = os.path.splitext(str(imagen))

            extension = extension.lower()
            filetype = extension[1:]
            if filetype == 'jpg':
                filetype = 'jpeg'
            
            ruta = str(id_lanzamiento) + nombrecorto + 'image' + extension
            ruta_thumbnail = str(id_lanzamiento) + nombrecorto + 'image_small' + extension

            im = Image.open(imagen)
            im.thumbnail(resize(800, im.size[0], im.size[1]))
            im.save(output, filetype)

            nueva_entrada.imagen = InMemoryUploadedFile(
                output,
                'FileField',
                ruta,
                'image/' + filetype,
                sys.getsizeof(output),
                None
            )

            im = Image.open(imagen)
            im.thumbnail(resize(200, im.size[0], im.size[1]))
            im.save(output_thumbnail, filetype)

            nueva_entrada.imagen_thumbnail = InMemoryUploadedFile(
                output_thumbnail,
                'FileField',
                ruta_thumbnail,
                'image/' + filetype,
                sys.getsizeof(output_thumbnail),
                None
            )

        nueva_entrada.save()
        form.save_m2m()

        self.success_url = reverse('lanzamiento:detail', kwargs={
                                   'nombrecorto': nueva_entrada.nombrecorto})
        return super().form_valid(form)

class LanzamientoDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    template_name = 'lanzamiento/delete.html'
    model = Lanzamiento
    success_url = '/lanzamiento'
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'
