from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "pronta-entrega.html", ROOT / "sob-encomenda.html"]

STYLE = '''<style id="catalog-hero-inline-final">
body[data-page="catalog"] .catalog-hero,
body[data-page="catalog"] .catalog-hero--order {
  position: relative !important;
  overflow: hidden !important;
  min-height: 320px !important;
  display: flex !important;
  align-items: center !important;
  background: #1a0f0b !important;
}
body[data-page="catalog"] .catalog-hero::before,
body[data-page="catalog"] .catalog-hero::after,
body[data-page="catalog"] .catalog-hero--order::before,
body[data-page="catalog"] .catalog-hero--order::after {
  content: none !important;
  display: none !important;
}
body[data-page="catalog"] .catalog-hero .catalog-hero-bg-final,
body[data-page="catalog"] .catalog-hero--order .catalog-hero-bg-final {
  position: absolute !important;
  inset: 0 !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  object-position: center center !important;
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
  z-index: 0 !important;
}
body[data-page="catalog"] .catalog-hero .catalog-hero-shade-final,
body[data-page="catalog"] .catalog-hero--order .catalog-hero-shade-final {
  position: absolute !important;
  inset: 0 !important;
  z-index: 1 !important;
  pointer-events: none !important;
  background:
    linear-gradient(90deg, rgba(8,6,4,.74) 0%, rgba(8,6,4,.48) 34%, rgba(8,6,4,.14) 66%, rgba(8,6,4,.02) 100%),
    linear-gradient(180deg, rgba(8,6,4,.08) 0%, rgba(8,6,4,.02) 48%, rgba(8,6,4,.24) 100%) !important;
}
body[data-page="catalog"] .catalog-hero > .container,
body[data-page="catalog"] .catalog-hero--order > .container {
  position: relative !important;
  z-index: 2 !important;
}
@media (max-width: 768px) {
  body[data-page="catalog"] .catalog-hero,
  body[data-page="catalog"] .catalog-hero--order {
    min-height: 260px !important;
  }
  body[data-page="catalog"] .catalog-hero .catalog-hero-bg-final,
  body[data-page="catalog"] .catalog-hero--order .catalog-hero-bg-final {
    object-position: 64% center !important;
  }
}
</style>'''

PRELOAD = '<link rel="preload" as="image" href="./assets/hero/catalog-hero-final-1800.webp?v=20260813-final">'
IMG = '<img class="catalog-hero-bg-final" src="./assets/hero/catalog-hero-final-1800.webp?v=20260813-final" alt="" loading="eager" fetchpriority="high" decoding="async" onerror="this.onerror=null;this.src=\'./assets/hero/pronta-entrega-horse.webp?v=20260813-final\';"><span class="catalog-hero-shade-final" aria-hidden="true"></span>'

for page in PAGES:
    text = page.read_text(encoding="utf-8")

    # Force a fresh stylesheet request while keeping the hero independent from external CSS.
    text = re.sub(r'./assets/css/styles\.css\?v=[^\"\']+', './assets/css/styles.css?v=20260813-final4', text)

    if 'id="catalog-hero-inline-final"' not in text:
        text = text.replace('</head>', PRELOAD + STYLE + '</head>', 1)

    # Remove any prior direct hero elements before installing exactly one final pair.
    text = re.sub(r'<img class="catalog-hero-bg-final"[^>]*><span class="catalog-hero-shade-final"[^>]*></span>', '', text)
    text = re.sub(r'(<section class="catalog-hero(?: catalog-hero--order)?">)', r'\1' + IMG, text, count=1)

    page.write_text(text, encoding="utf-8")
    print(f"patched {page.name}")
