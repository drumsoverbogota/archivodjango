from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'banda'

urlpatterns = [
    path('', views.BandaIndexView.as_view(), name='index'),
    path('create', views.BandaCreateView.as_view(), name='create'),
    path('<slug:nombrecorto>', views.BandaDetailView.as_view(), name='detail'),
    path('edit/<slug:nombrecorto>', views.BandaEditView.as_view(), name='edit'),
    path('delete/<slug:nombrecorto>', views.BandaDeleteView.as_view(), name='delete'),
]
