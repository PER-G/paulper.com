// Paulper.com – Navigation, Einblend-Animation, Bild-Lightbox
(function () {
  document.documentElement.classList.add('js');

  // Navigation: Hintergrund beim Scrollen, Mobilmenü
  var nav = document.querySelector('.nav');
  var onScroll = function () { nav.classList.toggle('scrolled', window.scrollY > 20); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  var toggle = document.querySelector('.nav-toggle');
  toggle.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });

  // Einblenden beim Scrollen
  var targets = document.querySelectorAll('.reveal, .card-body > h1, .card-body > p');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(function (t) { t.classList.add('in'); });
  }
  // Inhalte in aufgeklappten Bereichen sofort zeigen
  document.querySelectorAll('details').forEach(function (d) {
    d.addEventListener('toggle', function () {
      d.querySelectorAll('.reveal').forEach(function (r) { r.classList.add('in'); });
    });
  });

  // Lightbox für Bilder
  var lb = document.querySelector('.lightbox');
  var lbImg = lb.querySelector('img');
  var list = [], idx = 0;
  function show(i) { idx = (i + list.length) % list.length; lbImg.src = list[idx].currentSrc || list[idx].src; }
  function close() { lb.hidden = true; document.body.style.overflow = ''; }
  document.addEventListener('click', function (e) {
    var im = e.target.closest('img[data-lightbox]');
    if (!im) return;
    var group = im.closest('.gallery, .smart, .grid-layout') || document;
    list = Array.prototype.slice.call(group.querySelectorAll('img[data-lightbox]'));
    show(list.indexOf(im));
    lb.hidden = false;
    document.body.style.overflow = 'hidden';
  });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function () { show(idx - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { show(idx + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  });
})();
