(() => {
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const money=v=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(Number(v||0));
  const state={catalog:null,settings:null,cart:JSON.parse(localStorage.getItem('lr-cart')||'[]'),activeCategory:'all'};
  const page=document.body.dataset.page||'home'; const mode=document.body.dataset.mode||null;
  const localUrl=v=>{if(!v)return '';const s=String(v);if(/^(https?:|data:|blob:)/i.test(s))return s;return './'+s.replace(/^\.\//,'').replace(/^\//,'')};

  async function load(){
    try{
      const [catalog,settings]=await Promise.all([fetch('./data/catalog.json',{cache:'no-store'}).then(r=>r.json()),fetch('./data/settings.json',{cache:'no-store'}).then(r=>r.json())]);
      state.catalog=catalog;state.settings=settings;applySettings();renderCart();bindGlobal();
      if(page==='home')renderHome(); if(page==='catalog')renderCatalog();
      initIntro();
    }catch(e){console.error(e);toast('Não foi possível carregar o catálogo.');}
  }
  function visibleProducts(){return (state.catalog?.products||[]).filter(p=>p.active!==false&&!p.deleted)}
  function productImage(p){return localUrl(p.images?.[0]||'assets/products/default.svg')}
  function availableStock(p){return (p.variants||[]).filter(v=>v.active!==false).reduce((n,v)=>n+Math.max(0,Number(v.stock||0)),0)}
  function isAvailable(p){return p.type==='order'||availableStock(p)>0||p.allowBackorder}
  function stockText(p){if(p.type==='order')return p.orderLeadTime?`Prazo estimado: ${p.orderLeadTime}`:'Disponível sob encomenda';const n=availableStock(p);if(n<=0)return p.allowBackorder?'Sob encomenda':'Esgotado';if(n<=Number(p.minStock||2))return `Últimas ${n} unidade${n===1?'':'s'}`;return 'Disponível para pronta entrega'}
  function productCard(p){
    const badges=[p.isNew?'<span class="badge gold">Novo</span>':'',p.type==='order'?'<span class="badge">Sob encomenda</span>':'',!isAvailable(p)?'<span class="badge">Esgotado</span>':''].join('');
    return `<article class="product-card" data-product="${p.id}"><div class="product-image"><img src="${esc(productImage(p))}" alt="${esc(p.name)}" loading="lazy"><div class="product-badges">${badges}</div><button class="quick-add" data-open-product="${p.id}">${isAvailable(p)?'Escolher opções':'Ver produto'}</button></div><div class="product-info"><div class="product-meta">${esc(p.category)}${p.subcategory?' · '+esc(p.subcategory):''}</div><h3>${esc(p.name)}</h3><div class="price">${p.compareAtPrice?`<del>${money(p.compareAtPrice)}</del>`:''}<span>${money(p.price)}</span></div><div class="stock-note ${availableStock(p)<=Number(p.minStock||2)?'low':''}">${esc(stockText(p))}</div></div></article>`;
  }
  function renderHome(){
    const products=visibleProducts();
    const ready=products.filter(p=>p.type==='ready'&&isAvailable(p)).sort(sortFeatured).slice(0,4);
    const featured=products.filter(p=>p.featured).sort(sortFeatured).slice(0,4);
    $('#readyGrid').innerHTML=ready.map(productCard).join(''); $('#featuredGrid').innerHTML=(featured.length?featured:products.slice(0,4)).map(productCard).join('');
    const cats=(state.catalog.categories||[]).filter(c=>c.active!==false).slice(0,8);
    $('#categoryGrid').innerHTML=cats.map((c,i)=>`<a class="category-card" href="./pronta-entrega.html?category=${encodeURIComponent(c.name)}"><img src="${esc(localUrl(c.image||categoryFallback(i)))}" alt="${esc(c.name)}" loading="lazy"><div class="category-copy"><span>Explorar</span><h3>${esc(c.name)}</h3></div></a>`).join('');
    bindProductButtons(document);
  }
  function renderCatalog(){
    const qs=new URLSearchParams(location.search); state.activeCategory=qs.get('category')||'all';
    const cats=['all',...(state.catalog.categories||[]).filter(c=>c.active!==false).map(c=>c.name)];
    $('#categoryFilters').innerHTML=cats.map(c=>`<button class="chip ${c===state.activeCategory?'active':''}" data-category="${esc(c)}">${c==='all'?'Todos':esc(c)}</button>`).join('');
    $$('[data-category]').forEach(b=>b.onclick=()=>{state.activeCategory=b.dataset.category;$$('[data-category]').forEach(x=>x.classList.toggle('active',x.dataset.category===state.activeCategory));renderCatalogGrid();});
    $('#sortSelect').onchange=renderCatalogGrid; renderCatalogGrid();
  }
  function renderCatalogGrid(){
    let list=visibleProducts().filter(p=>p.type===mode); if(state.activeCategory!=='all')list=list.filter(p=>p.category===state.activeCategory);
    const sort=$('#sortSelect')?.value||'featured'; if(sort==='featured')list.sort(sortFeatured);if(sort==='name')list.sort((a,b)=>a.name.localeCompare(b.name));if(sort==='price-asc')list.sort((a,b)=>a.price-b.price);if(sort==='price-desc')list.sort((a,b)=>b.price-a.price);
    $('#catalogGrid').innerHTML=list.map(productCard).join(''); $('#catalogCount').textContent=`${list.length} produto${list.length===1?'':'s'}`;$('#emptyState').hidden=!!list.length;bindProductButtons(document);
  }
  function sortFeatured(a,b){return Number(b.featured)-Number(a.featured)||(a.sortOrder||999)-(b.sortOrder||999)}
  function bindProductButtons(root){$$('[data-open-product]',root).forEach(btn=>btn.onclick=e=>{e.preventDefault();openProduct(btn.dataset.openProduct)});$$('.product-card',root).forEach(card=>{card.querySelector('.product-info')?.addEventListener('click',()=>openProduct(card.dataset.product))})}
  function openProduct(id){
    const p=visibleProducts().find(x=>x.id===id);if(!p)return; const variants=(p.variants||[]).filter(v=>v.active!==false && (p.type==='order'||v.stock>0||p.allowBackorder));
    const opt=variants.map(v=>`<option value="${v.id}" data-stock="${v.stock||0}">${esc(variantLabel(v))}${p.type==='ready'?` — ${v.stock||0} em estoque`:''}</option>`).join('');
    $('#productModalContent').innerHTML=`<div class="product-modal"><div class="product-modal-image"><img src="${esc(productImage(p))}" alt="${esc(p.name)}"></div><div class="product-modal-copy"><button class="close-modal" data-close-modal>×</button><p class="eyebrow">${esc(p.category)}${p.subcategory?' · '+esc(p.subcategory):''}</p><h2>${esc(p.name)}</h2><div class="price">${p.compareAtPrice?`<del>${money(p.compareAtPrice)}</del>`:''}<span>${money(p.price)}</span></div><p class="description">${esc(p.description||'')}</p><div class="availability"><strong>${esc(stockText(p))}</strong></div><div class="variant-group"><label>Escolha a variação</label><select id="variantSelect" class="variant-select">${opt||'<option value="default">Padrão</option>'}</select></div><div class="product-modal-actions"><button class="btn btn-gold" id="addToCart" ${!isAvailable(p)?'disabled':''}>${isAvailable(p)?'Adicionar à sacola':'Indisponível'}</button></div><p class="stock-note">SKU: ${esc(p.sku||'—')}</p></div></div>`;
    $('#productModal').classList.add('open');document.body.classList.add('modal-open');$('#productModal').setAttribute('aria-hidden','false');
    $('[data-close-modal]').onclick=closeModal; $('#productModal').onclick=e=>{if(e.target.id==='productModal')closeModal()};
    $('#addToCart').onclick=()=>addToCart(p,$('#variantSelect').value);
  }
  function closeModal(){$('#productModal')?.classList.remove('open');document.body.classList.remove('modal-open')}
  function variantLabel(v){return [v.size,v.color,v.model].filter(Boolean).join(' / ')||v.label||'Padrão'}
  function addToCart(p,variantId){const v=(p.variants||[]).find(x=>x.id===variantId)||{id:'default',stock:999};const key=`${p.id}:${v.id}`;const existing=state.cart.find(i=>i.key===key);const max=p.type==='ready'&&!p.allowBackorder?Number(v.stock||0):99;if(existing){if(existing.qty>=max)return toast('Quantidade máxima disponível na sacola.');existing.qty++}else state.cart.push({key,productId:p.id,variantId:v.id,qty:1});saveCart();closeModal();openCart();toast('Produto adicionado à sacola.')}
  function saveCart(){localStorage.setItem('lr-cart',JSON.stringify(state.cart));renderCart()}
  function renderCart(){if(!state.catalog)return;const count=state.cart.reduce((n,i)=>n+i.qty,0);$$('[data-cart-count]').forEach(el=>el.textContent=count);const box=$('#cartItems');if(!box)return;if(!state.cart.length){box.innerHTML='<div class="empty-state"><h3>Sua sacola está vazia</h3><p>Escolha suas peças e volte aqui para finalizar.</p></div>';$('#cartTotal').textContent=money(0);return}let total=0;box.innerHTML=state.cart.map(i=>{const p=state.catalog.products.find(x=>x.id===i.productId);if(!p)return '';const v=(p.variants||[]).find(x=>x.id===i.variantId)||{};total+=Number(p.price)*i.qty;return `<div class="cart-item"><img src="${esc(productImage(p))}" alt="${esc(p.name)}"><div><h4>${esc(p.name)}</h4><small>${esc(variantLabel(v))}</small><small>${money(p.price)}</small><div class="qty"><button data-qty="-1" data-key="${i.key}">−</button><strong>${i.qty}</strong><button data-qty="1" data-key="${i.key}">+</button><button class="remove-item" data-remove="${i.key}">remover</button></div></div><strong>${money(Number(p.price)*i.qty)}</strong></div>`}).join('');$('#cartTotal').textContent=money(total);$$('[data-qty]',box).forEach(b=>b.onclick=()=>changeQty(b.dataset.key,Number(b.dataset.qty)));$$('[data-remove]',box).forEach(b=>b.onclick=()=>{state.cart=state.cart.filter(i=>i.key!==b.dataset.remove);saveCart()})}
  function changeQty(key,d){const i=state.cart.find(x=>x.key===key);if(!i)return;const p=state.catalog.products.find(x=>x.id===i.productId);const v=(p.variants||[]).find(x=>x.id===i.variantId)||{};const max=p.type==='ready'&&!p.allowBackorder?Number(v.stock||0):99;i.qty=Math.max(1,Math.min(max,i.qty+d));saveCart()}
  function openCart(){$('#cartDrawer')?.classList.add('open');$('#drawerBackdrop')?.classList.add('open');document.body.classList.add('drawer-open')}
  function closeCart(){$('#cartDrawer')?.classList.remove('open');$('#drawerBackdrop')?.classList.remove('open');document.body.classList.remove('drawer-open')}
  function checkout(){if(!state.cart.length)return toast('Sua sacola está vazia.');const s=state.settings;const id=`LR-${Date.now().toString().slice(-6)}`;let total=0;const lines=state.cart.map(i=>{const p=state.catalog.products.find(x=>x.id===i.productId);const v=(p.variants||[]).find(x=>x.id===i.variantId)||{};total+=p.price*i.qty;return `• ${i.qty}x ${p.name}\n  ${variantLabel(v)}\n  ${money(p.price)} cada`});const msg=`Olá! Gostaria de finalizar este pedido na ${s.storeName||'LR Country Wear'}.\n\n*Pedido ${id}*\n\n${lines.join('\n\n')}\n\n*Total dos produtos: ${money(total)}*\n\nGostaria de confirmar disponibilidade e finalizar a compra.`;const phone=String(s.whatsapp||'').replace(/\D/g,'');if(!phone)return toast('WhatsApp ainda não configurado.');window.open(`https://wa.me/${phone}?text=${encodeURIComponent(msg)}`,'_blank','noopener')}
  function applySettings(){const s=state.settings||{};$$('[data-footer-tagline]').forEach(e=>e.textContent=s.tagline||'Mais que estilo, é um jeito de viver.');$$('[data-whatsapp-link]').forEach(e=>e.href=`https://wa.me/${String(s.whatsapp||'').replace(/\D/g,'')}`);$$('[data-instagram-link]').forEach(e=>e.href=s.instagram||'#');if($('[data-hero-kicker]'))$('[data-hero-kicker]').textContent=s.heroKicker||'Nova coleção';if($('[data-hero-title]'))$('[data-hero-title]').innerHTML=esc(s.heroTitle||'Vista o country.\nViva o country.').replace(/\n/g,'<br>');if($('[data-hero-subtitle]'))$('[data-hero-subtitle]').textContent=s.heroSubtitle||'';$('#year')?.replaceChildren(String(new Date().getFullYear()))}
  function bindGlobal(){$$('[data-cart-open]').forEach(b=>b.onclick=openCart);$$('[data-cart-close]').forEach(b=>b.onclick=closeCart);$('#checkoutWhatsApp')?.addEventListener('click',checkout);$$('[data-search-toggle]').forEach(b=>b.onclick=()=>{$('#searchPanel').classList.toggle('open');if($('#searchPanel').classList.contains('open'))setTimeout(()=>$('#globalSearch')?.focus(),150)});$('#globalSearch')?.addEventListener('input',e=>renderSearch(e.target.value));document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeCart();closeModal();$('#searchPanel')?.classList.remove('open')}});window.addEventListener('scroll',()=>$('#siteHeader')?.classList.toggle('is-scrolled',scrollY>80))}
  function renderSearch(q){const box=$('#searchResults');if(!box)return;const t=q.trim().toLowerCase();if(t.length<2){box.innerHTML='';return}const list=visibleProducts().filter(p=>[p.name,p.category,p.subcategory,p.sku].join(' ').toLowerCase().includes(t)).slice(0,8);box.innerHTML=list.map(p=>`<button class="search-result" data-open-product="${p.id}"><small>${esc(p.category)}</small><strong>${esc(p.name)}</strong><span>${money(p.price)}</span></button>`).join('');bindProductButtons(box)}
  function initIntro(){if(page!=='home')return;const intro=$('#intro');const s=state.settings||{};if(!s.introEnabled||sessionStorage.getItem('lr-intro-seen')){intro?.classList.add('hidden');return}const video=$('#introVideo'),audio=$('#introAudio');if(s.introVideo){video.src=localUrl(s.introVideo);video.classList.add('active');video.play().catch(()=>{})}if(s.introAudio)audio.src=localUrl(s.introAudio);const enter=withSound=>{sessionStorage.setItem('lr-intro-seen','1');if(withSound&&s.introAudio)audio.play().catch(()=>{});intro.classList.add('hidden');setTimeout(()=>intro.remove(),900)};$('#enterStore').onclick=()=>enter(true);$('#enterMuted').onclick=()=>enter(false);if(s.introAutoEnter!==false)setTimeout(()=>{if(!intro.classList.contains('hidden'))enter(false)},5000)}
  function categoryFallback(i){return ['assets/products/shirt.svg','assets/products/boot.svg','assets/products/pants.svg','assets/products/hat.svg','assets/products/belt.svg','assets/products/jacket.svg'][i%6]}
  function esc(v=''){return String(v).replace(/[&<>'"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#039;','"':'&quot;'}[m]))}
  let tt;function toast(msg){const el=$('#toast');if(!el)return;el.textContent=msg;el.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>el.classList.remove('show'),2600)}
  load();
})();
