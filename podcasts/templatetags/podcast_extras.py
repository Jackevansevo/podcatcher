from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def format_duration(value):
    hours, minutes, seconds = map(int, value.split(":"))
    if bool(hours):
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
