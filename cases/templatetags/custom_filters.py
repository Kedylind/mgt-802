"""
Custom template filters for the case interview simulator.
"""
from django import template
import json
import math

register = template.Library()


@register.filter
def pprint(value):
    """Pretty print JSON data."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)


@register.filter
def get_item(list_obj, index):
    """Get item from list by index."""
    try:
        return list_obj[index]
    except (IndexError, TypeError, KeyError):
        return None


@register.filter
def max_value(values):
    """Get maximum value from list."""
    try:
        return max(values)
    except (ValueError, TypeError):
        return 1


@register.filter
def pie_angle(index, values):
    """Calculate SVG path coordinates for pie chart slices."""
    total = sum(values)
    percentages = [v / total for v in values]
    
    # Calculate cumulative angle
    cumulative = sum(percentages[:index])
    start_angle = cumulative * 360
    end_angle = (cumulative + percentages[index]) * 360
    
    # Convert to radians
    start_rad = math.radians(start_angle - 90)
    end_rad = math.radians(end_angle - 90)
    
    # Calculate points on circle (radius 90, center 100,100)
    x1 = 100 + 90 * math.cos(start_rad)
    y1 = 100 + 90 * math.sin(start_rad)
    x2 = 100 + 90 * math.cos(end_rad)
    y2 = 100 + 90 * math.sin(end_rad)
    
    # Large arc flag if angle > 180 degrees
    large = 1 if (end_angle - start_angle) > 180 else 0
    
    return {
        'x1': round(x1, 2),
        'y1': round(y1, 2),
        'x2': round(x2, 2),
        'y2': round(y2, 2),
        'large': large
    }

