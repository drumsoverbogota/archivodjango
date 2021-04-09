from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render

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
from archivo.models import resize
from archivo.models import Banda
from archivo.models import BandaLanzamiento
from archivo.models import Lanzamiento
from archivodjango.settings import MEDIA_ROOT

from .forms import LanzamientoForm
from .forms import OrderForm 

from io import BytesIO
from PIL import Image

import os
import sys

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
        lanzamiento_object = Lanzamiento.objects.get(nombrecorto=nombrecorto)
        context['lanzamiento'] = lanzamiento_object
        return context

class LanzamientoEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'lanzamiento/edit.html'
    form_class = LanzamientoForm
    model = Lanzamiento
    slug_field = 'nombrecorto'
    slug_url_kwarg = 'nombrecorto'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)

        id_lanzamiento = nueva_entrada.id
        nombrecorto = nueva_entrada.nombrecorto

        nueva_entrada.fecha_modificacion = timezone.now()

        imagen = nueva_entrada.imagen


        try:
            old_file = Lanzamiento.objects.get(id=id_lanzamiento).imagen
            if old_file and old_file != imagen:
                old_nombre, old_extension = os.path.splitext(old_file.name)
                old_ruta_thumbnail = MEDIA_ROOT + str(id_lanzamiento) + nombrecorto + 'image_small' + old_extension
                old_ruta = MEDIA_ROOT + str(id_lanzamiento) + nombrecorto + 'image' + old_extension
                old_file = Lanzamiento.objects.get(id=id_lanzamiento).imagen
                if os.path.isfile(old_ruta):
                    try:
                        os.remove(old_ruta)
                    except OSError as e:
                        print("Error borrando imagen! ", e)
                if os.path.isfile(old_ruta_thumbnail):
                    try:
                        os.remove(old_ruta_thumbnail)
                    except OSError as e:
                        print("Error borrando thumbnail! ", e)
            if imagen and old_file != imagen:
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

                    nueva_entrada.imagen = InMemoryUploadedFile(
                        output_thumbnail,
                        'FileField',
                        ruta_thumbnail,
                        'image/' + filetype,
                        sys.getsizeof(output_thumbnail),
                        None
                    )
        except Exception as e:
            print("Error subiendo los archivos!", e)

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
        id_lanzamiento = Lanzamiento.objects.latest('id').id + 1
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
            
            ruta = MEDIA_ROOT + str(id_lanzamiento) + nombrecorto + 'image' + extension
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
