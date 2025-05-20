# Custom template tag for splitting strings
# Place this in a file named 'custom_tags.py' inside your app's templatetags directory

from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split a string into a list on the given delimiter
    Usage: {{ 'Monday,Tuesday,Wednesday'|split:',' }}
    """
    return value.split(arg)