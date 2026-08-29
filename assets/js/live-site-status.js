(() => {
  'use strict';

  const VERSION = '3.2';
  const ENDPOINT = 'https://counterapi.com/api/yulliwasameur.github.io/visit/personal-site?unique=true';
  const COPY = {
    fr: {
      visitors: 'visiteurs uniques estimés',
      title: 'Estimation dédupliquée par empreinte anonyme ; aucune identité n’est affichée.',
      version: `Version ${VERSION}`,
    },
    en: {
      visitors: 'estimated unique visitors',
      title: 'Deduplicated estimate based on an anonymous hash; no identity is displayed.',
      version: `Version ${VERSION}`,
    },
    kab: {
      visitors: 'inebgawen imezliyen (asumer)',
      title: 'Asumer yettwasemmezdi s udlis uffir; ulac tamagit i d-yettwaseknen.',
      version: `Lqem ${VERSION}`,
    },
  };

  const currentLang = () => {
    const query = new URLSearchParams(window.location.search).get('lang');
    if (['fr', 'en', 'kab'].includes(query)) return query;
    const htmlLang = String(document.documentElement.lang || '').toLowerCase();
    if (htmlLang.startsWith('en')) return 'en';
    if (htmlLang.startsWith('kab')) return 'kab';
    return 'fr';
  };

  function addVersionBadge() {
    const nav = document.querySelector('.masthead__menu .visible-links');
    if (!nav || document.querySelector('.ya-version-badge')) return;
    const item = document.createElement('li');
    item.className = 'masthead__menu-item ya-version-badge';
    const badge = document.createElement('span');
    badge.textContent = `v${VERSION}`;
    badge.setAttribute('aria-label', COPY[currentLang()].version);
    item.append(badge);
    nav.append(item);
  }

  function addVisitorCounter() {
    if (document.querySelector('.ya-unique-counter')) return;
    const widget = document.createElement('aside');
    widget.className = 'ya-unique-counter';
    widget.setAttribute('role', 'status');
    widget.setAttribute('aria-live', 'polite');

    const dot = document.createElement('i');
    dot.setAttribute('aria-hidden', 'true');
    const count = document.createElement('strong');
    count.textContent = '—';
    count.id = 'ya-unique-visitor-count';
    const label = document.createElement('span');
    label.className = 'ya-unique-counter__label';

    widget.append(dot, count, label);
    document.body.append(widget);

    const translate = () => {
      const copy = COPY[currentLang()];
      label.textContent = copy.visitors;
      widget.title = copy.title;
      widget.setAttribute('aria-label', `${count.textContent} ${copy.visitors}`);
    };
    translate();

    document.querySelectorAll('[data-site-lang]').forEach((button) => {
      button.addEventListener('click', () => window.setTimeout(translate, 0));
    });

    fetch(ENDPOINT, { cache: 'no-store', headers: { Accept: 'application/json' } })
      .then((response) => {
        if (!response.ok) throw new Error(`Counter HTTP ${response.status}`);
        return response.json();
      })
      .then((payload) => {
        const value = payload?.count ?? payload?.data?.count ?? payload?.value;
        if (!Number.isFinite(Number(value))) throw new Error('Counter response missing count');
        count.textContent = new Intl.NumberFormat(currentLang() === 'en' ? 'en-GB' : 'fr-FR').format(Number(value));
        widget.classList.add('is-ready');
        translate();
      })
      .catch(() => {
        widget.classList.add('is-unavailable');
        translate();
      });
  }

  function init() {
    addVersionBadge();
    addVisitorCounter();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
