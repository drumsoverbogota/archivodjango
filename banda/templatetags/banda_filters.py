from django import template

register = template.Library()

@register.filter
def add_suffix(url):
    return url.replace(".", "_small.")

@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return value
