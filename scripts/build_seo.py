from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
SEO = json.loads((ROOT / "data/seo.json").read_text(encoding="utf-8"))
SITE = SEO["siteUrl"].rstrip("/")
STORE = SETTINGS.get("storeName", "LR Country Wear")
PHONE = re.sub(r"\D", "", SETTINGS.get("whatsapp", ""))
INSTAGRAM = SETTINGS.get("instagram", "https://www.instagram.com/lr_countrywear/")
TODAY = date.today().isoformat()


def abs_url(path: str = "") -> str:
    if not path:
        return SITE + "/"
    return SITE + "/" + path.lstrip("/")


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def json_script(data) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


def head_block(title: str, description: str, path: str, schema, image: str | None = None) -> str:
    canonical = abs_url(path)
    image_url = abs_url((image or SEO.get("defaultImage", "assets/instagram/post-1.jpg")).lstrip("/"))
    return f'''<!-- SEO:START -->
<meta name="description" content="{esc(description)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{canonical}">
<meta property="og:locale" content="pt_BR">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(STORE)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{image_url}">
{json_script(schema)}
<!-- SEO:END -->'''


def inject_head(path: Path, title: str, description: str, url_path: str, schema, image: str | None = None):
    content = path.read_text(encoding="utf-8")
    content = re.sub(r'\s*<meta\s+name="description"[^>]*>', "", content, flags=re.I)
    content = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', content, count=1, flags=re.I | re.S)
    block = head_block(title, description, url_path, schema, image)
    if "<!-- SEO:START -->" in content:
        content = re.sub(r'<!-- SEO:START -->.*?<!-- SEO:END -->', block, content, count=1, flags=re.S)
    else:
        content = content.replace("</head>", block + "\n</head>", 1)
    path.write_text(content, encoding="utf-8")


def home_schema():
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": abs_url("#website"),
                "url": abs_url(),
                "name": STORE,
                "alternateName": "LR Country",
                "inLanguage": "pt-BR",
            },
            {
                "@type": ["Organization", "OnlineStore"],
                "@id": abs_url("#organization"),
                "name": STORE,
                "url": abs_url(),
                "logo": abs_url("assets/brand/lr-mark-small.webp"),
                "image": abs_url(SEO.get("defaultImage", "assets/instagram/post-1.jpg")),
                "telephone": "+" + PHONE if PHONE else None,
                "sameAs": [INSTAGRAM],
                "areaServed": [
                    {"@type": "City", "name": "Rio das Ostras", "containedInPlace": {"@type": "State", "name": "Rio de Janeiro"}},
                    {"@type": "City", "name": "Macaé", "containedInPlace": {"@type": "State", "name": "Rio de Janeiro"}},
                    {"@type": "Country", "name": "Brasil"},
                ],
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": "+" + PHONE if PHONE else None,
                    "contactType": "customer service",
                    "availableLanguage": ["Portuguese"],
                },
            },
        ],
    }


def simple_page_schema(name: str, description: str, path: str):
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "name": name, "description": description, "url": abs_url(path), "inLanguage": "pt-BR"},
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Início", "item": abs_url()},
                    {"@type": "ListItem", "position": 2, "name": name, "item": abs_url(path)},
                ],
            },
        ],
    }


