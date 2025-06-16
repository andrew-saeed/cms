from django import template
from datetime import datetime, timezone

register = template.Library()

@register.filter
def days_since(value):
    if not value:
        return ""
    
    now = datetime.now(timezone.utc)
    delta = now - value

    if delta.days <= 0:
        return 'today'
    else:
        return f"{delta.days} days"