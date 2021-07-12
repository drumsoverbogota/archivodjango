from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render

# Create your views here.

from django.http import Http404

from django.utils import timezone

from django.views.generic import DetailView
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView
from django.urls import reverse

from archivo.models import generar_nombrecorto
from archivo.models import resize
from archivo.models import Banda
from archivo.models import Lanzamiento
from archivodjango.settings import MEDIA_ROOT

from .forms import BandaForm

from io import BytesIO
from PIL import Image

import logging
import os
import sys

logger = logging.getLogger(__name__)

class BandaIndexView(ListView):
    template_name = 'banda/index.html'
    context_object_name = 'bandas'

    extranjera = False

    def get_queryset(self):

        get_request = self.request.GET.get

        if get_request("extranjera") == "true":
            self.extranjera = True

        filtros = {}
        if not self.extranjera:
            filtros['extranjera'] = False

        return Banda.objects.filter(**filtros).order_by("nombre")

class BandaDetailView(TemplateView):
    template_name = 'banda/detail.html'

    def get_context_data(self, **kwargs):

        nombrecorto = kwargs['nombrecorto']

        context = super().get_context_data(**kwargs)
        
        try:
            banda_object = Banda.objects.get(nombrecorto=nombrecorto)
            context['banda'] = banda_object

            nodisponible = False
            for banda in banda_object.lanzamientos.all():
                if not banda.disponible:
                    nodisponible = True

            context['nodisponible'] = nodisponible

            return context
        except Exception as e:
            raise Http404(f"La banda con id {nombrecorto} no existe.")


class BandaEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'banda/edit.html'
    form_class = BandaForm
    model = Banda
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)

        id_banda = nueva_entrada.id
        nombrecorto = nueva_entrada.nombrecorto

        nueva_entrada.fecha_modificacion = timezone.now()

        imagen = nueva_entrada.imagen

        old_entrada = Banda.objects.get(id=id_banda)

        post_request = self.request.POST.get

        try:
            if post_request('imagen') != '':
                logger.debug('La imagen es')
                logger.debug(imagen)
                old_file = old_entrada.imagen
                if old_file:
                    logger.debug("Borrando imagen antigua...")
                    old_nombre, old_extension = os.path.splitext(old_file.name)
                    old_ruta_thumbnail = MEDIA_ROOT + str(id_banda) + nombrecorto + 'image_small' + old_extension
                    old_ruta = MEDIA_ROOT + str(id_banda) + nombrecorto + 'image' + old_extension
                    old_file = Banda.objects.get(id=id_banda).imagen
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
                
                ruta_thumbnail = str(id_banda) + nombrecorto + 'image_small' + extension
                ruta = str(id_banda) + nombrecorto + 'image' + extension

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
        self.success_url = reverse('banda:detail', kwargs={
                                   'nombrecorto': nueva_entrada.nombrecorto})
        return super().form_valid(form)


class BandaCreateView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'banda/edit.html'
    form_class = BandaForm
    success_url = '/'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)

        id_banda = Banda.objects.latest('id').id + 1
        nombrecorto = generar_nombrecorto(nueva_entrada.nombre, Banda)

        nueva_entrada.id = id_banda
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
            
            ruta = str(id_banda) + nombrecorto + 'image' + extension
            ruta_thumbnail = str(id_banda) + nombrecorto + 'image_small' + extension

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

        self.success_url = reverse('banda:detail', kwargs={
                                   'nombrecorto': nueva_entrada.nombrecorto})
        return super().form_valid(form)

class BandaDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    template_name = 'banda/delete.html'
    model = Banda
    success_url = '/banda'
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'
