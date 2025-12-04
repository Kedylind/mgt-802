"""
Custom template filters for the case interview simulator.
"""
from django import template
import json

register = template.Library()


@register.filter
def pprint(value):
    """Pretty print JSON data."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)

