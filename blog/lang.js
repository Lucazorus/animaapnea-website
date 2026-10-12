(function () {
  var LANGS = {
    en: { flag: '🇬🇧', label: 'EN', name: 'English' },
    fr: { flag: '🇫🇷', label: 'FR', name: 'Français' },
    es: { flag: '🇪🇸', label: 'ES', name: 'Español' },
    de: { flag: '🇩🇪', label: 'DE', name: 'Deutsch' },
    it: { flag: '🇮🇹', label: 'IT', name: 'Italiano' },
    pt: { flag: '🇧🇷', label: 'PT', name: 'Português' },
    ja: { flag: '🇯🇵', label: 'JA', name: '日本語' },
    zh: { flag: '🇨🇳', label: 'ZH', name: '中文' },
    da: { flag: '🇩🇰', label: 'DA', name: 'Dansk' },
    nl: { flag: '🇳🇱', label: 'NL', name: 'Nederlands' },
    hi: { flag: '🇮🇳', label: 'HI', name: 'हिन्दी' },
    id: { flag: '🇮🇩', label: 'ID', name: 'Bahasa Indonesia' },
    th: { flag: '🇹🇭', label: 'TH', name: 'ไทย' },
    vi: { flag: '🇻🇳', label: 'VI', name: 'Tiếng Việt' }
  };

  // Extract pathname from an absolute URL (handles www vs non-www)
  function getPath(url) {
    try { return new URL(url).pathname; } catch (e) { return url; }
  }

  // ── Detect current lang from canonical URL ──
  function getCurrentLang() {
    var canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) return null;
    var m = canonical.href.match(/\/blog\/([a-z]{2})\//);
    return m ? m[1] : null;
  }

  var currentLang = getCurrentLang(); // null on index page

  // ── Auto-redirect to stored language (article pages only) ──
  if (currentLang) {
    var stored = localStorage.getItem('lang');
    // If stored lang came from browser detection (not user choice), ignore it
    // User choice is flagged by 'lang_explicit' key
    var isExplicit = localStorage.getItem('lang_explicit') === '1';
    if (stored && !isExplicit) stored = null;
    // Only redirect if user explicitly chose a language (stored), not from browser detection
    if (stored && stored !== currentLang && LANGS[stored]) {
      var hreflang = document.querySelector('link[hreflang="' + stored + '"]');
      // Compare paths only — avoids www vs non-www mismatch
      if (hreflang && getPath(hreflang.href) !== window.location.pathname) {
        window.location.replace(hreflang.href);
        return;
      }
    }
  }

  // ── Build language selector in nav ──
  var nav = document.querySelector('.blog-nav');
  if (!nav) return;

  var activeLang = currentLang || localStorage.getItem('lang') || 'en';
  var activeInfo = LANGS[activeLang] || LANGS['en'];

  var wrapper = document.createElement('div');
  wrapper.className = 'blog-lang-select';

  var btn = document.createElement('button');
  btn.className = 'blog-lang-btn';
  btn.setAttribute('aria-label', 'Select language');
  btn.innerHTML = '<span>' + activeInfo.label + '</span>';

  var dropdown = document.createElement('div');
  dropdown.className = 'blog-lang-dropdown';

  Object.keys(LANGS).forEach(function (code) {
    var info = LANGS[code];
    var a = document.createElement('a');
    a.href = '#';
    a.textContent = info.name || info.label;
    if (code === activeLang) a.className = 'active';

    a.addEventListener('click', function (e) {
      e.preventDefault();
      localStorage.setItem('lang', code);
      localStorage.setItem('lang_explicit', '1'); // mark as explicit user choice
      var hreflang = document.querySelector('link[hreflang="' + code + '"]');
      if (hreflang) {
        window.location.href = hreflang.href;
      } else {
        // Index page: just update button and close
        btn.innerHTML = '<span>' + info.label + '</span>';
        dropdown.classList.remove('open');
      }
    });

    dropdown.appendChild(a);
  });

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    dropdown.classList.toggle('open');
  });

  document.addEventListener('click', function () {
    dropdown.classList.remove('open');
  });

  wrapper.appendChild(btn);
  wrapper.appendChild(dropdown);

  // ── Theme toggle ──
  var themeBtn = document.createElement('button');
  themeBtn.className = 'blog-theme-btn';
  themeBtn.setAttribute('aria-label', 'Toggle theme');

  var html = document.documentElement;
  var storedTheme = localStorage.getItem('theme');
  var sysPref = window.matchMedia('(prefers-color-scheme: light)').matches;
  var isSepia = storedTheme ? storedTheme === 'sepia' : sysPref;

  function applyTheme(sepia) {
    html.classList.toggle('sepia', sepia);
    themeBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  }
  applyTheme(isSepia);

  themeBtn.addEventListener('click', function () {
    var next = !html.classList.contains('sepia');
    applyTheme(next);
    localStorage.setItem('theme', next ? 'sepia' : 'dark');
  });

  var navRight = document.createElement('div');
  navRight.style.cssText = 'display:flex;align-items:center;gap:0.5rem;';
  navRight.appendChild(themeBtn);
  navRight.appendChild(wrapper);
  nav.appendChild(navRight);
})();
