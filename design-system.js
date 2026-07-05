/* binah design system — scroll reveal (no external libs) */
(function () {
  var els = document.querySelectorAll('.ds-reveal');
  if (!('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('ds-in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) {
        e.target.classList.add('ds-in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  els.forEach(function (el) { io.observe(el); });
})();
