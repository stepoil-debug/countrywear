from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = json.loads((ROOT / "data/settings.json").read_text(encoding="utf-8"))
SEO = json.loads((ROOT / "data/seo.json").read_text(encoding="utf-8"))
MARKETPLACES = json.loads((ROOT / "data/marketplaces.json").read_text(encoding="utf-8"))

STORE = SETTINGS.get("storeName", "LR Country Wear")
PHONE = "".join(ch for ch in SETTINGS.get("whatsapp", "") if ch.isdigit())
INSTAGRAM = SETTINGS.get("instagram", "https://www.instagram.com/lr_countrywear/")
SITE = SEO.get("siteUrl", "").rstrip("/")
CANONICAL = f"{SITE}/envios-correios.html"
IMAGE = f"{SITE}/{SEO.get('defaultImage', 'assets/instagram/post-1.jpg').lstrip('/')}"


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def marketplace_button(key: str, css_class: str) -> str:
    cfg = MARKETPLACES.get(key, {})
    label = esc(cfg.get("label", key))
    url = str(cfg.get("url", "") or "").strip()
    if url:
        return f'<a class="btn marketplace-btn {css_class}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">Abrir loja {label} ↗</a>'
    return f'<button class="btn marketplace-btn {css_class} is-pending" type="button" disabled aria-disabled="true" data-marketplace="{esc(key)}">Abrir loja {label} <span>Em breve</span></button>'


ml_btn = marketplace_button("mercadoLivre", "marketplace-btn--ml")
shopee_btn = marketplace_button("shopee", "marketplace-btn--shopee")

TITLE = f"Correios, Mercado Livre e Shopee | Moda Country | {STORE}"
DESCRIPTION = (
    "Compre moda country na LR Country Wear com pronta entrega em Rio das Ostras e Macaé, "
    "envios pelos Correios e estrutura preparada para as lojas da LR no Mercado Livre e Shopee."
)

schema = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "WebPage",
            "name": TITLE,
            "description": DESCRIPTION,
            "url": CANONICAL,
            "inLanguage": "pt-BR",
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Onde comprar e envios", "item": CANONICAL},
            ],
        },
    ],
}

page = f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="theme-color" content="#090705">
  <meta name="color-scheme" content="dark">
  <title>{esc(TITLE)}</title>
  <meta name="description" content="{esc(DESCRIPTION)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <link rel="canonical" href="{esc(CANONICAL)}">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{esc(STORE)}">
  <meta property="og:title" content="{esc(TITLE)}">
  <meta property="og:description" content="{esc(DESCRIPTION)}">
  <meta property="og:url" content="{esc(CANONICAL)}">
  <meta property="og:image" content="{esc(IMAGE)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(TITLE)}">
  <meta name="twitter:description" content="{esc(DESCRIPTION)}">
  <meta name="twitter:image" content="{esc(IMAGE)}">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
  <link rel="icon" href="./assets/brand/favicon.svg">
  <link rel="stylesheet" href="./assets/css/styles.css">
</head>
<body>
  <header class="seo-simple-header">
    <div class="container">
      <a class="logo" href="./"><strong>LR</strong><small>Country Wear</small></a>
      <nav>
        <a href="./pronta-entrega.html">Pronta entrega</a>
        <a href="./loja-country-rio-das-ostras.html">Rio das Ostras</a>
        <a href="./loja-country-macae.html">Macaé</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="seo-location-hero marketplace-hero">
      <div class="container">
        <p class="eyebrow">Compre pelo canal que preferir</p>
        <h1>Correios, Mercado Livre e Shopee</h1>
        <p>A LR Country Wear atende Rio das Ostras e Macaé com pronta entrega e também envia para outras cidades pelos Correios. A estrutura das lojas no Mercado Livre e na Shopee já está preparada e os links serão ativados quando os canais estiverem publicados.</p>
        <div class="hero-actions">
          <a class="btn btn-gold" href="./pronta-entrega.html">Ver produtos →</a>
          <a class="btn btn-whatsapp" href="https://wa.me/{PHONE}" target="_blank" rel="noopener noreferrer">Falar com a LR ↗</a>
        </div>
      </div>
    </section>

    <section class="section marketplace-section" aria-labelledby="marketplaceTitle">
      <div class="container">
        <div class="section-heading">
          <p class="eyebrow">Canais de compra</p>
          <h2 id="marketplaceTitle">Escolha onde comprar</h2>
          <p class="marketplace-intro">O catálogo da LR será centralizado no ERP. O site continua sendo o canal principal e, quando Mercado Livre e Shopee forem ativados, os botões abaixo levarão diretamente às respectivas lojas.</p>
        </div>
        <div class="marketplace-grid">
          <article class="marketplace-card marketplace-card--site">
            <div class="marketplace-brand"><span>LR</span><div><small>Canal principal</small><strong>Site LR + Correios</strong></div></div>
            <p>Escolha os produtos no site, envie a sacola pelo WhatsApp e confirme estoque, CEP, prazo e frete. Para fora da região, o envio é feito pelos Correios.</p>
            <div class="marketplace-status is-live"><i></i> Disponível agora</div>
            <a class="btn btn-gold marketplace-btn" href="./pronta-entrega.html">Comprar no site →</a>
          </article>

          <article class="marketplace-card marketplace-card--ml">
            <div class="marketplace-brand"><span>ML</span><div><small>Marketplace</small><strong>Mercado Livre</strong></div></div>
            <p>Canal preparado para receber os produtos da LR. Quando a loja estiver ativa, este botão levará diretamente para a página oficial no Mercado Livre.</p>
            <div class="marketplace-status is-pending"><i></i> Loja em preparação</div>
            {ml_btn}
          </article>

          <article class="marketplace-card marketplace-card--shopee">
            <div class="marketplace-brand"><span>SP</span><div><small>Marketplace</small><strong>Shopee</strong></div></div>
            <p>Canal preparado para publicação dos produtos da LR. Assim que a loja estiver pronta, este botão abrirá diretamente a loja oficial na Shopee.</p>
            <div class="marketplace-status is-pending"><i></i> Loja em preparação</div>
            {shopee_btn}
          </article>
        </div>
      </div>
    </section>

    <section class="section seo-location-content marketplace-how">
      <div class="container seo-copy-grid">
        <article>
          <h2>Como funciona pelo site</h2>
          <p>Escolha os produtos disponíveis, selecione tamanho e variação, adicione à sacola e envie o resumo pelo WhatsApp. A equipe confirma estoque, prazo e condições antes da finalização.</p>
        </article>
        <article>
          <h2>Prazo e frete pelos Correios</h2>
          <p>O prazo e o valor do envio variam conforme CEP, peso e volume do pedido. A informação final é confirmada no atendimento antes da postagem.</p>
        </article>
      </div>
    </section>
  </main>

  <footer class="seo-simple-footer">
    <div class="container">
      <span>© {date.today().year} {esc(STORE)}</span>
      <a href="{esc(INSTAGRAM)}" target="_blank" rel="noopener noreferrer">Instagram</a>
    </div>
  </footer>
</body>
</html>
'''

(ROOT / "envios-correios.html").write_text(page, encoding="utf-8")
print("Marketplace purchase channels applied to envios-correios.html")
