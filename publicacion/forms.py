from django.forms import ModelForm

from archivo.models import Publicacion

class PublicacionForm(ModelForm):
    class Meta:
        model = Publicacion
        exclude = [
            'nombrecorto',
            'fecha_creacion',
            'fecha_modificacion',
            'imagen_thumbnail',
            ]