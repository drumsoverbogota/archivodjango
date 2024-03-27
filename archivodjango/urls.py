"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import settings

urlpatterns = [
    path('', include('archivo.urls', namespace='archivo')),
    path('', include('login.urls', namespace='login')),
    path('', include('lanzamiento.urls', namespace='lanzamiento')),
    path('banda/', include('banda.urls', namespace='banda')),
    path('apis/', include('apis.urls', namespace='apis')),
    path('conciertos/', include('conciertos.urls', namespace='conciertos')),
    path('entrada/', include('entrada.urls', namespace='entrada')),
    path('publicacion/', include('publicacion.urls', namespace='publicacion')),
    path('admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)