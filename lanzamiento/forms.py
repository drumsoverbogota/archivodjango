from django.forms import CharField
from django.forms import ChoiceField
from django.forms import Textarea
from django.forms import TextInput
from django.forms import Select

from django.forms import Form
from django.forms import ModelForm

from archivo.models import Lanzamiento

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
    class Meta:
        model = Lanzamiento
        exclude = [
            'nombrecorto',
            'fecha_creacion', 
            'fecha_modificacion', 
            'bandas',
            ]


class OrderForm(Form):

    numero = ChoiceField(label="Items a mostrar", choices=numero)
    ordenar_por = ChoiceField(label="Ordenar Por", choices=orden)
    orden = ChoiceField(label="Ascendente", choices=ascendente)