def add_local_section():
    path = ROOT / "index.html"
    content = path.read_text(encoding="utf-8")
    section = '''<!-- LOCAL-SEO:START -->
<section class="section seo-local-section" aria-labelledby="seoLocalTitle">
  <div class="container">
    <div class="section-heading split reveal"><div><p class="eyebrow">Pronta entrega local + envios nacionais</p><h2 id="seoLocalTitle">Moda country em Rio das Ostras e Macaé</h2></div></div>
    <p class="seo-local-intro">A LR Country Wear atende clientes de Rio das Ostras e Macaé com peças country de pronta entrega e também envia pedidos pelos Correios para outras cidades do Brasil. Escolha camisas, botas, calças, chapéus, cintos e jaquetas e finalize o atendimento pelo WhatsApp.</p>
    <div class="seo-local-grid">
      <a href="./loja-country-rio-das-ostras.html"><strong>Rio das Ostras</strong><span>Pronta entrega e atendimento local</span><b>Ver opções →</b></a>
      <a href="./loja-country-macae.html"><strong>Macaé</strong><span>Moda country com pronta entrega</span><b>Ver opções →</b></a>
      <a href="./envios-correios.html"><strong>Envios pelos Correios</strong><span>Pedidos para outras cidades do Brasil</span><b>Como funciona →</b></a>
    </div>
  </div>
</section>
<!-- LOCAL-SEO:END -->'''
    if "<!-- LOCAL-SEO:START -->" in content:
        content = re.sub(r'<!-- LOCAL-SEO:START -->.*?<!-- LOCAL-SEO:END -->', section, content, count=1, flags=re.S)
    else:
        marker = '<section class="instagram-section"'
        content = content.replace(marker, section + "\n    " + marker, 1)
    path.write_text(content, encoding="utf-8")


def update_store_links():
    path = ROOT / "assets/js/store.js"
    content = path.read_text(encoding="utf-8")
    old = '<h3>${esc(p.name)}</h3>'
    new = '<h3><a class="product-detail-link" href="./produtos/${encodeURIComponent(p.id)}.html" aria-label="Ver detalhes de ${esc(p.name)}">${esc(p.name)}</a></h3>'
    if old in content:
        content = content.replace(old, new)
    content = content.replace("if(!e.target.closest('button'))openProduct(card.dataset.product)", "if(!e.target.closest('button,a'))openProduct(card.dataset.product)")
    path.write_text(content, encoding="utf-8")


def product_availability(p):
    stock = sum(max(0, int(v.get("stock", 0) or 0)) for v in p.get("variants", []) if v.get("active", True))
    if stock > 0:
        return "https://schema.org/InStock", stock
    if p.get("type") == "order" or p.get("allowBackorder"):
        return "https://schema.org/BackOrder", 0
    return "https://schema.org/OutOfStock", 0


