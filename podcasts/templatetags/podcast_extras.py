from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def format_duration(value):
    return ":".join(str(value).split(":")[:2])
