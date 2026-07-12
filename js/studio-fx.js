/* בינה סטודיו — אפקטים מתקדמים (GSAP + ScrollTrigger) */
(function () {
  if (!window.gsap) return;
  var motionOK = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!motionOK) return;
  if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  /* --- פיצול כותרת ההירו למילים --- */
  var h1 = document.querySelector('.hero h1');
  if (h1) {
    var walker = document.createTreeWalker(h1, NodeFilter.SHOW_TEXT);
    var textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    textNodes.forEach(function (node) {
      if (!node.nodeValue.trim()) return;
      /* לא מפצלים בתוך טקסט גרדיאנט — background-clip נשבר על ילדים עם transform */
      if (node.parentElement.closest('.grad-text')) return;
      var frag = document.createDocumentFragment();
      node.nodeValue.split(/(\s+)/).forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
        var w = document.createElement('span');
        w.className = 'fx-w';
        w.style.display = 'inline-block';
        w.textContent = part;
        frag.appendChild(w);
      });
      node.parentNode.replaceChild(frag, node);
    });
  }

  /* --- טיימליין כניסה להירו --- */
  var tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.from('.eyebrow', { y: 24, autoAlpha: 0, duration: 0.6 })
    .from('.hero h1 .fx-w', { y: 60, autoAlpha: 0, rotationX: -45, transformPerspective: 800, duration: 0.9, stagger: 0.05 }, '-=0.3')
    .from('.hero h1 .grad-text', { y: 60, autoAlpha: 0, duration: 0.9 }, '-=0.55')
    .from('.hero .sub', { y: 30, autoAlpha: 0, duration: 0.7 }, '-=0.5')
    .from('.hero-ctas .btn', { y: 24, autoAlpha: 0, duration: 0.6, stagger: 0.12 }, '-=0.4')
    .from('.hero-stats .stat', { y: 24, autoAlpha: 0, duration: 0.6, stagger: 0.1 }, '-=0.35');

  /* רשת ביטחון: אם משהו עצר את הטיימליין (טאב ברקע וכו') — להשלים ולהציג הכל */
  setTimeout(function () { if (tl.progress() < 1) tl.progress(1); }, 6000);

  if (!window.ScrollTrigger) return;

  /* --- פרלקסה עדינה בגלילה --- */
  gsap.utils.toArray('.aurora i').forEach(function (blob, i) {
    gsap.to(blob, {
      yPercent: (i + 1) * 14,
      ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
    });
  });

  gsap.utils.toArray('.project-media').forEach(function (media) {
    gsap.fromTo(media,
      { y: 60 },
      {
        y: -60,
        ease: 'none',
        scrollTrigger: { trigger: media, start: 'top bottom', end: 'bottom top', scrub: 1 }
      });
  });

  /* --- ריחוף מתמשך עדין למוקאפים --- */
  gsap.utils.toArray('.project-media .phone').forEach(function (el, i) {
    gsap.to(el, {
      y: '+=12',
      duration: 2.6 + i * 0.4,
      yoyo: true,
      repeat: -1,
      ease: 'sine.inOut',
      delay: i * 0.3
    });
  });

})();
