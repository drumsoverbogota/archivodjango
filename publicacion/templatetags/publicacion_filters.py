from django import template

register = template.Library()

@register.filter
def add_suffix(url):
    return url.replace(".", "_small.")
