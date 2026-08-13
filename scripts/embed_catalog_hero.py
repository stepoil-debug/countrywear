from pathlib import Path
import base64
import re

root = Path(__file__).resolve().parents[1]
hero = root / "assets/hero/catalog-hero-final-1800.webp"
image_data = base64.b64encode(hero.read_bytes()).decode("ascii")

style_block = '''<style id="catalog-hero-embedded-style">
body[data-page="catalog"] .catalog-hero,
body[data-page="catalog"] .catalog-hero--order {
  position: relative !important;
  overflow: hidden !important;
  min-height: 320px !important;
  display: flex !important;
  align-items: center !important;
  background-color: #1a0f0b !important;
}
body[data-page="catalog"] .catalog-hero::before,
body[data-page="catalog"] .catalog-hero::after,
body[data-page="catalog"] .catalog-hero--order::before,
body[data-page="catalog"] .catalog-hero--order::after {
  content: none !important;
  display: none !important;
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
}
</style>'''

gradient = (
    "linear-gradient(90deg,rgba(8,6,4,.64) 0%,rgba(8,6,4,.38) 34%,"
    "rgba(8,6,4,.08) 66%,rgba(8,6,4,.01) 100%),"
    "linear-gradient(180deg,rgba(8,6,4,.05) 0%,rgba(8,6,4,.01) 48%,"
    "rgba(8,6,4,.16) 100%),"
)
background = gradient + f"url(data:image/webp;base64,{image_data})"

for name in ("pronta-entrega.html", "sob-encomenda.html"):
    page = root / name
    text = page.read_text(encoding="utf-8")

    text = re.sub(r'<style id="catalog-hero-inline-final">.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<style id="catalog-hero-embedded-style">.*?</style>', '', text, flags=re.S)
    text = re.sub(r'<link rel="preload" as="image" href="\./assets/hero/catalog-hero-final-1800\.webp[^>]*>', '', text)
    text = re.sub(r'<img class="catalog-hero-bg-final"[^>]*><span class="catalog-hero-shade-final"[^>]*></span>', '', text)
    text = re.sub(r'./assets/css/styles\.css\?v=[^\"\']+', './assets/css/styles.css?v=20260813-final6', text)
    text = text.replace('</head>', style_block + '</head>', 1)

    def repl(match):
        classes = match.group(1)
        return (
            f'<section class="{classes}" '
            f'style="background-image:{background} !important;'
            'background-size:cover !important;'
            'background-position:center center !important;'
            'background-repeat:no-repeat !important;'
            'background-color:#1a0f0b !important;">'
        )

    text = re.sub(
        r'<section class="(catalog-hero(?: catalog-hero--order)?)"(?: style="[^"]*")?>',
        repl,
        text,
        count=1,
    )
    page.write_text(text, encoding="utf-8")
    print(name)
