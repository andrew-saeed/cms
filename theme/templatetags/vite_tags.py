import json
from django.conf import settings
from django.templatetags.static import static
from django import template

register = template.Library()
manifest_file = settings.BASE_DIR / 'static' / 'manifest.json'

def load_manifest():
    with open(manifest_file) as f:
        return json.load(f)
    
@register.simple_tag
def vite_all_js():
    """Return all JS files including entry + imports like vendor chunks."""
    try:
        manifest = load_manifest()
        collected = set()

        def collect_js(key):
            entry = manifest.get(key)
            if not entry:
                return
            js_file = entry.get("file")
            if js_file and js_file.endswith(".js"):
                collected.add(static(js_file))
            for imported in entry.get("imports", []):
                collect_js(imported)

        for k, v in manifest.items():
            if v.get("isEntry"):
                collect_js(k)

        return sorted(collected)
    except Exception as e:
        return [f"<!-- Error loading JS assets: {e} -->"]
    
@register.simple_tag
def vite_all_css():
    """Returns a set of all CSS file URLs (even shared in vendor)."""
    try:
        manifest = load_manifest()
        css_files = set()
        for v in manifest.values():
            for css in v.get("css", []):
                css_files.add(static(css))
        return sorted(css_files)
    except Exception as e:
        return [f"<!-- Error loading CSS assets: {e} -->"]