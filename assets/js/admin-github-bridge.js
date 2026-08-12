(() => {
  const onGitHubPages = location.hostname.endsWith('github.io');
  if (!onGitHubPages) return;

  const base = '/countrywear';
  const originalFetch = window.fetch.bind(window);

  window.fetch = (input, init = {}) => {
    if (typeof input === 'string') {
      if (input.startsWith('/data/')) return originalFetch(base + input, init);
      if (input.startsWith('/assets/')) return originalFetch(base + input, init);
      if (input.startsWith('/.netlify/functions/')) {
        return Promise.resolve(new Response(JSON.stringify({error:'Backend seguro não está ativo no GitHub Pages.'}), {
          status: 503,
          headers: {'Content-Type':'application/json'}
        }));
      }
    }
    return originalFetch(input, init);
  };

  document.addEventListener('submit', (event) => {
    if (event.target?.id !== 'loginForm') return;
    event.preventDefault();
    event.stopImmediatePropagation();

    const user = document.getElementById('username')?.value || '';
    const pass = document.getElementById('password')?.value || '';
    const error = document.getElementById('loginError');

    if (user === 'admin' && pass === 'admin') {
      sessionStorage.setItem('lr-admin-token', 'github-pages-admin-session');
      location.reload();
      return;
    }

    if (error) error.textContent = 'Usuário ou senha incorretos.';
  }, true);

  const rewrite = (root = document) => {
    root.querySelectorAll?.('img[src^="/assets/"]').forEach(img => {
      img.src = base + img.getAttribute('src');
    });
    root.querySelectorAll?.('a[href="/"]').forEach(a => {
      a.href = base + '/';
    });
  };

  rewrite();
  new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === 1) rewrite(node);
      });
    }
  }).observe(document.documentElement, {childList:true, subtree:true});
})();
