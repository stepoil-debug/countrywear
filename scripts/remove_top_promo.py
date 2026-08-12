from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# Remove a barra promocional completa de todas as páginas públicas da loja.
# O painel administrativo fica fora desta rotina.
paths = list(ROOT.glob("*.html")) + list((ROOT / "produtos").glob("*.html"))

pattern = re.compile(
    r'<div\s+class=["\']promo-bar["\'][^>]*>\s*'
    r'<div\s+class=["\']container\s+promo-inner["\'][^>]*>.*?</div>\s*'
    r'</div>\s*',
    re.IGNORECASE | re.DOTALL,
)

updated = []
for path in paths:
    if not path.exists():
        continue
    content = path.read_text(encoding="utf-8")
    new_content, count = pattern.subn("", content)
    if count:
        path.write_text(new_content, encoding="utf-8")
        updated.append(path.relative_to(ROOT).as_posix())

print("Promo bar removed from:", ", ".join(updated) if updated else "no matching pages")
