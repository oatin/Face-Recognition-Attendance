from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def subtract(value, arg):
    return int(value) - int(arg)