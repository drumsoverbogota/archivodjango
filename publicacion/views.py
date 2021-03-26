from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import TemplateView

from django.utils import timezone
from django.urls import reverse

from django.shortcuts import render
# Create your views here.

from archivo.models import generar_nombrecorto
from archivo.models import resize
from archivo.models import Publicacion
from archivodjango.settings import MEDIA_ROOT
from .forms import PublicacionForm

from io import BytesIO
from PIL import Image

import os
import sys

class PublicacionDetailView(TemplateView):
    template_name = 'publicacion/detail.html'

    def get_context_data(self, **kwargs):

        nombrecorto = kwargs['nombrecorto']

        context = super().get_context_data(**kwargs)
        publicacion_object = Publicacion.objects.get(nombrecorto=nombrecorto)
        context['publicacion'] = publicacion_object

        return context

class PublicacionEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'publicacion/edit.html'
    form_class = PublicacionForm
    model = Publicacion
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'

    def form_valid(self, form):
        print(form)
        nueva_entrada = form.save(commit=False)

        id_publicacion = nueva_entrada.id
        nombrecorto = nueva_entrada.nombrecorto

        nueva_entrada.fecha_modificacion = timezone.now()

        imagen = nueva_entrada.imagen
        print(imagen)        

        try:
            old_file = Publicacion.objects.get(id=id_publicacion).imagen
            if old_file and old_file != imagen:
                old_nombre, old_extension = old_file.name.split('.')
                old_ruta_thumbnail = MEDIA_ROOT + str(id_publicacion) + nombrecorto + 'image_small.' + old_extension
                old_ruta = MEDIA_ROOT + str(id_publicacion) + nombrecorto + 'image.' + old_extension
                old_file = Publicacion.objects.get(id=id_publicacion).imagen
                if os.path.isfile(old_ruta):
                    os.remove(old_ruta)
                if os.path.isfile(old_ruta_thumbnail):
                    os.remove(old_ruta_thumbnail)

            if imagen and old_file != imagen:
                output = BytesIO()

                nombre, extension = str(imagen).split('.')

                extension = extension.lower()
                filetype = extension
                if filetype == 'jpg':
                    filetype = 'jpeg'
                
                ruta_thumbnail = MEDIA_ROOT + str(id_publicacion) + nombrecorto + 'image_small.' + extension
                ruta = MEDIA_ROOT + str(id_publicacion) + nombrecorto + 'image.' + extension

                im = Image.open(imagen)
                im.thumbnail(resize(400, im.size[0], im.size[1]))
                im.save(ruta_thumbnail)

                im = Image.open(imagen)
                im.thumbnail(resize(800, im.size[0], im.size[1]))
                im.save(output, filetype)

                imagen = InMemoryUploadedFile(
                    output,
                    'FileField',
                    ruta,
                    'image/' + filetype,
                    sys.getsizeof(output),
                    None
                )

        except Exception as e:
            print("No existe el archivo!", e)

        nueva_entrada.save()
        form.save_m2m()

        self.success_url = reverse('publicacion:detail', kwargs={
                                   'nombrecorto': nueva_entrada.nombrecorto})
        return super().form_valid(form)

class PublicacionDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    template_name = 'publicacion/delete.html'
    model = Publicacion
    success_url = '/publicacion'
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'

class PublicacionCreateView(LoginRequiredMixin, FormView):
    login_url = '/login'
    template_name = 'publicacion/edit.html'
    form_class = PublicacionForm
    success_url = '/'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)

        id_publicacion = Publicacion.objects.latest('id').id + 1
        nombrecorto = generar_nombrecorto(nueva_entrada.nombre, Publicacion)

        nueva_entrada.id = id_publicacion
        nueva_entrada.nombrecorto = nombrecorto

        nueva_entrada.fecha_creacion = timezone.now()
        nueva_entrada.fecha_modificacion = timezone.now()

        imagen = nueva_entrada.imagen

        if imagen:
            output = BytesIO()

            nombre, extension = str(imagen).split('.')

            extension = extension.lower()
            filetype = extension
            if filetype == 'jpg':
                filetype = 'jpeg'
            
            ruta_thumbnail = MEDIA_ROOT + str(id_publicacion) + nombrecorto + 'image_small.' + extension
            ruta = MEDIA_ROOT + str(id_publicacion) + nombrecorto + 'image.' + extension

            im = Image.open(imagen)
            im.thumbnail(resize(200, im.size[0], im.size[1]))
            im.save(ruta_thumbnail)

            im = Image.open(imagen)
            im.thumbnail(resize(800, im.size[0], im.size[1]))
            im.save(output, filetype)

            imagen = InMemoryUploadedFile(
                output,
                'FileField',
                ruta,
                'image/' + filetype,
                sys.getsizeof(output),
                None
            )

        nueva_entrada.save()
        form.save_m2m()

        self.success_url = reverse('publicacion:detail', kwargs={
                                   'nombrecorto': nueva_entrada.nombrecorto})
        return super().form_valid(form)

class PublicacionIndexView(ListView):
    template_name = 'publicacion/index.html'
    context_object_name = 'publicaciones'
    no_visibles = False

    def get_queryset(self):
        get_request = self.request.GET.get

        if get_request("no_visible") == "true":
            self.no_visibles = True

        filtros = {}

        if not self.no_visibles:
            filtros['visible'] = True

        return Publicacion.objects.filter(**filtros).order_by('nombre').order_by('numero')