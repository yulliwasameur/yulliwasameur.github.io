(() => {
  'use strict';

  const VERSION = '3.2';
  const ENDPOINT = 'https://counterapi.com/api/yulliwasameur.github.io/visit/cyberresearchradar?unique=true';
  const COPY = {
    fr: { version: `v${VERSION} · catalogue élargi`, visitors: 'visiteurs uniques estimés', title: 'Compteur dédupliqué par empreinte anonyme ; aucune identité n’est affichée.' },
    en: { version: `v${VERSION} · expanded catalogue`, visitors: 'estimated unique visitors', title: 'Counter deduplicated by anonymous hash; no identity is displayed.' },
    kab: { version: `v${VERSION} · akaram yewsaɛ`, visitors: 'inebgawen imezliyen (asumer)', title: 'Asmiḍan yettwasemmezdi s udlis uffir; ulac tamagit i d-yettwaseknen.' },
  };

  const language = () => {
    const query = new URLSearchParams(location.search).get('lang');
    if (['fr', 'en', 'kab'].includes(query)) return query;
    const pressed = document.querySelector('[data-lang][aria-pressed="true"]');
    return ['fr', 'en', 'kab'].includes(pressed?.dataset.lang) ? pressed.dataset.lang : 'fr';
  };

  function addVersion() {
    if (document.querySelector('.radar-version-badge')) return;
    const tools = document.querySelector('.header-tools') || document.querySelector('.topbar');
    if (!tools) return;
    const badge = document.createElement('span');
    badge.className = 'radar-version-badge';
    badge.dataset.radarVersion = VERSION;
    tools.prepend(badge);
    const translate = () => { badge.textContent = COPY[language()].version; badge.setAttribute('aria-label', COPY[language()].version); };
    translate();
    document.querySelectorAll('[data-lang]').forEach((button) => button.addEventListener('click', () => setTimeout(translate, 0)));
  }

  function addCounter() {
    if (document.querySelector('.radar-unique-counter')) return;
    const widget = document.createElement('aside');
    widget.className = 'radar-unique-counter';
    widget.setAttribute('role', 'status');
    widget.setAttribute('aria-live', 'polite');
    const dot = document.createElement('i'); dot.setAttribute('aria-hidden', 'true');
    const count = document.createElement('strong'); count.textContent = '—';
    const label = document.createElement('span');
    widget.append(dot, count, label);
    document.body.append(widget);

    const translate = () => {
      const copy = COPY[language()];
      label.textContent = copy.visitors;
      widget.title = copy.title;
      widget.setAttribute('aria-label', `${count.textContent} ${copy.visitors}`);
    };
    translate();
    document.querySelectorAll('[data-lang]').forEach((button) => button.addEventListener('click', () => setTimeout(translate, 0)));

    fetch(ENDPOINT, { cache: 'no-store', headers: { Accept: 'application/json' } })
      .then((response) => { if (!response.ok) throw new Error(String(response.status)); return response.json(); })
      .then((payload) => {
        const value = payload?.count ?? payload?.data?.count ?? payload?.value;
        if (!Number.isFinite(Number(value))) throw new Error('count missing');
        count.textContent = new Intl.NumberFormat(language() === 'en' ? 'en-GB' : 'fr-FR').format(Number(value));
        widget.classList.add('is-ready');
        translate();
      })
      .catch(() => widget.classList.add('is-unavailable'));
  }

  function init() {
    document.documentElement.dataset.radarVersion = VERSION;
    addVersion();
    addCounter();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
