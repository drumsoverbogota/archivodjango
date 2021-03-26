from django.shortcuts import render

from django.db.models import Q

from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import TemplateView

from entrada.models import Entrada
from archivo.models import Banda
from archivo.models import Lanzamiento
from archivo.models import Publicacion

class IndexView(ListView):
    template_name = 'archivo/index.html'
    context_object_name = 'ultimas_entradas_list'
    paginate_by = 5

    def get_queryset(self):
        return Entrada.objects.filter(tipo='noticia').order_by('-fecha')


class AboutView(TemplateView):
    template_name = 'archivo/about.html'

class AdminView(TemplateView):
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

        context["peticion"] = peticion
        context["bandas"] = bandas
        context["lanzamientos"] = lanzamientos
        context["publicaciones"] = publicaciones
        
        return context 