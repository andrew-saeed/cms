import json
from django.conf import settings
from django.templatetags.static import static
from django import template

register = template.Library()
manifest_file = settings.BASE_DIR / 'static' / 'manifest.json'

@register.simple_tag
def vite_asset(asset_path):
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
        file_path = manifest[asset_path]['file']
        return static(f"{file_path}")
    except Exception as e:
        # Log the error or raise an exception as needed.
        return f"<!-- Error loading asset: {e} -->"

@register.simple_tag
def vite_css_vendors():
    try:
        with open(manifest_file) as f:
            manifest = json.load(f)
        return list(map(static, manifest['src/main.js']['css']))
    except Exception as e:
        # Log the error or raise an exception as needed.
        return f"<!-- Error loading asset: {e} -->"