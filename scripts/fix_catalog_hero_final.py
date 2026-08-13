from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "pronta-entrega.html", ROOT / "sob-encomenda.html"]
HERO_FILE = ROOT / "assets" / "hero" / "catalog-hero-final-1800.webp"

hero_b64 = base64.b64encode(HERO_FILE.read_bytes()).decode("ascii")
data_uri = f"data:image/webp;base64,{hero_b64}"

MEDIA_STYLE = '''<style id="catalog-hero-inline-v3">
@media (max-width: 768px) {
  [data-hero-inline-v3] { object-position: 64% center !important; }
  body[data-page="catalog"] .catalog-hero,
  body[data-page="catalog"] .catalog-hero--order { min-height: 260px !important; }
}
</style>'''

for page in PAGES:
    text = page.read_text(encoding="utf-8")

    # Remove every previous catalog-hero experiment so there is only one implementation.
    text = re.sub(r'<link rel="preload"[^>]*catalog-hero[^>]*>', '', text)
    text = re.sub(r'<style id="catalog-hero-inline-final">.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<style id="catalog-hero-inline-v3">.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<img class="catalog-hero-bg-final"[^>]*>', '', text)
    text = re.sub(r'<span class="catalog-hero-shade-final"[^>]*></span>', '', text)
    text = re.sub(r'<img[^>]*data-hero-inline-v3[^>]*>', '', text)
    text = re.sub(r'<span[^>]*data-hero-shade-v3[^>]*></span>', '', text)

    # Fresh stylesheet request; the photo itself no longer depends on any external asset request.
    text = re.sub(r'./assets/css/styles\.css\?v=[^\"\']+', './assets/css/styles.css?v=20260813-v3', text)

    # Normalize hero opening tag and make it its own stacking context.
    text = re.sub(
        r'<section class="(catalog-hero(?: catalog-hero--order)?)"(?: style="[^"]*")?>',
        r'<section class="\1" style="position:relative!important;overflow:hidden!important;min-height:320px!important;display:flex!important;align-items:center!important;background:#160d09!important;isolation:isolate!important;">',
        text,
        count=1,
    )

    img = (
        '<img data-hero-inline-v3 alt="" aria-hidden="true" '
        f'src="{data_uri}" '
        'style="position:absolute!important;inset:0!important;width:100%!important;height:100%!important;object-fit:cover!important;object-position:center center!important;display:block!important;visibility:visible!important;opacity:1!important;z-index:0!important;pointer-events:none!important;">'
        '<span data-hero-shade-v3 aria-hidden="true" '
        'style="position:absolute!important;inset:0!important;display:block!important;z-index:1!important;pointer-events:none!important;background:linear-gradient(90deg,rgba(8,6,4,.72) 0%,rgba(8,6,4,.46) 38%,rgba(8,6,4,.14) 68%,rgba(8,6,4,.02) 100%),linear-gradient(180deg,rgba(8,6,4,.08) 0%,rgba(8,6,4,.02) 50%,rgba(8,6,4,.22) 100%)!important;"></span>'
    )

    text = re.sub(
        r'(<section class="catalog-hero(?: catalog-hero--order)?"[^>]*>)',
        r'\1' + img,
        text,
        count=1,
    )

    # Keep text above the inline image and shade.
    text = re.sub(
        r'(<section class="catalog-hero(?: catalog-hero--order)?"[^>]*>.*?<span data-hero-shade-v3[^>]*></span>)<div class="container"(?: style="[^"]*")?>',
        r'\1<div class="container" style="position:relative!important;z-index:2!important;">',
        text,
        count=1,
        flags=re.S,
    )

    text = text.replace('</head>', MEDIA_STYLE + '</head>', 1)
    page.write_text(text, encoding="utf-8")
    print(f"patched {page.name} with inline hero ({len(hero_b64)} base64 chars)")
