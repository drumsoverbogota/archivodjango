from django import forms

from django.forms import ModelForm

from conciertos.models import Conciertos

class DateInput(forms.DateInput):
    input_type = 'date'


class ConciertosForm(ModelForm):
    class Meta:
        model = Conciertos
        exclude = [
            'nombrecorto',
            'fecha_creacion',
            'fecha_modificacion',
            'imagen_thumbnail',
            ]
        widgets = {
            'fecha_grabacion': DateInput(
                format=('%Y-%m-%d'),
            ),
        }
