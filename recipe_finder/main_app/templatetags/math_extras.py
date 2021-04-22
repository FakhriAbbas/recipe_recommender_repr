from django import template

register = template.Library()


# https://www.canada.ca/en/health-canada/services/understanding-food-labels/percent-daily-value.html
@register.filter(name='division_dv')
def division_dv(value,arg):
    if value is None:
        return 0
    elif value is '':
        return 0
    elif arg is None:
        return 0
    arg = float(str(arg))
    value = float(str(value))
    result = (value / arg) * 100

    if result >= 100:
        return 100
    return int(result)

@register.filter(name='division')
def division_dv(value,arg):
    if value is None:
        return 0
    elif value is '':
        return 0
    elif arg is None:
        return 0
    arg = float(str(arg))
    value = float(str(value))
    result = (value / arg) * 100

    return int(result)