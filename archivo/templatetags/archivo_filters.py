from django import template

register = template.Library()

@register.filter
def mostrar_bandas(banda):
    if len(banda) > 1:
        return 'V.A.'
    else:
        return banda[0].nombre
    
