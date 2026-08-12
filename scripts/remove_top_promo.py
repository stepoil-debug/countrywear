from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "index.html"

if path.exists():
    content = path.read_text(encoding="utf-8")
    content = content.replace('<span>✦ Frete grátis para todo o Brasil em compras acima de R$ 399,90</span>', '')
    path.write_text(content, encoding="utf-8")

print("Top free-shipping promo removed from storefront")
