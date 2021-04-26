from django.forms import CharField
from django.forms import ChoiceField
from django.forms import Textarea
from django.forms import TextInput
from django.forms import Select
from django.forms import CheckboxSelectMultiple
from django.forms import TypedChoiceField

from django.forms import Form
from django.forms import ModelForm

from archivo.models import Lanzamiento

from archivo.models import FORMATOS


ascendente = [
    ("ascendente", "Sí"),
    ("descendente", "No")
]

orden = [
    ("nombre", "Nombre"),
    ("anho", "Año"),
    ("formato", "Formato"),
    ("referencia", "Referencia"),
]

numero = []

for i in range(10, 101, 10):
    valor = str(i)
    numero.append((valor, valor))


class LanzamientoForm(ModelForm):

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})

        instance = kwargs.get('instance', None)
        
        if instance:
            for id, formato in FORMATOS:
                if formato == instance.formato:
                    initial['formato'] = id
        else:
            initial['formato'] = 1
        kwargs['initial'] = initial
        super(LanzamientoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Lanzamiento
        exclude = [
            'imagen_thumbnail',
            'nombrecorto',
            'fecha_creacion', 
            'fecha_modificacion', 
            ]

        widgets = {
            'bandas': CheckboxSelectMultiple(
                attrs={
                    "class": "column-checkbox"
                }
                ),
        }

class OrderForm(Form):

    numero = ChoiceField(label="Items a mostrar", choices=numero)
    ordenar_por = ChoiceField(label="Ordenar Por", choices=orden)
    orden = ChoiceField(label="Ascendente", choices=ascendente)
