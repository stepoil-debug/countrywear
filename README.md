# LR Country Wear — Loja + ERP

Projeto completo para catálogo de produtos country, pronta entrega, sob encomenda, carrinho e fechamento via WhatsApp, com painel administrativo conectado ao GitHub.

## O que já está pronto

- Home premium responsiva com introdução cinematográfica e suporte a vídeo/áudio.
- Página **Pronta Entrega** com categorias, filtros, variações e estoque.
- Página **Sob Encomenda** com prazo e variações.
- Carrinho persistente no navegador e envio da sacola completa para o WhatsApp.
- ERP/Admin com login, dashboard, produtos, variações, estoque, categorias, lixeira, mídia e conteúdo da loja.
- Ajustes de estoque com histórico operacional.
- Exportação de estoque em CSV.
- Upload de imagens com compressão automática para WebP; suporte a áudio/vídeo.
- Conteúdo, catálogo e mídias versionados no GitHub.
- Netlify Functions para autenticação e gravação segura no repositório.

## Arquitetura

`Loja estática -> JSON versionado -> Netlify -> Funções seguras -> GitHub API`

O cliente da loja nunca recebe o token do GitHub. O painel administrativo usa uma sessão assinada de 12 horas.

## Configuração única no Netlify

Conecte este repositório ao Netlify e crie as variáveis de ambiente:

```text
ADMIN_USER=admin
ADMIN_PASSWORD=<senha-forte-do-administrador>
SESSION_SECRET=<segredo-aleatorio-longo>
GITHUB_REPO=stepoil-debug/countrywear
GITHUB_BRANCH=main
GITHUB_TOKEN=<token-com-permissao-contents-read-write-no-repositorio>
```

> Nunca grave `ADMIN_PASSWORD`, `SESSION_SECRET` ou `GITHUB_TOKEN` dentro do repositório.

Depois do deploy:

- Loja: `/`
- Pronta entrega: `/pronta-entrega.html`
- Sob encomenda: `/sob-encomenda.html`
- Administração: `/admin/`

## Como o administrador trabalha

1. Entra em `/admin/`.
2. Cria/edita produto, categoria, estoque, fotos ou textos.
3. Clica **Salvar alterações**.
4. O painel cria commits no GitHub.
5. O Netlify detecta o commit e publica a nova versão.

## WhatsApp

O carrinho gera uma mensagem completa com ID do pedido, itens, variações, quantidades e total dos produtos. O envio ao WhatsApp **não baixa estoque automaticamente**. A baixa deve ocorrer quando a venda for confirmada, evitando reservar estoque para clientes que apenas abriram a conversa.

## Introdução musical

A abertura suporta `introVideo` e `introAudio` nas configurações do admin. Navegadores normalmente bloqueiam áudio automático, então o som inicia no clique do visitante em **Entrar na LR**. Sem mídia cadastrada, a abertura usa a identidade visual da marca como fallback.

## Segurança

- Credenciais e token ficam somente nas variáveis do Netlify.
- Funções administrativas exigem token de sessão assinado.
- O upload é restrito às pastas de mídia do projeto e tem limite de 6 MB por arquivo após processamento.
- O repositório pode permanecer público sem expor as credenciais.
