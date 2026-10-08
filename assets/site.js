// Paulper.com – Navigation, Seitenwechsel-Effekte, Einblenden, Lightbox
(function () {
  var root = document.documentElement;
  root.classList.add('js');
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------------------------------------------------------- Navigation
  var nav = document.querySelector('.nav');
  var toggle = document.querySelector('.nav-toggle');
  toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });

  // Aufklappmenüs: nicht über den Fensterrand hinausragen lassen
  document.querySelectorAll('.has-menu').forEach(function (item) {
    item.addEventListener('mouseenter', function () {
      var fly = item.querySelector('.flyout');
      fly.style.setProperty('--shift', '0px');
      var r = fly.getBoundingClientRect(), pad = 12, shift = 0;
      if (r.right > innerWidth - pad) shift = innerWidth - pad - r.right;
      if (r.left + shift < pad) shift = pad - r.left;
      fly.style.setProperty('--shift', shift + 'px');
    });
  });

  // ---------------------------------------------------------- Seitenwechsel-Effekte
  var fx = document.createElement('div');
  fx.id = 'fx';
  document.body.appendChild(fx);

  function show(html, color) {
    fx.style.setProperty('--fc', color || '#2997FF');
    fx.innerHTML = html;
    fx.classList.add('run');
  }
  function rnd(a, b) { return a + Math.random() * (b - a); }

  var FX = {
    start: function () {
      show('<div class="fx-veil"></div><div class="fx-ring"></div><div class="fx-ring b"></div><div class="fx-ring c"></div>', '#2997FF');
    },
    foto: function () {
      var blades = '';
      for (var i = 0; i < 6; i++) {
        blades += '<path transform="rotate(' + (i * 60) + ' 500 500)" d="M500 500 L1000 210 L1000 -200 L380 -200 Z" fill="#050507" stroke="#2a2a30" stroke-width="3"/>';
      }
      show('<div class="fx-shutter"><svg viewBox="0 0 1000 1000">' + blades + '</svg></div><div class="fx-flash"></div>', '#fff');
    },
    reise: function () {
      show('<div class="fx-veil"></div><svg class="fx-plane" viewBox="0 0 1200 700" preserveAspectRatio="none">' +
        '<defs><linearGradient id="fxTrail" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#9fd0ff"/></linearGradient></defs>' +
        '<path class="trail" d="M -60 620 C 300 520, 600 140, 1260 60"/>' +
        '<g class="jet"><path d="M0 -6 L34 -2 L44 0 L34 2 L0 6 L-4 0 Z M10 0 L-6 -22 L2 -22 L22 -1 Z M10 0 L-6 22 L2 22 L22 1 Z M-2 0 L-12 -9 L-8 -9 L4 -1 Z M-2 0 L-12 9 L-8 9 L4 1 Z" fill="#fff" transform="scale(1.6)"/></g>' +
        '</svg>', '#2997FF');
    },
    auto: function () {
      var h = '<div class="fx-dim"></div>';
      var cols = ['#ffffff', '#2997FF', '#FF7A5C', '#BF5AF2', '#9fd0ff'];
      for (var i = 0; i < 26; i++) {
        h += '<span class="fx-streak" style="top:' + rnd(4, 96).toFixed(1) + '%;height:' + (Math.random() < .3 ? 3 : 1.5) +
          'px;--sc:' + cols[i % cols.length] + ';animation-delay:' + rnd(0, .25).toFixed(2) + 's;width:' + rnd(20, 50).toFixed(0) + '%"></span>';
      }
      show(h, '#2997FF');
    },
    ueber: function () {
      show('<div class="fx-veil"></div><svg class="fx-db" viewBox="0 0 300 120"><rect x="90" y="52" width="120" height="16" rx="8" fill="#9AA5AB"/><rect x="52" y="14" width="26" height="92" rx="8" fill="#D6DEE2"/><rect x="24" y="28" width="24" height="64" rx="7" fill="#AEB9BD"/><rect x="222" y="14" width="26" height="92" rx="8" fill="#D6DEE2"/><rect x="252" y="28" width="24" height="64" rx="7" fill="#AEB9BD"/></svg>', '#30D158');
      setTimeout(function () {
        document.body.classList.add('shake');
        setTimeout(function () { document.body.classList.remove('shake'); }, 360);
      }, 500);
    },
    games: function () {
      var h = '<div class="fx-veil"></div>';
      var cols = ['#16FFBB', '#29DDDA', '#2997FF', '#BF5AF2', '#FF7A5C', '#F2E14C'];
      for (var i = 0; i < 46; i++) {
        var a = Math.random() * Math.PI * 2, d = rnd(18, 70);
        h += '<span class="fx-px" style="background:' + cols[i % cols.length] + ';--dx:' + (Math.cos(a) * d).toFixed(1) + 'vmax;--dy:' +
          (Math.sin(a) * d).toFixed(1) + 'vmax;--r:' + rnd(-180, 180).toFixed(0) + 'deg;animation-delay:' + rnd(0, .12).toFixed(2) + 's"></span>';
      }
      show(h, '#16FFBB');
    },
    kontakt: function () {
      show('<svg class="fx-ecg" viewBox="0 0 1200 200" preserveAspectRatio="none"><path d="M0 100 L140 100 L158 100 L172 74 L186 126 L200 100 L330 100 L365 100 L380 26 L400 168 L420 100 L555 100 L595 100 L610 72 L625 122 L640 100 L780 100 L820 100 L836 20 L856 172 L876 100 L1020 100 L1055 100 L1070 70 L1085 124 L1100 100 L1200 100"/></svg>', '#BF5AF2');
    },
    fitness: function () {
      show('<div class="fx-veil"></div><div class="fx-ring"></div><div class="fx-ring b"></div><svg class="fx-ecg" viewBox="0 0 1200 200" preserveAspectRatio="none"><path d="M0 100 L300 100 L330 100 L350 60 L370 140 L390 100 L520 100 L560 100 L580 20 L605 180 L630 100 L780 100 L820 100 L840 64 L860 136 L880 100 L1200 100"/></svg>', '#30D158');
    },
    impressum: function () {
      show('<div class="fx-veil"></div><div class="fx-ring"></div><div class="fx-ring b"></div>', '#86868B');
    }
  };
  // Wie lange der Effekt läuft, bevor die neue Seite geladen wird
  var WAIT = { start: 420, foto: 520, reise: 620, auto: 480, ueber: 760, games: 440, kontakt: 520, impressum: 380, fitness: 560 };

  function keyFor(path) {
    path = decodeURI(path);
    if (path === '/' || path === '/index.html') return 'start';
    if (path.indexOf('/per-fotografie') === 0) return 'foto';
    if (path.indexOf('/per-entdecke') === 0) return 'reise';
    if (path.indexOf('/per-auto') === 0) return 'auto';
    if (path.indexOf('/per-über') === 0) return 'ueber';
    if (path.indexOf('/per-games') === 0) return 'games';
    if (path.indexOf('/per-blog') === 0) return 'kontakt';
    if (path.indexOf('/per-impressum') === 0) return 'impressum';
    if (path.indexOf('/per-fitness') === 0) return 'fitness';
    return null;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || a.target === '_blank') return;
    var url = new URL(a.href, location.href);
    if (url.origin !== location.origin) return;
    if (url.pathname === location.pathname) return; // Anker auf derselben Seite
    var key = keyFor(url.pathname);
    if (!key || reduced) return;
    e.preventDefault();
    nav.classList.remove('open');
    FX[key]();
    try { sessionStorage.setItem('per-arrive', key); } catch (err) {}
    setTimeout(function () { location.href = url.href; }, WAIT[key] || 450);
  });

  // Ziele beim Überfahren vorladen, damit der Wechsel flüssig ist
  var pre = {};
  document.addEventListener('pointerover', function (e) {
    var a = e.target.closest('a[href^="/"]');
    if (!a || pre[a.href]) return;
    pre[a.href] = 1;
    var l = document.createElement('link');
    l.rel = 'prefetch'; l.href = a.href;
    document.head.appendChild(l);
  });

  // Ankunft: Inhalt weich einblenden
  try {
    if (sessionStorage.getItem('per-arrive')) {
      sessionStorage.removeItem('per-arrive');
      document.body.classList.add('arriving');
      setTimeout(function () { document.body.classList.remove('arriving'); }, 1000);
    }
  } catch (err) {}
  // Zurück-Taste (bfcache): Effekt-Ebene entfernen
  window.addEventListener('pageshow', function () { fx.classList.remove('run'); fx.innerHTML = ''; });

  // ---------------------------------------------------------- Einblenden beim Scrollen
  var targets = document.querySelectorAll('.card, .reveal, .card-body > .h1, .card-body > p, .card-body > .eyebrow');
  if ('IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add(e.target.classList.contains('card') ? 'in-view' : 'in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .04 });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add(t.classList.contains('card') ? 'in-view' : 'in'); });
  }
  document.querySelectorAll('details').forEach(function (d) {
    d.addEventListener('toggle', function () {
      d.querySelectorAll('.reveal').forEach(function (r) { r.classList.add('in'); });
    });
  });

  // ---------------------------------------------------------- Lightbox
  var lb = document.querySelector('.lightbox');
  var lbImg = lb.querySelector('img');
  var list = [], idx = 0;
  function showImg(i) { idx = (i + list.length) % list.length; lbImg.src = list[idx].currentSrc || list[idx].src; }
  function close() { lb.hidden = true; document.body.style.overflow = ''; }
  document.addEventListener('click', function (e) {
    var im = e.target.closest('img[data-lightbox]');
    if (!im) return;
    var group = im.closest('.gallery, .smart, .grid-layout') || document;
    list = Array.prototype.slice.call(group.querySelectorAll('img[data-lightbox]'));
    showImg(list.indexOf(im));
    lb.hidden = false;
    document.body.style.overflow = 'hidden';
  });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function () { showImg(idx - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { showImg(idx + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') showImg(idx - 1);
    if (e.key === 'ArrowRight') showImg(idx + 1);
  });
})();
