from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'conciertos'

urlpatterns = [
    path('', views.ConciertosIndexView.as_view(), name='index'),
    path('create', views.ConciertosCreateView.as_view(), name='create'),
    path('<slug:nombrecorto>', views.ConciertosDetailView.as_view(), name='detail'),
    path('edit/<slug:nombrecorto>', views.ConciertosEditView.as_view(), name='edit'),
    path('delete/<slug:nombrecorto>', views.ConciertosDeleteView.as_view(), name='delete'),
]
