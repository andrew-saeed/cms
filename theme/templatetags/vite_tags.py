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
    """
    Returns all CSS files:
    - CSS mentioned in 'css' keys (e.g. for vendor or main.js)
    - Pure CSS entries (like 'src/style.css')
    """
    try:
        manifest = load_manifest()
        css_files = set()

        for k, v in manifest.items():
            # 1. CSS explicitly listed in the 'css' field
            for css in v.get("css", []):
                css_files.add(static(css))

            # 2. Direct CSS entry (like 'src/style.css')
            if k.endswith('.css') and v.get("file", "").endswith(".css"):
                css_files.add(static(v["file"]))

        return sorted(css_files)
    except Exception as e:
        return [f"<!-- Error loading CSS assets: {e} -->"]