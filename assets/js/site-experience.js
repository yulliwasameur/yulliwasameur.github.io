(() => {
  'use strict';

  const LANGS = ['fr', 'en', 'kab'];
  const LOCALES = { fr: 'fr-FR', en: 'en-GB', kab: 'fr-DZ' };
  const NAV = {
    fr: { publications: 'Publications', research: 'Recherche', teaching: 'Enseignement', talks: 'Conférences', analyses: 'Analyses', code: 'Code', cv: 'CV', radar: 'CyberResearch Radar' },
    en: { publications: 'Publications', research: 'Research', teaching: 'Teaching', talks: 'Talks', analyses: 'Insights', code: 'Code', cv: 'CV', radar: 'CyberResearch Radar' },
    kab: { publications: 'Imagraden', research: 'Anadi', teaching: 'Aselmed', talks: 'Timliliyin', analyses: 'Tisleḍ', code: 'Tangalt', cv: 'CV', radar: 'CyberResearch Radar' }
  };
  const PAGE_TITLES = {
    '/': { fr: 'Yulliwas Ameur — Recherche, cybersécurité et formation', en: 'Yulliwas Ameur — Research, cybersecurity and education', kab: 'Yulliwas Ameur — Anadi, taɣellist tumḍint d uselmed' },
    '/publications/': { fr: 'Publications', en: 'Publications', kab: 'Imagraden' },
    '/recherche/': { fr: 'Recherche', en: 'Research', kab: 'Anadi' },
    '/teaching/': { fr: 'Enseignement', en: 'Teaching', kab: 'Aselmed' },
    '/talks/': { fr: 'Conférences et interventions', en: 'Talks and conferences', kab: 'Timliliyin d tameslayin' },
    '/analyses/': { fr: 'Analyses', en: 'Insights', kab: 'Tisleḍ' },
    '/code/': { fr: 'Code et artefacts', en: 'Code and artefacts', kab: 'Tangalt d yiferdisen' },
    '/cv/': { fr: 'Curriculum vitæ', en: 'Curriculum vitae', kab: 'Amecwar n uxeddim' }
  };
  const META = {
    fr: 'Portail académique trilingue de Yulliwas Ameur : recherche, publications, conférences, formations et CyberResearch Radar.',
    en: 'Yulliwas Ameur’s trilingual academic portal: research, publications, talks, education and CyberResearch Radar.',
    kab: 'Asmel akademi s kraḍ n tutlayin n Yulliwas Ameur: anadi, imagraden, timliliyin, aselmed d CyberResearch Radar.'
  };
  const RADAR_COPY = {
    fr: { conference: 'Conférence', workshop: 'Workshop', fallback: 'Les prochaines échéances seront visibles lors de la prochaine synchronisation.' },
    en: { conference: 'Conference', workshop: 'Workshop', fallback: 'Upcoming deadlines will appear after the next synchronisation.' },
    kab: { conference: 'Tamlilit', workshop: 'Workshop', fallback: 'Izmaz iqerben ad d-banen deg usnifel awurman i d-iteddun.' }
  };
  const state = { lang: 'fr', theme: 'dark', radar: [], manifest: null, rotateTimer: null };

  const attr = (node, name) => node.getAttribute(`data-${name}`);
  const pathKey = () => {
    const path = window.location.pathname;
    return path.endsWith('/') ? path : `${path}/`;
  };
  const initialLang = () => {
    const query = new URLSearchParams(window.location.search).get('lang');
    if (LANGS.includes(query)) return query;
    try { const saved = localStorage.getItem('ya-language'); if (LANGS.includes(saved)) return saved; } catch (_) {}
    return 'fr';
  };
  const initialTheme = () => {
    try { const saved = localStorage.getItem('ya-theme'); if (saved === 'light' || saved === 'dark') return saved; } catch (_) {}
    return 'dark';
  };

  function translateNode(node, lang) {
    const value = attr(node, lang);
    if (value !== null) node.textContent = value;
    const html = attr(node, `${lang}-html`);
    if (html !== null) node.innerHTML = html;
    const aria = attr(node, `${lang}-aria`);
    if (aria !== null) node.setAttribute('aria-label', aria);
  }

  function updateLinks() {
    document.querySelectorAll('[data-lang-link], [data-radar-link]').forEach((link) => {
      try {
        const url = new URL(link.getAttribute('href'), window.location.origin);
        if (url.origin !== window.location.origin) return;
        url.searchParams.set('lang', state.lang);
        link.href = `${url.pathname}${url.search}${url.hash}`;
      } catch (_) {}
    });
  }

  function updatePageTitle() {
    const translations = PAGE_TITLES[pathKey()];
    if (translations) {
      const title = translations[state.lang] || translations.fr;
      document.title = pathKey() === '/' ? title : `${title} - Yulliwas AMEUR`;
      const heading = pathKey() !== '/' ? document.querySelector('.page__title, .archive h1') : null;
      if (heading) heading.textContent = title;
    }
    const meta = document.querySelector('meta[name="description"]');
    if (meta && pathKey() === '/') meta.content = META[state.lang];
  }

  function startRotator() {
    const node = document.querySelector('.ya-rotate');
    if (!node) return;
    clearInterval(state.rotateTimer);
    const values = (attr(node, `rotate-${state.lang}`) || '').split('|').filter(Boolean);
    if (!values.length) return;
    let index = 0;
    node.textContent = values[0];
    state.rotateTimer = setInterval(() => {
      node.classList.add('is-changing');
      window.setTimeout(() => { index = (index + 1) % values.length; node.textContent = values[index]; node.classList.remove('is-changing'); }, 180);
    }, 2600);
  }

  function renderRadar() {
    const list = document.getElementById('ya-next-calls');
    if (!list) return;
    list.replaceChildren();
    if (!state.radar.length) {
      const p = document.createElement('p'); p.className = 'ya-call-fallback'; p.textContent = RADAR_COPY[state.lang].fallback; list.append(p); return;
    }
    state.radar.slice(0, 3).forEach((item) => {
      const a = document.createElement('a'); a.className = 'ya-call'; a.href = item.cfpUrl || item.officialUrl || item.evidenceUrl || `/cyberresearchradar/?lang=${state.lang}`; a.target = '_blank'; a.rel = 'noreferrer';
      const date = new Date(item.deadline);
      const d = document.createElement('span'); d.className = 'ya-call-date';
      const day = document.createElement('b'); day.textContent = new Intl.DateTimeFormat(LOCALES[state.lang], { day: '2-digit', timeZone: 'UTC' }).format(date);
      const month = document.createElement('small'); month.textContent = new Intl.DateTimeFormat(LOCALES[state.lang], { month: 'short', timeZone: 'UTC' }).format(date).replace('.', ''); d.append(day, month);
      const body = document.createElement('span'); body.className = 'ya-call-body';
      const title = document.createElement('b'); title.textContent = item.acronym || item.title; title.title = item.title;
      const details = document.createElement('small'); details.textContent = [RADAR_COPY[state.lang][item.type] || item.type, item.city, item.country].filter(Boolean).join(' · '); body.append(title, details);
      const arrow = document.createElement('i'); arrow.textContent = '↗'; arrow.setAttribute('aria-hidden', 'true'); a.append(d, body, arrow); list.append(a);
    });
  }

  function applyLanguage(lang, writeUrl = false) {
    state.lang = LANGS.includes(lang) ? lang : 'fr';
    document.documentElement.lang = state.lang;
    document.querySelectorAll('[data-fr], [data-en], [data-kab], [data-fr-aria], [data-en-aria], [data-kab-aria]').forEach((node) => translateNode(node, state.lang));
    document.querySelectorAll('[data-nav-key]').forEach((node) => { const key = node.dataset.navKey; if (NAV[state.lang][key]) node.textContent = NAV[state.lang][key]; });
    document.querySelectorAll('[data-site-lang]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.siteLang === state.lang)));
    updateLinks(); updatePageTitle(); startRotator(); renderRadar();
    try { localStorage.setItem('ya-language', state.lang); } catch (_) {}
    if (writeUrl) { const url = new URL(window.location.href); url.searchParams.set('lang', state.lang); history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`); }
  }

  function applyTheme(theme) {
    state.theme = theme === 'light' ? 'light' : 'dark';
    document.documentElement.dataset.siteTheme = state.theme;
    const button = document.querySelector('[data-theme-toggle]');
    if (button) button.setAttribute('aria-pressed', String(state.theme === 'light'));
    try { localStorage.setItem('ya-theme', state.theme); } catch (_) {}
  }

  function initControls() {
    document.querySelectorAll('[data-site-lang]').forEach((button) => button.addEventListener('click', () => applyLanguage(button.dataset.siteLang, true)));
    const theme = document.querySelector('[data-theme-toggle]');
    if (theme) theme.addEventListener('click', () => applyTheme(state.theme === 'dark' ? 'light' : 'dark'));
  }

  function initReveal() {
    const nodes = [...document.querySelectorAll('[data-reveal]')];
    nodes.forEach((node) => node.style.setProperty('--delay', `${Number(node.dataset.delay || 0)}ms`));
    if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) { nodes.forEach((node) => node.classList.add('is-visible')); return; }
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); } }), { threshold: .12, rootMargin: '0px 0px -8% 0px' });
    nodes.forEach((node) => observer.observe(node));
  }

  function initCounters() {
    const run = (node) => {
      const end = Number(node.dataset.count); if (!Number.isFinite(end)) return;
      const start = performance.now();
      const tick = (now) => { const p = Math.min(1, (now - start) / 900); node.textContent = String(Math.round(end * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    };
    const nodes = [...document.querySelectorAll('[data-count]')];
    if (!('IntersectionObserver' in window)) return nodes.forEach(run);
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => { if (entry.isIntersecting) { run(entry.target); observer.unobserve(entry.target); } }), { threshold: .6 });
    nodes.forEach((node) => observer.observe(node));
  }

  function initTabs() {
    const root = document.querySelector('[data-tabs]'); if (!root) return;
    const buttons = [...root.querySelectorAll('[data-tab]')]; const panels = [...root.querySelectorAll('[data-panel]')];
    const open = (name, focus = false) => { buttons.forEach((b) => { const active = b.dataset.tab === name; b.setAttribute('aria-selected', String(active)); b.tabIndex = active ? 0 : -1; if (active && focus) b.focus(); }); panels.forEach((p) => { p.hidden = p.dataset.panel !== name; }); };
    buttons.forEach((button, i) => { button.addEventListener('click', () => open(button.dataset.tab)); button.addEventListener('keydown', (event) => { if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return; event.preventDefault(); const next = event.key === 'ArrowRight' ? (i + 1) % buttons.length : (i - 1 + buttons.length) % buttons.length; open(buttons[next].dataset.tab, true); }); });
  }

  function initTiltAndGlow() {
    if (matchMedia('(pointer: fine)').matches && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('[data-tilt]').forEach((card) => { card.addEventListener('pointermove', (e) => { const r = card.getBoundingClientRect(); card.style.setProperty('--rx', `${-((e.clientY-r.top)/r.height-.5)*2.2}deg`); card.style.setProperty('--ry', `${((e.clientX-r.left)/r.width-.5)*2.6}deg`); }); card.addEventListener('pointerleave', () => { card.style.setProperty('--rx', '0deg'); card.style.setProperty('--ry', '0deg'); }); });
      const glow = document.querySelector('.ya-cursor-glow'); if (glow) window.addEventListener('pointermove', (e) => { glow.style.transform = `translate3d(${e.clientX-260}px,${e.clientY-260}px,0)`; }, { passive: true });
    }
  }

  function initProgress() {
    const bar = document.querySelector('.site-scroll-progress span'); if (!bar) return;
    const update = () => { const max = document.documentElement.scrollHeight - innerHeight; bar.style.width = `${max > 0 ? Math.min(100, scrollY / max * 100) : 0}%`; };
    addEventListener('scroll', update, { passive: true }); update();
  }

  async function initRadar() {
    if (!document.querySelector('[data-ya-home]')) return;
    try {
      const [manifestResponse, cyberResponse, cryptoResponse] = await Promise.all([
        fetch('/cyberresearchradar/data/manifest.json', { cache: 'no-cache' }),
        fetch('/cyberresearchradar/data/cyber_opportunities.json', { cache: 'no-cache' }),
        fetch('/cyberresearchradar/data/crypto_opportunities.json', { cache: 'no-cache' })
      ]);
      if (![manifestResponse, cyberResponse, cryptoResponse].every((r) => r.ok)) throw new Error('Radar unavailable');
      const [manifest, cyber, crypto] = await Promise.all([manifestResponse.json(), cyberResponse.json(), cryptoResponse.json()]); state.manifest = manifest;
      const counts = manifest.recordCounts || {}; const put = (id, value) => { const node = document.getElementById(id); if (node && value != null) node.textContent = String(value); };
      put('ya-radar-events', counts.eventsUnique || counts.eventsRaw); put('ya-radar-journals', counts.journals); put('ya-radar-country-count', counts.countries); put('ya-radar-countries', counts.countries);
      const generated = new Date(manifest.generatedAt); put('ya-radar-updated', Number.isNaN(generated.getTime()) ? '—' : new Intl.DateTimeFormat(LOCALES[state.lang], { day: '2-digit', month: 'short', timeZone: 'UTC' }).format(generated));
      const now = Date.now(); const unique = new Map();
      [...cyber, ...crypto].forEach((item) => { if (!item || !item.id || !item.deadline || !['conference','workshop'].includes(item.type)) return; if (item.status && !['verified','watchlist'].includes(item.status)) return; const deadline = new Date(item.deadline).getTime(); if (!Number.isFinite(deadline) || deadline < now) return; const previous = unique.get(item.id); if (!previous || item.status === 'verified') unique.set(item.id, item); });
      state.radar = [...unique.values()].sort((a,b) => new Date(a.deadline)-new Date(b.deadline)); renderRadar();
    } catch (error) { console.warn('Radar preview unavailable', error); renderRadar(); }
  }

  function init() {
    state.lang = initialLang(); state.theme = initialTheme(); applyTheme(state.theme); initControls(); applyLanguage(state.lang); initReveal(); initCounters(); initTabs(); initTiltAndGlow(); initProgress(); initRadar();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true }); else init();
})();