def product_page(p):
    slug = p["id"]
    path = f"produtos/{slug}.html"
    canonical = abs_url(path)
    image_rel = p.get("images", ["/assets/brand/lr-mark-small.webp"])[0].lstrip("/")
    image_abs = abs_url(image_rel)
    image_local = "../" + image_rel
    availability, stock = product_availability(p)
    title = f'{p["name"]} | Moda Country | {STORE}'
    description = f'{p.get("description", "")} Consulte tamanhos e disponibilidade. Pronta entrega em Rio das Ostras e Macaé e envios pelos Correios.'
    offer = {
        "@type": "Offer",
        "url": canonical,
        "priceCurrency": "BRL",
        "price": f'{float(p.get("price", 0)):.2f}',
        "availability": availability,
        "itemCondition": "https://schema.org/NewCondition",
    }
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Product",
                "name": p["name"],
                "description": p.get("description", ""),
                "image": [image_abs],
                "sku": p.get("sku", ""),
                "brand": {"@type": "Brand", "name": STORE},
                "category": p.get("category", "Moda Country"),
                "offers": offer,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Início", "item": abs_url()},
                    {"@type": "ListItem", "position": 2, "name": p.get("category", "Produtos"), "item": abs_url("pronta-entrega.html" if p.get("type") == "ready" else "sob-encomenda.html")},
                    {"@type": "ListItem", "position": 3, "name": p["name"], "item": canonical},
                ],
            },
        ],
    }
    variants = "".join(
        f'<li><strong>{esc(" / ".join(x for x in [v.get("size", ""), v.get("color", ""), v.get("model", "")] if x) or "Padrão")}</strong><span>{("Disponível: " + str(v.get("stock", 0)) + " un.") if p.get("type") == "ready" else "Sob encomenda"}</span></li>'
        for v in p.get("variants", []) if v.get("active", True)
    )
    price = f'R$ {float(p.get("price", 0)):,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    compare = ""
    if p.get("compareAtPrice"):
        old = f'R$ {float(p["compareAtPrice"]):,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
        compare = f'<del>{old}</del>'
    msg = quote(f'Olá! Tenho interesse no produto {p["name"]} ({p.get("sku", "")}). Gostaria de confirmar tamanho, disponibilidade e entrega.')
    status = "Pronta entrega" if p.get("type") == "ready" and stock > 0 else ("Sob encomenda" if p.get("type") == "order" else "Consulte disponibilidade")
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#090705"><meta name="color-scheme" content="dark"><title>{esc(title)}</title>
{head_block(title, description, path, schema, image_rel)}
<link rel="icon" href="../assets/brand/favicon.svg"><link rel="stylesheet" href="../assets/css/styles.css"></head>
<body><header class="seo-simple-header"><div class="container"><a class="logo" href="../"><strong>LR</strong><small>Country Wear</small></a><nav><a href="../pronta-entrega.html">Pronta entrega</a><a href="../sob-encomenda.html">Sob encomenda</a><a href="../loja-country-rio-das-ostras.html">Rio das Ostras</a><a href="../loja-country-macae.html">Macaé</a></nav></div></header>
<main class="seo-product-page"><div class="container seo-product-shell"><div class="seo-product-image"><img src="{esc(image_local)}" alt="{esc(p["name"])}"></div><article class="seo-product-copy"><p class="eyebrow">{esc(p.get("category", "Moda Country"))}{(" · " + esc(p.get("subcategory"))) if p.get("subcategory") else ""}</p><h1>{esc(p["name"])}</h1><div class="seo-product-price">{compare}<strong>{price}</strong></div><p>{esc(p.get("description", ""))}</p><div class="seo-product-status"><strong>{status}</strong><span>SKU {esc(p.get("sku", "—"))}</span></div><h2>Variações</h2><ul class="seo-variant-list">{variants}</ul><div class="seo-shipping-note"><strong>Atendimento e entrega</strong><p>Pronta entrega para Rio das Ostras e Macaé conforme disponibilidade. Para outras cidades, enviamos pelos Correios. Confirme prazo, tamanho e frete no atendimento.</p></div><a class="btn btn-whatsapp" href="https://wa.me/{PHONE}?text={msg}" target="_blank" rel="noopener noreferrer">Consultar pelo WhatsApp ↗</a></article></div>
<section class="section seo-product-links"><div class="container"><h2>Comprar moda country na região</h2><p><a href="../loja-country-rio-das-ostras.html">Moda country em Rio das Ostras</a> · <a href="../loja-country-macae.html">Moda country em Macaé</a> · <a href="../envios-correios.html">Envios pelos Correios</a></p></div></section></main>
<footer class="seo-simple-footer"><div class="container"><span>© {date.today().year} {esc(STORE)}</span><a href="{esc(INSTAGRAM)}" target="_blank" rel="noopener noreferrer">Instagram</a></div></footer></body></html>'''


def location_page(city: str, slug: str, intro: str, body_a: str, body_b: str):
    path = f"{slug}.html"
    title = f"Loja Country em {city} | Pronta Entrega | {STORE}"
    description = f"Moda country com pronta entrega para {city}: camisas, botas, calças, chapéus, cintos e jaquetas. Atendimento pelo WhatsApp e envios pelos Correios."
    schema = simple_page_schema(title, description, path)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#090705"><meta name="color-scheme" content="dark"><title>{esc(title)}</title>{head_block(title, description, path, schema)}<link rel="icon" href="./assets/brand/favicon.svg"><link rel="stylesheet" href="./assets/css/styles.css"></head><body><header class="seo-simple-header"><div class="container"><a class="logo" href="./"><strong>LR</strong><small>Country Wear</small></a><nav><a href="./pronta-entrega.html">Pronta entrega</a><a href="./sob-encomenda.html">Sob encomenda</a><a href="./#categorias">Categorias</a></nav></div></header><main><section class="seo-location-hero"><div class="container"><p class="eyebrow">LR Country Wear · {esc(city)}</p><h1>Moda country com pronta entrega em {esc(city)}</h1><p>{esc(intro)}</p><div class="hero-actions"><a class="btn btn-gold" href="./pronta-entrega.html">Ver pronta entrega →</a><a class="btn btn-whatsapp" href="https://wa.me/{PHONE}" target="_blank" rel="noopener noreferrer">Falar no WhatsApp ↗</a></div></div></section><section class="section seo-location-content"><div class="container seo-copy-grid"><article><h2>Country para o dia a dia, rodeio e arena</h2><p>{esc(body_a)}</p><p>O catálogo reúne camisas, botas, calças, chapéus, cintos e jaquetas em diferentes tamanhos e modelos. A disponibilidade mostrada no site é confirmada no atendimento antes da finalização.</p></article><article><h2>Pronta entrega e envio</h2><p>{esc(body_b)}</p><p>Para compras fora da região, a LR também envia pelos Correios. O valor e o prazo dependem do CEP e são confirmados antes do envio.</p></article></div></section><section class="section seo-local-cta"><div class="container"><p class="eyebrow">Atendimento direto</p><h2>Escolha sua peça e fale com a LR</h2><p>Monte sua sacola no site e envie o pedido completo pelo WhatsApp para confirmar tamanho, estoque e entrega.</p><a class="btn btn-gold" href="./pronta-entrega.html">Comprar pronta entrega →</a></div></section></main><footer class="seo-simple-footer"><div class="container"><span>© {date.today().year} {esc(STORE)}</span><a href="./envios-correios.html">Envios pelos Correios</a><a href="{esc(INSTAGRAM)}" target="_blank" rel="noopener noreferrer">Instagram</a></div></footer></body></html>'''


