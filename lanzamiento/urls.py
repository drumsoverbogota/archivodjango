from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'lanzamiento'

urlpatterns = [
    path('grabaciones', views.LanzamientoIndexView.as_view(), name='index'),
    path('grabaciones/create', views.LanzamientoCreateView.as_view(), name='create'),
    path('grabaciones/<slug:nombrecorto>', views.LanzamientoDetailView.as_view(), name='detail'),
    path('grabaciones/edit/<slug:nombrecorto>', views.LanzamientoEditView.as_view(), name='edit'),
    path('grabaciones/delete/<slug:nombrecorto>', views.LanzamientoDeleteView.as_view(), name='delete'),
    #Estos se deja para propositos de "legacy"
    path('lanzamiento', views.LanzamientoIndexView.as_view(), name='oldindex'),
    path('lanzamiento/create', views.LanzamientoCreateView.as_view(), name='oldcreate'),
    path('lanzamiento/<slug:nombrecorto>', views.LanzamientoDetailView.as_view(), name='olddetail'),
    path('lanzamiento/edit/<slug:nombrecorto>', views.LanzamientoEditView.as_view(), name='oldedit'),
    path('lanzamiento/delete/<slug:nombrecorto>', views.LanzamientoDeleteView.as_view(), name='olddelete'),
]
