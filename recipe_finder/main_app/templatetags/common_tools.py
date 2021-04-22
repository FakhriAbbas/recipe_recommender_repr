from django import template

register = template.Library()

@register.filter(name='range_filter')
def custom_range(value):
    return range(value)