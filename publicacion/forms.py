from django.forms import CharField
from django.forms import ChoiceField
from django.forms import Textarea
from django.forms import TextInput
from django.forms import Select

from django.forms import Form
from django.forms import ModelForm

from archivo.models import Publicacion

class PublicacionForm(ModelForm):
    class Meta:
        model = Publicacion
        exclude = [
            'nombrecorto',
            'fecha_creacion',
            'fecha_modificacion'
            ]
