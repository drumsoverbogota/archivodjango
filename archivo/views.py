from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from django.db.models import Q

from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import TemplateView

from entrada.models import Entrada
from conciertos.models import Conciertos
from archivo.models import Banda
from archivo.models import Lanzamiento
from archivo.models import Publicacion

class IndexView(ListView):
    template_name = 'archivo/index.html'
    context_object_name = 'ultimas_entradas_list'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actualizaciones"] = Lanzamiento.objects.filter(
            disponible=True,
            visible=True
        ).order_by('-fecha_modificacion')[:5]
        return context

    def get_queryset(self):
        return Entrada.objects.filter(tipo='noticia').order_by('-fecha')

class ListaView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'archivo/lista.html'
    def get_context_data(self, **kwargs):

        get_request = self.request.GET.get
        context = super().get_context_data(**kwargs)
        context["lanzamientos"] = Lanzamiento.objects.all().order_by('indice_referencia')
        context["publicaciones"] = Publicacion.objects.all()
        return context

class FaltantesView(TemplateView):
    template_name = 'archivo/faltantes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lanzamientos"] = Lanzamiento.objects.filter(
            Q(portadas=False) |
            Q(disco_digitalizado=False)
        ).filter(
            disponible=True,
            visible=True
        ).order_by('indice_referencia')
        context["no_disponibles"] = Lanzamiento.objects.filter(
            disponible=False, 
            visible=True
        ).order_by('indice_referencia')
        return context

class AboutView(TemplateView):
    template_name = 'archivo/about.html'

class AdminView(LoginRequiredMixin, TemplateView):
    template_name = 'archivo/admin.html'

class ContactView(TemplateView):
    template_name = 'archivo/contact.html'

class BuscarView(TemplateView):
    template_name = 'archivo/buscar.html'

    def get_context_data(self, **kwargs):

        get_request = self.request.GET.get
        
        context = super().get_context_data(**kwargs)

        peticion = get_request("peticion", "")
        bandas = Banda.objects.filter(
            Q(nombre__icontains=peticion) | 
            Q(otros__icontains=peticion) | 
            Q(integrantes__icontains=peticion) | 
            Q(comentarios__icontains=peticion)
        )

        lanzamientos = Lanzamiento.objects.filter(
            Q(visible=True) &
            Q(nombre__icontains=peticion) | 
            Q(referencia__icontains=peticion) | 
            Q(anho__icontains=peticion) | 
            Q(tracklist__icontains=peticion) | 
            Q(creditos__icontains=peticion) | 
            Q(notas__icontains=peticion) | 
            Q(indice_referencia__icontains=peticion) 
        )

        publicaciones = Publicacion.objects.filter(
            Q(visible=True) &
            Q(nombre__icontains=peticion) | 
            Q(fecha__icontains=peticion) | 
            Q(notas__icontains=peticion) | 
            Q(indice_referencia__icontains=peticion) 
        )

        conciertos = Conciertos.objects.filter(
            Q(visible=True) &
            Q(nombre__icontains=peticion) |
            Q(notas__icontains=peticion)
        )

        context["peticion"] = peticion
        context["bandas"] = bandas
        context["lanzamientos"] = lanzamientos
        context["publicaciones"] = publicaciones
        context["conciertos"] = conciertos
        
        return context 
