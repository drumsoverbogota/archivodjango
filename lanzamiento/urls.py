from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'lanzamiento'

urlpatterns = [
    path('lanzamiento', views.LanzamientoIndexView.as_view(), name='index'),
    path('lanzamiento/create', views.LanzamientoCreateView.as_view(), name='create'),
    path('lanzamiento/<slug:nombrecorto>', views.LanzamientoDetailView.as_view(), name='detail'),
    path('lanzamiento/edit/<slug:nombrecorto>', views.LanzamientoEditView.as_view(), name='edit'),
    path('lanzamiento/delete/<slug:nombrecorto>', views.LanzamientoDeleteView.as_view(), name='delete'),
]
