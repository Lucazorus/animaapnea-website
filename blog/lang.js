(function () {
  var LANGS = {
    en: { flag: '🇬🇧', label: 'EN' },
    fr: { flag: '🇫🇷', label: 'FR' },
    es: { flag: '🇪🇸', label: 'ES' },
    de: { flag: '🇩🇪', label: 'DE' },
    it: { flag: '🇮🇹', label: 'IT' },
    pt: { flag: '🇧🇷', label: 'PT' },
    ja: { flag: '🇯🇵', label: 'JA' },
    zh: { flag: '🇨🇳', label: 'ZH' }
  };

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
    var browserLang = (navigator.language || '').slice(0, 2);
    var target = stored || (LANGS[browserLang] ? browserLang : null);
    if (target && target !== currentLang && LANGS[target]) {
      var hreflang = document.querySelector('link[hreflang="' + target + '"]');
      if (hreflang && hreflang.href !== window.location.href) {
        window.location.replace(hreflang.href);
        return;
      }
    }
    // Save current lang if arriving from direct URL
    if (!stored) localStorage.setItem('lang', currentLang);
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
      // On article pages, go to hreflang equivalent
      var hreflang = document.querySelector('link[hreflang="' + code + '"]');
      if (hreflang) {
        window.location.href = hreflang.href;
      } else {
        // On index page, just update button label and close
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
