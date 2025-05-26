from django import template
from datetime import datetime, timezone

register = template.Library()

@register.filter
def days_since(value):
    if not value:
        return ""
    now = datetime.now(timezone.utc)
    delta = now - value
    return f"{delta.days} days"