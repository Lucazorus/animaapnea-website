/* Anima Apnea — article enhancements: reading progress, TOC scrollspy,
   theme-aware SVG charts and the CO2/O2 table calculator.
   Charts read their data and translated labels from data-* attributes,
   so the same script serves every language. */
(function () {
  var NS = 'http://www.w3.org/2000/svg';

  function el(name, attrs, text) {
    var n = document.createElementNS(NS, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }

  function fmt(s) {
    s = Math.round(s);
    var m = Math.floor(s / 60), r = s % 60;
    return m + ':' + (r < 10 ? '0' : '') + r;
  }

  function json(node, key, fallback) {
    try { return JSON.parse(node.getAttribute(key)); } catch (e) { return fallback; }
  }

  // ── Reading progress ──
  var bar = document.querySelector('.read-progress');
  var body = document.querySelector('.article-body');
  function onScroll() {
    if (!bar || !body) return;
    var r = body.getBoundingClientRect();
    var total = r.height - window.innerHeight;
    var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
    bar.style.width = (p * 100) + '%';
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ── TOC scrollspy ──
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a[href^="#"]'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('active'); });
        var a = map[e.target.id];
        if (a) a.classList.add('active');
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) {
      var t = document.getElementById(id);
      if (t) io.observe(t);
    });
  }

  // ── Chart: table timeline (one row per round: rest then hold) ──
  function drawTimeline(host, rounds, L, holdClass) {
    host.innerHTML = '';
    var W = 640, rowH = 26, gap = 8, left = 34, right = 56, top = 8;
    var H = top + rounds.length * (rowH + gap) + 26;
    var maxT = 0;
    rounds.forEach(function (r) { maxT = Math.max(maxT, r[0] + r[1]); });
    var step = maxT > 360 ? 120 : 60;
    maxT = Math.ceil(maxT / step) * step;
    var sx = (W - left - right) / maxT;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': L.aria || '' });

    for (var t = 0; t <= maxT; t += step) {
      var x = left + t * sx;
      svg.appendChild(el('line', { x1: x, x2: x, y1: top - 4, y2: H - 22, 'class': 'c-grid' }));
      svg.appendChild(el('text', { x: x, y: H - 6, 'text-anchor': 'middle', 'class': 'c-tick' }, fmt(t)));
    }

    rounds.forEach(function (r, i) {
      var y = top + i * (rowH + gap);
      svg.appendChild(el('text', { x: 0, y: y + rowH / 2 + 4, 'class': 'c-tick' }, (L.round || 'R') + (i + 1)));
      var rw = r[0] * sx, hw = r[1] * sx;
      svg.appendChild(el('rect', { x: left, y: y, width: Math.max(rw - 2, 1), height: rowH, rx: 5, 'class': 'c-rest' }));
      svg.appendChild(el('rect', { x: left + rw, y: y, width: hw, height: rowH, rx: 5, 'class': holdClass }));
      if (rw > 38) svg.appendChild(el('text', { x: left + 8, y: y + rowH / 2 + 4, 'class': 'c-tick' }, fmt(r[0])));
      svg.appendChild(el('text', { x: left + rw + hw + 8, y: y + rowH / 2 + 4, 'class': 'c-lab' }, fmt(r[1])));
    });
    host.appendChild(svg);
  }

  // ── Chart: blood gases during a static breath-hold (schematic) ──
  function drawBloodGas(host, L) {
    var W = 640, H = 300, l = 44, r = 20, t = 24, b = 40;
    var iw = W - l - r, ih = H - t - b;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': L.aria || '' });
    var bp = 0.52; // physiological breaking point (fraction of hold)

    // struggle-phase zone
    svg.appendChild(el('rect', { x: l + bp * iw, y: t, width: (1 - bp) * iw, height: ih, 'class': 'c-zone' }));
    for (var g = 0; g <= 4; g++) {
      var gy = t + g * ih / 4;
      svg.appendChild(el('line', { x1: l, x2: W - r, y1: gy, y2: gy, 'class': 'c-grid' }));
    }
    svg.appendChild(el('line', { x1: l, x2: W - r, y1: t + ih, y2: t + ih, 'class': 'c-axis' }));

    function path(fn) {
      var d = '';
      for (var i = 0; i <= 60; i++) {
        var p = i / 60;
        d += (i ? 'L' : 'M') + (l + p * iw).toFixed(1) + ',' + (t + (1 - fn(p)) * ih).toFixed(1);
      }
      return d;
    }
    var co2 = function (p) { return 0.18 + 0.7 * Math.pow(p, 0.85); };
    var o2 = function (p) { return 0.92 - 0.06 * p - 0.62 * Math.pow(Math.max(0, p - 0.45) / 0.55, 2.2); };

    svg.appendChild(el('path', { d: path(co2) + 'L' + (l + iw) + ',' + (t + ih) + 'L' + l + ',' + (t + ih) + 'Z', 'class': 'c-co2-area' }));
    svg.appendChild(el('path', { d: path(co2), 'class': 'c-co2-line' }));
    svg.appendChild(el('path', { d: path(o2), 'class': 'c-o2-line' }));

    // markers
    var urge = 0.3, ux = l + urge * iw, bx = l + bp * iw;
    svg.appendChild(el('line', { x1: ux, x2: ux, y1: t, y2: t + ih, 'class': 'c-warn', style: 'opacity:.55' }));
    svg.appendChild(el('line', { x1: bx, x2: bx, y1: t, y2: t + ih, 'class': 'c-warn' }));
    svg.appendChild(el('text', { x: ux + 6, y: t + 14, 'class': 'c-warn-t', style: 'opacity:.75' }, L.urge || ''));
    svg.appendChild(el('text', { x: bx + 6, y: t + 14, 'class': 'c-warn-t' }, L.bp || ''));

    // phase labels
    svg.appendChild(el('text', { x: l + bp * iw / 2, y: H - 12, 'text-anchor': 'middle', 'class': 'c-lab' }, L.easy || ''));
    svg.appendChild(el('text', { x: l + (bp + (1 - bp) / 2) * iw, y: H - 12, 'text-anchor': 'middle', 'class': 'c-lab' }, L.struggle || ''));
    svg.appendChild(el('text', { x: l - 10, y: t + ih + 4, 'text-anchor': 'end', 'class': 'c-tick' }, '0'));
    svg.appendChild(el('text', { x: W - r, y: H - 26, 'text-anchor': 'end', 'class': 'c-tick' }, L.time || ''));

    // end labels on curves
    svg.appendChild(el('text', { x: W - r - 4, y: t + (1 - co2(1)) * ih - 8, 'text-anchor': 'end', 'class': 'c-lab-strong', style: 'fill:var(--co2)' }, L.co2 || 'CO₂'));
    svg.appendChild(el('text', { x: W - r - 4, y: t + (1 - o2(1)) * ih + 18, 'text-anchor': 'end', 'class': 'c-lab-strong', style: 'fill:var(--o2)' }, L.o2 || 'O₂'));
    host.appendChild(svg);
  }

  // ── Chart: weekly load bars ──
  function drawWeek(host, days, L) {
    var W = 640, H = 170, l = 8, r = 8, t = 10, b = 44;
    var n = days.length, slot = (W - l - r) / n, bw = Math.min(54, slot - 14), ih = H - t - b;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': L.aria || '' });
    svg.appendChild(el('line', { x1: l, x2: W - r, y1: t + ih, y2: t + ih, 'class': 'c-axis' }));
    days.forEach(function (d, i) {
      var cx = l + slot * i + slot / 2;
      var h = Math.max(4, d.v * ih);
      var cls = d.k === 'co2' ? 'c-hold' : d.k === 'o2' ? 'c-hold-o2' : 'c-rest';
      svg.appendChild(el('rect', { x: cx - bw / 2, y: t + ih - h, width: bw, height: h, rx: 6, 'class': cls }));
      svg.appendChild(el('text', { x: cx, y: H - 24, 'text-anchor': 'middle', 'class': 'c-lab' }, d.d));
      svg.appendChild(el('text', { x: cx, y: H - 8, 'text-anchor': 'middle', 'class': 'c-tick' }, d.t || ''));
    });
    host.appendChild(svg);
  }

  // ── Calculator (mirrors the Anima app's TableAdaptation formulas) ──
  function snap15(v) { return Math.round(v / 15) * 15; }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }

  function co2Table(pr) {
    var hold = clamp(snap15(pr * 0.5), 30, 240);
    var rest = clamp(snap15(pr * 0.67), 60, 300);
    var rounds = [];
    for (var i = 0; i < 8; i++) rounds.push([clamp(rest - i * 15, 10, 300), hold]);
    return rounds;
  }
  function o2Table(pr) {
    var start = clamp(snap15(pr * 0.33), 30, 180);
    var end = Math.max(start, snap15(pr * 0.8));
    var stepH = (end - start) / 7, rounds = [];
    for (var i = 0; i < 8; i++) rounds.push([120, Math.round(start + i * stepH)]);
    return rounds;
  }

  document.querySelectorAll('[data-calc]').forEach(function (c) {
    var kind = c.getAttribute('data-calc');
    var L = json(c, 'data-labels', {});
    var range = c.querySelector('input[type=range]');
    var out = c.querySelector('.calc-pr');
    var chart = c.querySelector('.calc-chart');
    var cells = c.querySelectorAll('.calc-out b');
    function update() {
      var pr = +range.value;
      out.textContent = fmt(pr);
      var rounds = kind === 'o2' ? o2Table(pr) : co2Table(pr);
      var total = rounds.reduce(function (s, r) { return s + r[0] + r[1]; }, 0);
      if (kind === 'o2') {
        cells[0].textContent = fmt(rounds[0][1]) + ' → ' + fmt(rounds[7][1]);
        cells[1].textContent = fmt(rounds[0][0]);
      } else {
        cells[0].textContent = fmt(rounds[0][1]);
        cells[1].textContent = fmt(rounds[0][0]) + ' → ' + fmt(rounds[7][0]);
      }
      cells[2].textContent = '≈ ' + Math.round(total / 60) + ' ' + (L.min || 'min');
      drawTimeline(chart, rounds, L, kind === 'o2' ? 'c-hold-o2' : 'c-hold');
    }
    range.addEventListener('input', update);
    update();
  });

  document.querySelectorAll('[data-chart]').forEach(function (host) {
    var type = host.getAttribute('data-chart');
    var L = json(host, 'data-labels', {});
    if (type === 'timeline') drawTimeline(host, json(host, 'data-rounds', []), L, host.getAttribute('data-kind') === 'o2' ? 'c-hold-o2' : 'c-hold');
    if (type === 'blood-gas') drawBloodGas(host, L);
    if (type === 'week') drawWeek(host, json(host, 'data-days', []), L);
  });
})();
