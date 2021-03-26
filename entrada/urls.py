from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'entrada'

urlpatterns = [
    path('entrada/edit/<int:pk>', views.EntradaEditView.as_view(), name='edit'),
    path('entrada/delete/<int:pk>', views.DeleteEntradaView.as_view(), name='delete'),
    path('entrada/<int:pk>', views.EntradaDetailView.as_view(), name='detail'),
    path('entrada/create', views.EntradaCreateView.as_view(), name='create'),
]
