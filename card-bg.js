(function () {
  'use strict';

  /* ── hex → rgba helper ── */
  function rgba(hex, a) {
    var r = parseInt(hex.slice(1,3),16),
        g = parseInt(hex.slice(3,5),16),
        b = parseInt(hex.slice(5,7),16);
    return 'rgba('+r+','+g+','+b+','+a+')';
  }

  /* ── Per-category themes (same visual language as header-bg.js) ── */
  var THEMES = {
    compare: {
      p: '#7c3aed', s: '#a78bfa',
      bg0: '#06020f', bg1: '#0d0520',
      chars: '≠≡↔∝⊕⊗∴Ψ01'.split(''),
      extra: 'twoRings'
    },
    tools: {
      p: '#06b6d4', s: '#38bdf8',
      bg0: '#020d12', bg1: '#041520',
      chars: '⚙◈⬡⊕⟳01∑Ω'.split(''),
      extra: 'circuit'
    },
    guide: {
      p: '#16a34a', s: '#4ade80',
      bg0: '#021207', bg1: '#061a0c',
      chars: '→⇒▶✓∑∆⊕Ω01'.split(''),
      extra: 'flow'
    },
    news: {
      p: '#dc2626', s: '#f87171',
      bg0: '#110202', bg1: '#1a0404',
      chars: '⚡★✦⊕ΨΩ01∆'.split(''),
      extra: 'radar'
    },
    analysis: {
      p: '#4338ca', s: '#818cf8',
      bg0: '#03020f', bg1: '#060417',
      chars: '∑∆ΨΩπ∫∂◈01'.split(''),
      extra: 'bars'
    },
    review: {
      p: '#d97706', s: '#fbbf24',
      bg0: '#0e0600', bg1: '#180b00',
      chars: '★⊗◈∴✦∵⟐⬡01'.split(''),
      extra: 'stars'
    },
    tips: {
      p: '#0f766e', s: '#2dd4bf',
      bg0: '#020f0d', bg1: '#041a16',
      chars: '✦⊕◉⟐∞⊗01Ψ'.split(''),
      extra: 'radiate'
    },
    orange: {
      p: '#ea580c', s: '#fb923c',
      bg0: '#100300', bg1: '#1c0600',
      chars: '⚙◉⊕→∑∆01Ω'.split(''),
      extra: 'circuit'
    },
    blue: {
      p: '#1a73e8', s: '#60a5fa',
      bg0: '#020814', bg1: '#040f20',
      chars: '★⊕◈⬡Ψ01∑∆'.split(''),
      extra: 'twoRings'
    },
    pink: {
      p: '#db2777', s: '#f472b6',
      bg0: '#0f0108', bg1: '#1a0210',
      chars: '★⊗◈✦∵01⟐Ψ'.split(''),
      extra: 'stars'
    },
  };

  var DEFAULT = THEMES.compare;

  var GUIDE_MAP = {
    'guide-chatgpt':    'tools',
    'guide-claude':     'compare',
    'guide-midjourney': 'pink',
    'guide-ollama':     'guide',
    'guide-prompt':     'analysis',
    'vibe-coding':      'analysis',
    'gemini':           'blue',
    'perplexity':       'tools',
    'canva':            'pink',
    'n8n':              'orange',
    'make':             'tools',
    'cursor':           'analysis',
    'comfyui':          'pink',
  };

  function themeFor(thumb) {
    var card = thumb.closest('[data-cat]');
    if (card) return THEMES[card.dataset.cat] || DEFAULT;
    var parent = thumb.closest('.guide-card, .prev-story-card');
    if (parent) {
      var link = parent.querySelector('a[href]');
      if (link) {
        for (var key in GUIDE_MAP) {
          if (link.href.indexOf(key) !== -1) return THEMES[GUIDE_MAP[key]] || DEFAULT;
        }
      }
    }
    return DEFAULT;
  }

  function buildNodes(W, H) {
    var count = Math.max(8, Math.floor(W / 26));
    var nodes = [];
    for (var i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.28,
        vy: (Math.random() - 0.5) * 0.28,
        r: 1.2 + Math.random() * 1.6,
        pulse: Math.random() * Math.PI * 2,
        sec: Math.random() > 0.62,
      });
    }
    return nodes;
  }

  function buildChars(W, H, theme) {
    var count = Math.max(3, Math.floor(W / 48));
    var arr = [];
    for (var i = 0; i < count; i++) {
      arr.push({
        x: Math.random() * W, y: Math.random() * H,
        vy: 0.13 + Math.random() * 0.17,
        char: theme.chars[Math.floor(Math.random() * theme.chars.length)],
        alpha: 0.05 + Math.random() * 0.09,
        size: 8 + Math.random() * 4,
        swap: Math.floor(Math.random() * 80),
      });
    }
    return arr;
  }

  var instances = [];
  var globalT  = 0;
  var raf      = null;

  function createInstance(thumb) {
    if (thumb.dataset.bgInit) return null;
    thumb.dataset.bgInit = '1';

    var canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;display:block;';
    thumb.insertBefore(canvas, thumb.firstChild);

    var W = canvas.width  = thumb.offsetWidth  || 300;
    var H = canvas.height = thumb.offsetHeight || 140;
    var ctx   = canvas.getContext('2d');
    var theme = themeFor(thumb);
    var phase = (Math.random() * 5000) | 0;

    return { canvas, ctx, W, H, theme, phase,
             nodes: buildNodes(W, H),
             chars: buildChars(W, H, theme),
             ex: { radarA: 0 },
             thumb };
  }

  /* ══════════════════════════════════════
     DRAW ONE FRAME
  ══════════════════════════════════════ */
  function draw(inst, t) {
    var ctx = inst.ctx, W = inst.W, H = inst.H, th = inst.theme;
    var lt  = t + inst.phase;

    /* background */
    var bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, th.bg0);
    bg.addColorStop(1, th.bg1);
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    /* grid */
    ctx.save();
    ctx.strokeStyle = rgba(th.p, 0.07);
    ctx.lineWidth   = 0.5;
    for (var x = 0; x < W; x += 22) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
    for (var y = 0; y < H; y += 22) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
    ctx.restore();

    /* scan line */
    var sy = (lt * 0.24) % (H * 2.3);
    if (sy <= H) {
      var sg = ctx.createLinearGradient(0, sy-5, 0, sy+5);
      sg.addColorStop(0,   rgba(th.s, 0));
      sg.addColorStop(0.5, rgba(th.s, 0.08));
      sg.addColorStop(1,   rgba(th.s, 0));
      ctx.fillStyle = sg;
      ctx.fillRect(0, sy-5, W, 10);
    }

    /* floating symbols */
    ctx.save();
    inst.chars.forEach(function(b) {
      b.swap++;
      if (b.swap > 80) { b.swap = 0; b.char = th.chars[Math.floor(Math.random() * th.chars.length)]; }
      ctx.font      = b.size + 'px monospace';
      ctx.fillStyle = rgba(th.s, b.alpha);
      ctx.fillText(b.char, b.x, b.y);
      b.y += b.vy;
      if (b.y > H + 12) b.y = -12;
    });
    ctx.restore();

    /* neural connections */
    var DIST  = Math.min(W * 0.42, 115);
    var nodes = inst.nodes;
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i+1; j < nodes.length; j++) {
        var dx = nodes[i].x - nodes[j].x;
        var dy = nodes[i].y - nodes[j].y;
        var d  = Math.sqrt(dx*dx + dy*dy);
        if (d < DIST) {
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = rgba(nodes[i].sec ? th.s : th.p, (1-d/DIST)*0.35);
          ctx.lineWidth   = 0.6;
          ctx.stroke();
        }
      }
    }

    /* node dots */
    nodes.forEach(function(n) {
      n.pulse += 0.04;
      var g   = 0.5 + 0.5 * Math.sin(n.pulse);
      var col = n.sec ? th.s : th.p;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r * (0.9 + 0.3*g), 0, Math.PI*2);
      ctx.fillStyle   = col;
      ctx.shadowColor = col;
      ctx.shadowBlur  = 7 * g;
      ctx.globalAlpha = 0.7 + 0.3*g;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.shadowBlur  = 0;
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0) n.x = W; if (n.x > W) n.x = 0;
      if (n.y < 0) n.y = H; if (n.y > H) n.y = 0;
    });

    drawExtra(ctx, W, H, th, lt, inst.ex);
  }

  /* ══════════════════════════════════════
     CATEGORY-SPECIFIC EXTRAS
  ══════════════════════════════════════ */
  function drawExtra(ctx, W, H, th, t, ex) {

    function qRings(cx, cy, r, tVal, alpha) {
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(cx, cy);
      [
        { rx: r,      ry: r*0.32, a:  tVal*0.009 },
        { rx: r,      ry: r*0.32, a:  tVal*0.009 + Math.PI/2 },
        { rx: r*0.68, ry: r*0.26, a: -tVal*0.013 + Math.PI/4 },
      ].forEach(function(d) {
        ctx.save();
        ctx.rotate(d.a);
        ctx.beginPath();
        ctx.ellipse(0, 0, d.rx, d.ry, 0, 0, Math.PI*2);
        ctx.strokeStyle = rgba(th.s, 0.65);
        ctx.lineWidth   = 0.85;
        ctx.shadowColor = th.s;
        ctx.shadowBlur  = 5;
        ctx.stroke();
        ctx.restore();
      });
      var grd = ctx.createRadialGradient(0,0,0, 0,0,r*0.26);
      grd.addColorStop(0, rgba(th.p, 0.55));
      grd.addColorStop(1, rgba(th.p, 0));
      ctx.beginPath();
      ctx.arc(0, 0, r*0.26, 0, Math.PI*2);
      ctx.fillStyle = grd;
      ctx.fill();
      ctx.restore();
    }

    switch (th.extra) {

      /* compare — two quantum rings + beam */
      case 'twoRings': {
        var r = Math.min(H*0.38, 28);
        qRings(W*0.22, H*0.5, r,  t, 0.28);
        qRings(W*0.78, H*0.5, r, -t, 0.22);
        var ba   = 0.10 + 0.07 * Math.sin(t * 0.022);
        var beam = ctx.createLinearGradient(W*0.22, H*0.5, W*0.78, H*0.5);
        beam.addColorStop(0,   rgba(th.p, 0));
        beam.addColorStop(0.5, rgba(th.s, ba));
        beam.addColorStop(1,   rgba(th.p, 0));
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(W*0.22, H*0.5);
        ctx.lineTo(W*0.78, H*0.5);
        ctx.strokeStyle = beam;
        ctx.lineWidth   = 1.5;
        ctx.stroke();
        ctx.restore();
        break;
      }

      /* tools — circuit traces + ring */
      case 'circuit': {
        qRings(W*0.78, H*0.48, Math.min(H*0.32, 22), t, 0.2);
        ctx.save();
        ctx.globalAlpha = 0.22;
        ctx.strokeStyle = rgba(th.p, 0.7);
        ctx.lineWidth   = 1;
        var ox = W*0.1, oy = H*0.32;
        ctx.beginPath();
        ctx.moveTo(ox,    oy);
        ctx.lineTo(ox+18, oy);
        ctx.lineTo(ox+18, oy+22);
        ctx.lineTo(ox+38, oy+22);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(ox, oy+38);
        ctx.lineTo(ox+28, oy+38);
        ctx.stroke();
        [[ox,oy],[ox+18,oy+22],[ox+38,oy+22],[ox+28,oy+38]].forEach(function(pt) {
          ctx.beginPath();
          ctx.arc(pt[0], pt[1], 3, 0, Math.PI*2);
          ctx.fillStyle = rgba(th.s, 0.9);
          ctx.fill();
        });
        ctx.restore();
        break;
      }

      /* guide — animated dashed flow path + arrow */
      case 'flow': {
        ctx.save();
        ctx.setLineDash([5, 9]);
        ctx.lineDashOffset = -(t * 0.45 % 28);
        ctx.strokeStyle    = rgba(th.s, 0.35);
        ctx.lineWidth      = 1.6;
        ctx.beginPath();
        ctx.moveTo(W*0.08, H*0.55);
        ctx.bezierCurveTo(W*0.28, H*0.15, W*0.58, H*0.85, W*0.88, H*0.5);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.moveTo(W*0.84, H*0.42);
        ctx.lineTo(W*0.91, H*0.5);
        ctx.lineTo(W*0.84, H*0.58);
        ctx.strokeStyle = rgba(th.s, 0.55);
        ctx.lineWidth   = 1.6;
        ctx.stroke();
        ctx.restore();
        qRings(W*0.15, H*0.52, Math.min(H*0.28, 18), t, 0.18);
        break;
      }

      /* news — radar sweep + small ring */
      case 'radar': {
        ctx.save();
        var cx = W*0.78, cy = H*0.5, rad = Math.min(H*0.42, 34);
        ex.radarA = (ex.radarA + 0.028) % (Math.PI*2);
        ctx.globalAlpha = 0.2;
        ctx.strokeStyle = rgba(th.p, 0.55);
        ctx.lineWidth   = 0.7;
        [1, 0.65, 0.33].forEach(function(f) {
          ctx.beginPath(); ctx.arc(cx, cy, rad*f, 0, Math.PI*2); ctx.stroke();
        });
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(ex.radarA);
        var sw = ctx.createLinearGradient(0, 0, rad, 0);
        sw.addColorStop(0, rgba(th.p, 0.55));
        sw.addColorStop(1, rgba(th.p, 0));
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, rad, -0.45, 0.05);
        ctx.closePath();
        ctx.fillStyle = sw;
        ctx.fill();
        ctx.restore();
        ctx.restore();
        qRings(W*0.22, H*0.5, Math.min(H*0.28, 18), t, 0.18);
        break;
      }

      /* analysis — animated bar chart + ring */
      case 'bars': {
        ctx.save();
        ctx.globalAlpha = 0.28;
        [0.30, 0.52, 0.44, 0.72, 0.58, 0.84].forEach(function(h, i) {
          var bh = H * h * (0.8 + 0.2 * Math.sin(t*0.019 + i*0.6));
          var bx = W*0.54 + i*20;
          var g  = ctx.createLinearGradient(0, H, 0, H-bh);
          g.addColorStop(0, rgba(th.p, 0.85));
          g.addColorStop(1, rgba(th.s, 0.45));
          ctx.fillStyle = g;
          ctx.fillRect(bx, H-bh, 9, bh);
        });
        ctx.restore();
        qRings(W*0.2, H*0.52, Math.min(H*0.32, 22), t, 0.22);
        break;
      }

      /* review — star constellation + ring */
      case 'stars': {
        ctx.save();
        var pts = [[0.1,0.2],[0.3,0.12],[0.52,0.26],[0.42,0.62],[0.72,0.46],[0.2,0.72],[0.62,0.78],[0.82,0.28]];
        [[0,1],[1,2],[2,4],[0,3],[3,5],[4,7]].forEach(function(pair) {
          var a = pts[pair[0]], b = pts[pair[1]];
          ctx.beginPath();
          ctx.moveTo(a[0]*W, a[1]*H);
          ctx.lineTo(b[0]*W, b[1]*H);
          ctx.strokeStyle = rgba(th.s, 0.12);
          ctx.lineWidth   = 0.6;
          ctx.stroke();
        });
        pts.forEach(function(p, i) {
          var bright = 0.55 + 0.45 * Math.sin(t*0.016 + i*1.3);
          ctx.beginPath();
          ctx.arc(p[0]*W, p[1]*H, 1.6 + bright*1.2, 0, Math.PI*2);
          ctx.fillStyle   = rgba(th.s, bright);
          ctx.shadowColor = th.s;
          ctx.shadowBlur  = 7 * bright;
          ctx.fill();
          ctx.shadowBlur  = 0;
        });
        ctx.restore();
        qRings(W*0.5, H*0.5, Math.min(H*0.3, 20), t, 0.13);
        break;
      }

      /* tips — central radiance + ring */
      case 'radiate': {
        ctx.save();
        var pr  = 16 + 9 * Math.sin(t * 0.018);
        var grd = ctx.createRadialGradient(W*0.5,H*0.5,0, W*0.5,H*0.5, pr*2.2);
        grd.addColorStop(0,    rgba(th.p, 0.42));
        grd.addColorStop(0.45, rgba(th.s, 0.16));
        grd.addColorStop(1,    rgba(th.p, 0));
        ctx.beginPath();
        ctx.arc(W*0.5, H*0.5, pr*2.2, 0, Math.PI*2);
        ctx.fillStyle = grd;
        ctx.fill();
        ctx.globalAlpha = 0.16;
        for (var k = 0; k < 8; k++) {
          var ang = k * Math.PI/4 + t * 0.006;
          ctx.beginPath();
          ctx.moveTo(W*0.5 + Math.cos(ang)*9,      H*0.5 + Math.sin(ang)*9);
          ctx.lineTo(W*0.5 + Math.cos(ang)*pr*1.9,  H*0.5 + Math.sin(ang)*pr*1.9);
          ctx.strokeStyle = rgba(th.s, 0.5);
          ctx.lineWidth   = 0.9;
          ctx.stroke();
        }
        ctx.restore();
        qRings(W*0.5, H*0.5, Math.min(H*0.42, 30), t, 0.14);
        break;
      }
    }
  }

  /* ── Animation loop ── */
  function loop() {
    globalT++;
    instances.forEach(function(inst) {
      var rect = inst.thumb.getBoundingClientRect();
      if (rect.bottom > -150 && rect.top < window.innerHeight + 150) {
        draw(inst, globalT);
      }
    });
    raf = requestAnimationFrame(loop);
  }

  function initThumbs() {
    document.querySelectorAll('.card-thumb, .guide-thumb').forEach(function(thumb) {
      var inst = createInstance(thumb);
      if (inst) instances.push(inst);
    });
    if (instances.length && !raf) loop();
  }

  if (window.MutationObserver) {
    new MutationObserver(function(muts) {
      muts.forEach(function(m) {
        m.addedNodes.forEach(function(node) {
          if (node.nodeType !== 1) return;
          (node.querySelectorAll ? node.querySelectorAll('.card-thumb, .guide-thumb') : [])
            .forEach(function(thumb) {
              var inst = createInstance(thumb);
              if (inst) { instances.push(inst); if (!raf) loop(); }
            });
        });
      });
    }).observe(document.body, { childList: true, subtree: true });
  }

  document.addEventListener('visibilitychange', function() {
    if (document.hidden) { cancelAnimationFrame(raf); raf = null; }
    else if (instances.length) loop();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThumbs);
  } else {
    initThumbs();
  }
})();
