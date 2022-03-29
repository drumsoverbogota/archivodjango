from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'publicacion'

urlpatterns = [
    path('', views.PublicacionIndexView.as_view(), name='index'),
    path('create', views.PublicacionCreateView.as_view(), name='create'),
    path('<slug:nombrecorto>', views.PublicacionDetailView.as_view(), name='detail'),
    path('edit/<slug:nombrecorto>', views.PublicacionEditView.as_view(), name='edit'),
    path('delete/<slug:nombrecorto>', views.PublicacionDeleteView.as_view(), name='delete'),
]
