from django.forms import ModelForm
from django.forms import Textarea
from django.forms import TextInput
from django.forms import CheckboxSelectMultiple

from archivo.models import Banda

class BandaForm(ModelForm):
    class Meta:
        model = Banda
        exclude = [
            'nombrecorto',
            'fecha_creacion', 
            'fecha_modificacion', 
            ]
        
        widgets = {
            'lanzamientos': CheckboxSelectMultiple(
                attrs={
                    "class": "column-checkbox"
                }
                ),
        }