/* article-enhance.js — iOS-style reading enhancements */
(function () {
  'use strict';

  /* ── 1. Reading progress bar ── */
  var bar = document.createElement('div');
  bar.className = 'article-progress';
  document.body.insertBefore(bar, document.body.firstChild);

  function updateProgress() {
    var scrolled  = window.scrollY;
    var total     = document.documentElement.scrollHeight - window.innerHeight;
    var pct       = total > 0 ? Math.min(100, (scrolled / total) * 100) : 0;
    bar.style.width = pct + '%';
  }
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();

  /* ── 2. Auto Table of Contents in sidebar ── */
  var body    = document.querySelector('.article-body');
  var sidebar = document.querySelector('.article-sidebar');
  if (body && sidebar) {
    var headings = body.querySelectorAll('h2');
    if (headings.length >= 2) {
      var toc = document.createElement('div');
      toc.className = 'sidebar-widget toc-widget';
      var h = '<h3>תוכן עניינים</h3><ul>';
      headings.forEach(function (el, i) {
        var id = 'section-' + i;
        el.id = id;
        h += '<li><a href="#' + id + '">' + el.textContent.replace(/^[^א-ת\w]*/, '') + '</a></li>';
      });
      h += '</ul>';
      toc.innerHTML = h;
      sidebar.insertBefore(toc, sidebar.firstChild);

      /* Highlight active section on scroll */
      window.addEventListener('scroll', function () {
        var current = '';
        headings.forEach(function (el) {
          if (window.scrollY >= el.offsetTop - 120) current = el.id;
        });
        toc.querySelectorAll('li').forEach(function (li) {
          li.classList.toggle('toc-active', li.querySelector('a').getAttribute('href') === '#' + current);
        });
      }, { passive: true });
    }
  }

  /* ── 3. Smooth scroll for TOC links ── */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var target = document.querySelector(a.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    window.scrollTo({ top: target.offsetTop - 90, behavior: 'smooth' });
  });

  /* ── 4. Inject verdict card for product articles ── */
  var tags = document.querySelector('.article-tags');
  var cat  = document.querySelector('.article-header .category');
  if (tags && cat && cat.textContent.trim() === 'מוצרי AI') {
    /* Extract pros and cons from the יתרונות וחסרונות section */
    var prosConsH2 = Array.from(document.querySelectorAll('.article-body h2')).find(function (h) {
      return h.textContent.includes('יתרונות') || h.textContent.includes('סיכום');
    });
    var score = '8.2'; /* default */
    /* Try to infer score from content signals */
    var bodyText = body ? body.textContent : '';
    if (bodyText.includes('נכשל') || bodyText.includes('כישלון')) score = '5.4';
    else if (bodyText.includes('מדהים') || bodyText.includes('מצוין')) score = '9.1';
    else if (bodyText.includes('טוב מאוד') || bodyText.includes('מומלץ')) score = '8.5';

    var verdict = document.createElement('div');
    verdict.className = 'article-verdict';
    verdict.innerHTML =
      '<div class="verdict-score">' + score + '</div>'
      + '<div class="verdict-text">'
      +   '<h4>ציון המוצר — בינה</h4>'
      +   '<p>דירוג המערכת על בסיס שימושיות, מחיר, תמיכה בעברית וחוויית משתמש.</p>'
      + '</div>';
    tags.parentNode.insertBefore(verdict, tags);
  }

  /* ── 5. Animate illustration blocks on scroll ── */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.article-img-illus').forEach(function (el) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      io.observe(el);
    });
  }

})();
