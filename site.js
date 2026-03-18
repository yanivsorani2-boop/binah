/* ── Shared site JS — binah ── */

/* Theme toggle */
function toggleTheme() {
  var html = document.documentElement;
  var isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) { html.removeAttribute('data-theme'); localStorage.setItem('binah-theme','dark'); }
  else { html.setAttribute('data-theme','light'); localStorage.setItem('binah-theme','light'); }
}

/* Scroll reveal */
(function() {
  var els = document.querySelectorAll('.reveal');
  if (!window.IntersectionObserver) {
    els.forEach(function(el) { el.classList.add('visible'); });
    return;
  }
  var io = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); }
    });
  }, { threshold: 0.06 });
  els.forEach(function(el) { io.observe(el); });
})();

/* Back to top */
(function() {
  var btn = document.getElementById('back-to-top');
  if (!btn) return;
  window.addEventListener('scroll', function() {
    if (window.scrollY > 400) btn.classList.add('visible');
    else btn.classList.remove('visible');
  }, { passive: true });
})();

/* Mobile hamburger */
function toggleMenu() {
  var nav = document.getElementById('main-nav');
  var btn = document.getElementById('hamburger');
  if (nav) nav.classList.toggle('open');
  if (btn) btn.classList.toggle('open');
}

/* Close menu when nav link is tapped */
document.addEventListener('DOMContentLoaded', function() {
  var nav = document.getElementById('main-nav');
  var btn = document.getElementById('hamburger');
  if (nav) {
    nav.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() {
        nav.classList.remove('open');
        if (btn) btn.classList.remove('open');
      });
    });
  }
  /* Close menu on outside tap */
  document.addEventListener('click', function(e) {
    if (nav && nav.classList.contains('open') &&
        !nav.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
      nav.classList.remove('open');
      if (btn) btn.classList.remove('open');
    }
  });
});
