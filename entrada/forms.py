from django.forms import ModelForm
from django.forms import Textarea
from django.forms import TextInput

from .models import Entrada

class CreateEntradaForm(ModelForm):
    class Meta:
        model = Entrada
        exclude = ['fecha', 'resumen']
        widgets = {
            'titulo': TextInput(attrs={'size': 50,'maxlength': 100}),
            'contenido': Textarea(attrs={'cols': 80, 'rows': 20}),
        }