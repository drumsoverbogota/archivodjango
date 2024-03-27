from django.urls import include, path
from rest_framework import routers

from django.urls import path

from archivodjango import settings

from . import views

app_name = 'apis'

router = routers.DefaultRouter()
router.register(r'conciertos', views.ConciertosViewSet)
router.register(r'lanzamientos', views.LanzamientosViewSet)
router.register(r'bandas', views.BandaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
