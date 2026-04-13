(function () {
  var LANGS = {
    en: { flag: '🇬🇧', label: 'EN' },
    fr: { flag: '🇫🇷', label: 'FR' },
    es: { flag: '🇪🇸', label: 'ES' },
    de: { flag: '🇩🇪', label: 'DE' },
    it: { flag: '🇮🇹', label: 'IT' },
    pt: { flag: '🇧🇷', label: 'PT' },
    ja: { flag: '🇯🇵', label: 'JA' },
    zh: { flag: '🇨🇳', label: 'ZH' },
    da: { flag: '🇩🇰', label: 'DA' },
    nl: { flag: '🇳🇱', label: 'NL' },
    hi: { flag: '🇮🇳', label: 'HI' },
    id: { flag: '🇮🇩', label: 'ID' },
    th: { flag: '🇹🇭', label: 'TH' },
    vi: { flag: '🇻🇳', label: 'VI' }
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
  btn.innerHTML = activeInfo.flag + ' <span>' + activeInfo.label + '</span>';

  var dropdown = document.createElement('div');
  dropdown.className = 'blog-lang-dropdown';

  Object.keys(LANGS).forEach(function (code) {
    var info = LANGS[code];
    var a = document.createElement('a');
    a.href = '#';
    a.textContent = info.flag + '  ' + info.label;
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
        btn.innerHTML = info.flag + ' <span>' + info.label + '</span>';
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
  nav.appendChild(wrapper);
})();
