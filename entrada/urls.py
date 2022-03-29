from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'entrada'

urlpatterns = [
    path('create', views.EntradaCreateView.as_view(), name='create'),
    path('<int:pk>', views.EntradaDetailView.as_view(), name='detail'),    
    path('edit/<int:pk>', views.EntradaEditView.as_view(), name='edit'),
    path('delete/<int:pk>', views.EntradaDeleteView.as_view(), name='delete')  
]