def shipping_page():
    path = "envios-correios.html"
    title = f"Envios pelos Correios | Moda Country | {STORE}"
    description = "Compre moda country na LR Country Wear e consulte o envio pelos Correios para sua cidade. Pronta entrega local em Rio das Ostras e Macaé."
    schema = simple_page_schema(title, description, path)
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#090705"><meta name="color-scheme" content="dark"><title>{esc(title)}</title>{head_block(title, description, path, schema)}<link rel="icon" href="./assets/brand/favicon.svg"><link rel="stylesheet" href="./assets/css/styles.css"></head><body><header class="seo-simple-header"><div class="container"><a class="logo" href="./"><strong>LR</strong><small>Country Wear</small></a><nav><a href="./pronta-entrega.html">Pronta entrega</a><a href="./loja-country-rio-das-ostras.html">Rio das Ostras</a><a href="./loja-country-macae.html">Macaé</a></nav></div></header><main><section class="seo-location-hero"><div class="container"><p class="eyebrow">Atendimento para todo o Brasil</p><h1>Moda country com envio pelos Correios</h1><p>Além da pronta entrega para Rio das Ostras e Macaé, a LR Country Wear atende clientes de outras cidades com envio pelos Correios. Escolha seus produtos e consulte o frete pelo WhatsApp.</p><div class="hero-actions"><a class="btn btn-gold" href="./pronta-entrega.html">Ver produtos →</a><a class="btn btn-whatsapp" href="https://wa.me/{PHONE}" target="_blank" rel="noopener noreferrer">Calcular atendimento ↗</a></div></div></section><section class="section seo-location-content"><div class="container seo-copy-grid"><article><h2>Como funciona o pedido</h2><p>Escolha os produtos disponíveis, selecione tamanho e variação, adicione à sacola e envie o resumo pelo WhatsApp. A equipe confirma estoque e condições antes da finalização.</p></article><article><h2>Prazo e frete</h2><p>O prazo e o valor do envio variam conforme CEP, peso e volume do pedido. A informação final é confirmada no atendimento antes da postagem.</p></article></div></section></main><footer class="seo-simple-footer"><div class="container"><span>© {date.today().year} {esc(STORE)}</span><a href="{esc(INSTAGRAM)}" target="_blank" rel="noopener noreferrer">Instagram</a></div></footer></body></html>'''


