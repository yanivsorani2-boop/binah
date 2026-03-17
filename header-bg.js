(function () {
  'use strict';

  var canvas, ctx, W, H, raf;
  var nodes = [], BINARY = [], pulses = [];

  var COLORS = {
    primary : '#7c3aed',
    cyan    : '#06b6d4',
    white   : 'rgba(255,255,255,0.85)',
    dimLine : 'rgba(124,58,237,0.18)',
    dimCyan : 'rgba(6,182,212,0.14)',
  };

  /* ── setup ── */
  function init() {
    var header = document.querySelector('header');
    if (!header) return;

    canvas = document.createElement('canvas');
    canvas.id = 'header-canvas';
    header.insertBefore(canvas, header.firstChild);
    ctx = canvas.getContext('2d');

    resize();
    buildNodes();
    buildBinary();
    loop();

    window.addEventListener('resize', function () { resize(); buildNodes(); buildBinary(); });
  }

  function resize() {
    var header = document.querySelector('header');
    W = canvas.width  = header.offsetWidth;
    H = canvas.height = header.offsetHeight;
  }

  /* ── nodes (neural net style) ── */
  function buildNodes() {
    nodes = [];
    var count = Math.max(18, Math.floor(W / 60));
    for (var i = 0; i < count; i++) {
      nodes.push({
        x   : Math.random() * W,
        y   : Math.random() * H,
        vx  : (Math.random() - 0.5) * 0.35,
        vy  : (Math.random() - 0.5) * 0.35,
        r   : 1.5 + Math.random() * 2,
        pulse: Math.random() * Math.PI * 2,
        cyan: Math.random() > 0.65,
      });
    }
  }

  /* ── floating binary / hex digits ── */
  function buildBinary() {
    BINARY = [];
    var CHARS = '01ΨΩ∆∑⊕⊗◈⬡'.split('');
    var count = Math.floor(W / 90);
    for (var i = 0; i < count; i++) {
      BINARY.push({
        x    : Math.random() * W,
        y    : Math.random() * H,
        vy   : 0.18 + Math.random() * 0.25,
        char : CHARS[Math.floor(Math.random() * CHARS.length)],
        alpha: 0.06 + Math.random() * 0.12,
        size : 9 + Math.random() * 5,
        swap : 0,
        CHARS: CHARS,
      });
    }
    pulses = [];
  }

  /* ── grid lines ── */
  function drawGrid() {
    var step = 38;
    ctx.save();
    ctx.strokeStyle = 'rgba(124,58,237,0.07)';
    ctx.lineWidth   = 0.5;
    for (var x = 0; x < W; x += step) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (var y = 0; y < H; y += step) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
    ctx.restore();
  }

  /* ── robot silhouette (SVG-style via canvas, right side) ── */
  function drawRobot(ox, oy, scale, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(ox, oy);
    ctx.scale(scale, scale);
    ctx.strokeStyle = '#7c3aed';
    ctx.lineWidth   = 1.2;
    ctx.shadowColor = '#7c3aed';
    ctx.shadowBlur  = 8;

    // Head
    ctx.strokeRect(-14, -30, 28, 22);
    // Eyes
    ctx.beginPath();
    ctx.arc(-7, -20, 3.5, 0, Math.PI * 2);
    ctx.moveTo(7, -20); ctx.arc(7, -20, 3.5, 0, Math.PI * 2);
    ctx.stroke();
    // Antenna
    ctx.beginPath(); ctx.moveTo(0,-30); ctx.lineTo(0,-40);
    ctx.moveTo(-5,-40); ctx.lineTo(5,-40);
    ctx.stroke();
    // Body
    ctx.strokeRect(-18, -7, 36, 26);
    // Chest circuit
    ctx.strokeRect(-9,-1, 18, 12);
    ctx.beginPath(); ctx.moveTo(-9,5); ctx.lineTo(9,5); ctx.stroke();
    // Arms
    ctx.strokeRect(-26,-5,8,20);
    ctx.strokeRect(18,-5,8,20);
    // Legs
    ctx.strokeRect(-14,19,10,18);
    ctx.strokeRect(4,19,10,18);
    ctx.restore();
  }

  /* ── quantum ring ── */
  function drawQuantumRing(cx, cy, r, t, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(cx, cy);

    // Orbiting ellipses
    var rings = [
      {rx: r,   ry: r*0.35, angle: t*0.4},
      {rx: r,   ry: r*0.35, angle: t*0.4 + Math.PI/2},
      {rx: r*0.7, ry: r*0.28, angle: -t*0.6 + Math.PI/4},
    ];
    rings.forEach(function(ring) {
      ctx.save();
      ctx.rotate(ring.angle);
      ctx.beginPath();
      ctx.ellipse(0, 0, ring.rx, ring.ry, 0, 0, Math.PI*2);
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth   = 0.8;
      ctx.shadowColor = '#06b6d4';
      ctx.shadowBlur  = 6;
      ctx.stroke();
      ctx.restore();
    });

    // Core nucleus
    var grd = ctx.createRadialGradient(0,0,0, 0,0,r*0.22);
    grd.addColorStop(0, 'rgba(124,58,237,0.6)');
    grd.addColorStop(1, 'rgba(6,182,212,0)');
    ctx.beginPath(); ctx.arc(0,0,r*0.22,0,Math.PI*2);
    ctx.fillStyle = grd; ctx.fill();

    ctx.restore();
  }

  /* ── neural connections ── */
  function drawNodes(t) {
    var DIST = Math.min(W * 0.18, 140);

    // connections
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i+1; j < nodes.length; j++) {
        var dx = nodes[i].x - nodes[j].x;
        var dy = nodes[i].y - nodes[j].y;
        var d  = Math.sqrt(dx*dx + dy*dy);
        if (d < DIST) {
          var alpha = (1 - d/DIST) * 0.4;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = nodes[i].cyan
            ? 'rgba(6,182,212,' + alpha + ')'
            : 'rgba(124,58,237,' + alpha + ')';
          ctx.lineWidth = 0.7;
          ctx.stroke();
        }
      }
    }

    // node dots + glow
    nodes.forEach(function(n) {
      n.pulse += 0.04;
      var glow = 0.55 + 0.45 * Math.sin(n.pulse);
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r * (0.9 + 0.3*glow), 0, Math.PI*2);
      ctx.fillStyle   = n.cyan ? COLORS.cyan : COLORS.primary;
      ctx.shadowColor = n.cyan ? COLORS.cyan : COLORS.primary;
      ctx.shadowBlur  = 8 * glow;
      ctx.globalAlpha = 0.75 + 0.25 * glow;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.shadowBlur  = 0;

      // move
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0) n.x = W; if (n.x > W) n.x = 0;
      if (n.y < 0) n.y = H; if (n.y > H) n.y = 0;
    });
  }

  /* ── floating chars ── */
  function drawBinary() {
    ctx.save();
    ctx.font = '10px monospace';
    BINARY.forEach(function(b) {
      b.swap++;
      if (b.swap > 90) {
        b.swap = 0;
        b.char = b.CHARS[Math.floor(Math.random() * b.CHARS.length)];
      }
      ctx.fillStyle   = 'rgba(6,182,212,' + b.alpha + ')';
      ctx.font        = b.size + 'px monospace';
      ctx.fillText(b.char, b.x, b.y);
      b.y += b.vy;
      if (b.y > H + 20) b.y = -20;
    });
    ctx.restore();
  }

  /* ── scan line ── */
  function drawScanLine(t) {
    var y = (t * 0.4) % (H * 2);
    if (y > H) return;
    var grd = ctx.createLinearGradient(0, y-6, 0, y+6);
    grd.addColorStop(0,   'rgba(6,182,212,0)');
    grd.addColorStop(0.5, 'rgba(6,182,212,0.06)');
    grd.addColorStop(1,   'rgba(6,182,212,0)');
    ctx.fillStyle = grd;
    ctx.fillRect(0, y-6, W, 12);
  }

  /* ── main loop ── */
  var t = 0;
  function loop() {
    ctx.clearRect(0, 0, W, H);

    // Background gradient
    var bg = ctx.createLinearGradient(0,0,W,H);
    bg.addColorStop(0,   '#08080f');
    bg.addColorStop(0.5, '#0c0a18');
    bg.addColorStop(1,   '#07101a');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    drawGrid();
    drawScanLine(t);
    drawBinary();
    drawNodes(t);

    // Robot (right side, subtle)
    var rScale = Math.min(H/90, 0.75);
    drawRobot(W - 80 * rScale, H/2 + 8 * rScale, rScale, 0.12);
    drawRobot(W - 170 * rScale, H/2 - 5 * rScale, rScale * 0.7, 0.07);

    // Quantum rings (left area)
    var qr = Math.min(H * 0.55, 38);
    drawQuantumRing(qr * 1.6, H/2, qr, t * 0.012, 0.22);
    drawQuantumRing(qr * 3.6, H/2 - 4, qr * 0.6, -t * 0.018, 0.13);

    t++;
    raf = requestAnimationFrame(loop);
  }

  /* ── pause when tab hidden ── */
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) { cancelAnimationFrame(raf); }
    else { t = 0; loop(); }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
