/* ── Article Hero Canvas — auto-themed by category ── */
(function () {
  var header = document.querySelector('.article-header');
  if (!header) return;

  /* ── Category → theme map ── */
  var THEMES = {
    'מוצרי AI':  { syms: ['🥽','🤖','📱','💡','🔮','🧠','⚡','🛸'], c1: '0,255,136',   c2: '124,58,237', bg1: '#010d06', bg2: '#060120', bg3: '#020808' },
    'כלים':      { syms: ['💻','⚙','🔧','🎨','🔍','{}','API','✦'], c1: '124,58,237',  c2: '6,182,212',  bg1: '#050213', bg2: '#0a0420', bg3: '#030112' },
    'חדשות':     { syms: ['📰','🕐','📡','⚡','📊','🔔','NEW','→'],  c1: '6,182,212',   c2: '99,102,241', bg1: '#020c18', bg2: '#050f22', bg3: '#010a14' },
    'ניתוח':     { syms: ['📊','🔬','📈','🧪','💡','→','∑','≈'],    c1: '99,102,241',  c2: '6,182,212',  bg1: '#040118', bg2: '#07021f', bg3: '#020010' },
    'השוואה':    { syms: ['⚖','↔','🔄','VS','←→','≡','≠','📊'],    c1: '6,182,212',   c2: '124,58,237', bg1: '#020d16', bg2: '#050f20', bg3: '#010b13' },
    'מדריך':     { syms: ['📖','💡','→','📝','✓','{}','//','✦'],    c1: '6,182,212',   c2: '124,58,237', bg1: '#030b1a', bg2: '#060d22', bg3: '#02080f' },
    'עסקים':     { syms: ['📈','💼','💡','⬆','₪','$','%','🏢'],    c1: '16,185,129',  c2: '124,58,237', bg1: '#040114', bg2: '#07021e', bg3: '#020011' },
    'AI מטורף':  { syms: ['⚡','🌪','💥','🔥','!!','😱','🤯','★'],  c1: '255,80,80',   c2: '255,180,0',  bg1: '#0d0200', bg2: '#150008', bg3: '#000510' },
  };
  var DEFAULT = { syms: ['🧠','⚡','✦','∞','🔮','AI','01','→'], c1: '124,58,237', c2: '6,182,212', bg1: '#04010e', bg2: '#0b0320', bg3: '#020714' };

  var catEl = header.querySelector('.category');
  var cat   = catEl ? catEl.textContent.trim() : '';
  var T     = THEMES[cat] || DEFAULT;

  /* ── Build wrapper ── */
  var wrap = document.createElement('div');
  wrap.className = 'article-hero-wrap';

  var cv = document.createElement('canvas');
  cv.id  = 'article-hero-canvas';

  /* Move header out of its container into wrap */
  var container = header.parentNode; /* .container */
  var section   = container.parentNode;
  section.insertBefore(wrap, container);
  wrap.appendChild(cv);
  wrap.appendChild(header); /* re-parent header into wrap */
  section.removeChild(container); /* remove old empty container */

  /* ── Canvas animation ── */
  var ctx = cv.getContext('2d');
  var W, H, nodes, tick = 0;

  function resize() {
    W = cv.width  = cv.offsetWidth;
    H = cv.height = cv.offsetHeight;
    initNodes();
  }

  function initNodes() {
    nodes = [];
    for (var i = 0; i < 26; i++) {
      nodes.push({
        x:    Math.random() * W,
        y:    Math.random() * H,
        vx:   (Math.random() - 0.5) * 0.5,
        vy:   (Math.random() - 0.5) * 0.5,
        r:    Math.random() * 2 + 1.3,
        sym:  Math.random() < 0.32 ? T.syms[Math.floor(Math.random() * T.syms.length)] : null,
        pulse: Math.random() * Math.PI * 2,
        ring:  Math.random() < 0.28,
        ringR: 0,
        col:   Math.random() < 0.55 ? T.c1 : T.c2
      });
    }
  }

  function draw() {
    tick++;

    /* background */
    var g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0,   T.bg1);
    g.addColorStop(0.5, T.bg2);
    g.addColorStop(1,   T.bg3);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    /* subtle grid */
    ctx.strokeStyle = 'rgba(124,58,237,0.05)';
    ctx.lineWidth = 1;
    var gs = 44;
    for (var x = 0; x < W; x += gs) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
    for (var y = 0; y < H; y += gs) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

    /* connections */
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i + 1; j < nodes.length; j++) {
        var dx = nodes[j].x - nodes[i].x, dy = nodes[j].y - nodes[i].y;
        var d  = Math.sqrt(dx * dx + dy * dy);
        if (d < 130) {
          var a  = (1 - d / 130) * 0.38;
          var gl = ctx.createLinearGradient(nodes[i].x, nodes[i].y, nodes[j].x, nodes[j].y);
          gl.addColorStop(0, 'rgba(' + nodes[i].col + ',' + a + ')');
          gl.addColorStop(1, 'rgba(' + nodes[j].col + ',' + a + ')');
          ctx.strokeStyle = gl; ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(nodes[i].x, nodes[i].y); ctx.lineTo(nodes[j].x, nodes[j].y); ctx.stroke();

          /* traveling dot every 90 frames */
          if (tick % 90 === (i * 3) % 90) {
            var t2 = (tick % 90) / 90;
            var tx = nodes[i].x + dx * t2, ty = nodes[i].y + dy * t2;
            ctx.fillStyle = 'rgba(' + T.c2 + ',0.85)';
            ctx.beginPath(); ctx.arc(tx, ty, 1.8, 0, Math.PI * 2); ctx.fill();
          }
        }
      }
    }

    /* nodes */
    nodes.forEach(function (n) {
      n.pulse += 0.042;
      var gw = Math.sin(n.pulse) * 0.38 + 0.65;

      if (n.ring) {
        n.ringR = (n.ringR + 0.75) % 32;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.ringR, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(' + T.c2 + ',' + (0.38 * (1 - n.ringR / 32)) + ')';
        ctx.lineWidth = 1; ctx.stroke();
      }

      var gn = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 4);
      gn.addColorStop(0, 'rgba(' + n.col + ',' + gw + ')');
      gn.addColorStop(1, 'rgba(' + n.col + ',0)');
      ctx.fillStyle = gn; ctx.beginPath(); ctx.arc(n.x, n.y, n.r * 4, 0, Math.PI * 2); ctx.fill();

      ctx.fillStyle = 'rgba(230,225,255,0.9)';
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();

      if (n.sym) {
        ctx.font = '13px sans-serif';
        ctx.globalAlpha = 0.52 * gw;
        ctx.fillStyle = '#fff';
        ctx.fillText(n.sym, n.x - 7, n.y - 13);
        ctx.globalAlpha = 1;
      }

      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    });

    /* scan line */
    var sc = (tick * 1.1) % H;
    var sg = ctx.createLinearGradient(0, sc - 7, 0, sc + 7);
    sg.addColorStop(0,   'rgba(' + T.c1 + ',0)');
    sg.addColorStop(0.5, 'rgba(' + T.c1 + ',0.13)');
    sg.addColorStop(1,   'rgba(' + T.c1 + ',0)');
    ctx.fillStyle = sg; ctx.fillRect(0, sc - 7, W, 14);

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
})();
