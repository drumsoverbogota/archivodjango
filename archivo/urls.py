from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views
from entrada.views import BlogIndexView

app_name = 'archivo'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about', views.AboutView.as_view(), name='about'),
    path('admin_page', views.AdminView.as_view(), name='admin'),
    path('blog', BlogIndexView.as_view(), name='blog'),
    path('contact', views.ContactView.as_view(), name='contact'),
    path('buscar', views.BuscarView.as_view(), name='buscar'),
    path('lista', views.ListaView.as_view(), name='lista'),
    path('faltantes', views.FaltantesView.as_view(), name='faltantes'),
]
