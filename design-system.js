/* binah design system — scroll reveal + count-up (no external libs) */
(function () {
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Count-up: <element data-count="12"> animates 0 → 12 when visible */
  function countUp(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    if (reduced) { el.textContent = target; return; }
    var dur = 1500, start = null;
    function tick(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  var reveals = document.querySelectorAll('.ds-reveal');
  var counters = document.querySelectorAll('[data-count]');

  if (!('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('ds-in'); });
    counters.forEach(function (el) { el.textContent = el.getAttribute('data-count'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      if (e.target.hasAttribute('data-count')) countUp(e.target);
      else e.target.classList.add('ds-in');
      io.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  reveals.forEach(function (el) { io.observe(el); });
  counters.forEach(function (el) { io.observe(el); });
})();