def write_pages():
    products_dir = ROOT / "produtos"
    products_dir.mkdir(exist_ok=True)
    for old in products_dir.glob("*.html"):
        old.unlink()
    for p in CATALOG.get("products", []):
        if p.get("active", True) and not p.get("deleted"):
            (products_dir / f'{p["id"]}.html').write_text(product_page(p), encoding="utf-8")
    (ROOT / "loja-country-rio-das-ostras.html").write_text(location_page(
        "Rio das Ostras", "loja-country-rio-das-ostras",
        "Peças country para quem quer comprar perto, confirmar disponibilidade rapidamente e receber atendimento direto da LR.",
        "Para quem está em Rio das Ostras, a proposta é facilitar a compra de moda country com catálogo online, estoque de pronta entrega e atendimento humano para escolher a variação certa.",
        "Os itens marcados como pronta entrega podem ser atendidos na região conforme confirmação de estoque. O pedido é organizado pelo site e finalizado diretamente com a equipe da LR.",
    ), encoding="utf-8")
    (ROOT / "loja-country-macae.html").write_text(location_page(
        "Macaé", "loja-country-macae",
        "A LR aproxima a moda country de Macaé com catálogo online, peças selecionadas e atendimento rápido para confirmar estoque e tamanho.",
        "Em Macaé, clientes que procuram camisa country, bota western, calça, chapéu, cinto ou jaqueta podem consultar as peças disponíveis sem depender de um catálogo genérico nacional.",
        "A pronta entrega para Macaé é confirmada produto a produto no atendimento. Assim você sabe a variação disponível antes de concluir o pedido e combinar a entrega.",
    ), encoding="utf-8")
    (ROOT / "envios-correios.html").write_text(shipping_page(), encoding="utf-8")


def write_robots_sitemap():
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('sitemap.xml')}\n", encoding="utf-8")
    urls = ["", "pronta-entrega.html", "sob-encomenda.html", "loja-country-rio-das-ostras.html", "loja-country-macae.html", "envios-correios.html"]
    urls += [f'produtos/{p["id"]}.html' for p in CATALOG.get("products", []) if p.get("active", True) and not p.get("deleted")]
    body = "\n".join(f"  <url><loc>{esc(abs_url(u))}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls)
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'''
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def update_core_pages():
    home_title = f"Loja Country em Rio das Ostras e Macaé | {STORE}"
    home_desc = "Moda country com pronta entrega em Rio das Ostras e Macaé. Camisas, botas, calças, chapéus, cintos e jaquetas. Enviamos pelos Correios e atendemos pelo WhatsApp."
    inject_head(ROOT / "index.html", home_title, home_desc, "", home_schema(), SEO.get("defaultImage"))
    ready_title = f"Moda Country Pronta Entrega | Rio das Ostras e Macaé | {STORE}"
    ready_desc = "Confira moda country pronta entrega para Rio das Ostras e Macaé: camisas, botas, calças, cintos e jaquetas. Consulte estoque e finalize pelo WhatsApp."
    inject_head(ROOT / "pronta-entrega.html", ready_title, ready_desc, "pronta-entrega.html", simple_page_schema(ready_title, ready_desc, "pronta-entrega.html"))
    order_title = f"Moda Country Sob Encomenda | {STORE}"
    order_desc = "Peças country sob encomenda: botas, camisas, chapéus e outros modelos. Consulte tamanhos, prazo e envio para Rio das Ostras, Macaé e outras cidades."
    inject_head(ROOT / "sob-encomenda.html", order_title, order_desc, "sob-encomenda.html", simple_page_schema(order_title, order_desc, "sob-encomenda.html"))
    add_local_section()
    update_store_links()


if __name__ == "__main__":
    update_core_pages()
    write_pages()
    write_robots_sitemap()
    print("SEO build complete")
