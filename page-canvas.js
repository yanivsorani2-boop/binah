/* ═══════════════════════════════════════════════════════════════
   PageCanvas — canvas-based hero banner, per-theme colors+elements
   binah.co.il
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── Per-theme config ──────────────────────────────────────────
     c1   : node glow + dot color  (rgb string)
     c2   : mid connection color   (rgb string)
     c3   : end connection color   (rgb string)
     trace: trace line color       (rgb string)
     scan : scan line color        (rgb string)
     hud  : HUD arc color          (rgba string)
     bg   : [stop0, stop0.5, stop1] background gradient
     icons: floating emoji symbols
     extra: function name for theme-specific drawn shapes
  ────────────────────────────────────────────────────────────── */
  var THEMES = {
    products: {
      c1:'0,255,136', c2:'6,182,212', c3:'0,255,136',
      trace:'0,255,136', scan:'0,255,136',
      hud:'rgba(6,182,212,0.10)',
      bg:['#050210','#0a0325','#02070f'],
      icons:['🥽','🤖','📱','💡','🔮','🧠','⚡','🛸','💻','🔬'],
      extra:'drawProducts'
    },
    tools: {
      c1:'139,92,246', c2:'99,102,241', c3:'6,182,212',
      trace:'139,92,246', scan:'139,92,246',
      hud:'rgba(139,92,246,0.12)',
      bg:['#07020f','#100418','#030108'],
      icons:['⚙','💻','🔧','{}','API','//','⌨','🔍','✦','⚡'],
      extra:'drawTools'
    },
    guides: {
      c1:'6,182,212', c2:'56,189,248', c3:'99,102,241',
      trace:'6,182,212', scan:'6,182,212',
      hud:'rgba(6,182,212,0.10)',
      bg:['#020c14','#041826','#010a10'],
      icons:['📖','💡','→','📝','✓','🎓','📚','✦','{}','//'],
      extra:'drawGuides'
    },
    news: {
      c1:'59,130,246', c2:'6,182,212', c3:'139,92,246',
      trace:'59,130,246', scan:'59,130,246',
      hud:'rgba(59,130,246,0.12)',
      bg:['#020814','#040e22','#010610'],
      icons:['📰','🕐','📡','⚡','📊','🔔','NEW','→','📢','🌐'],
      extra:'drawNews'
    },
    quiz: {
      c1:'168,85,247', c2:'139,92,246', c3:'236,72,153',
      trace:'168,85,247', scan:'168,85,247',
      hud:'rgba(168,85,247,0.12)',
      bg:['#08020f','#110320','#050010'],
      icons:['?','⚖','↔','→','✓','✗','AI','💡','⭐','🎯'],
      extra:'drawQuiz'
    },
    business: {
      c1:'16,185,129', c2:'5,150,105', c3:'6,182,212',
      trace:'16,185,129', scan:'16,185,129',
      hud:'rgba(16,185,129,0.10)',
      bg:['#020c08','#031810','#010805'],
      icons:['📈','💼','💡','⬆','₪','$','%','🏢','📊','🤝'],
      extra:'drawBusiness'
    },
    crazy: {
      c1:'249,115,22', c2:'239,68,68', c3:'250,204,21',
      trace:'249,115,22', scan:'239,68,68',
      hud:'rgba(249,115,22,0.12)',
      bg:['#0d0200','#180500','#070000'],
      icons:['⚡','🌪','💥','🔥','!!','😱','🤯','★','🚀','👁'],
      extra:'drawCrazy'
    },
    articles: {
      c1:'232,121,249', c2:'139,92,246', c3:'6,182,212',
      trace:'139,92,246', scan:'232,121,249',
      hud:'rgba(232,121,249,0.10)',
      bg:['#070010','#0d0120','#040008'],
      icons:['✍','📝','💬','→','"','✦','📖','✒','📃','//'],
      extra:'drawArticles'
    },
  };
  var DEFAULT = THEMES.products;

  /* ── Theme-specific extra shapes (drawn on canvas) ── */
  function drawProducts(ctx, W, H, frame) {
    /* rotating HUD dashes — already in base, nothing extra */
  }

  function drawTools(ctx, W, H, frame) {
    /* Spinning gear outlines in corners */
    var gears = [{x:W*0.06,y:H*0.25,r:28,speed:0.008},{x:W*0.94,y:H*0.75,r:20,speed:-0.012},{x:W*0.9,y:H*0.22,r:16,speed:0.015}];
    gears.forEach(function(g) {
      var a = frame * g.speed;
      ctx.save(); ctx.translate(g.x, g.y); ctx.rotate(a);
      ctx.strokeStyle = 'rgba(139,92,246,0.18)'; ctx.lineWidth = 1.2;
      var teeth = 8, step = Math.PI / teeth;
      ctx.beginPath();
      for (var i = 0; i < teeth*2; i++) {
        var ang = i * step - Math.PI/2;
        var r = i%2===0 ? g.r : g.r*0.72;
        var m = i===0 ? 'moveTo' : 'lineTo';
        ctx[m](r*Math.cos(ang), r*Math.sin(ang));
      }
      ctx.closePath(); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 0, g.r*0.28, 0, Math.PI*2); ctx.stroke();
      ctx.restore();
    });
  }

  function drawGuides(ctx, W, H, frame) {
    /* Book outlines floating on sides */
    var books = [{x:W*0.05,y:H*0.5,w:32,h:42},{x:W*0.95,y:H*0.4,w:26,h:36}];
    books.forEach(function(b, i) {
      var bob = Math.sin(frame*0.02 + i*1.5) * 5;
      ctx.strokeStyle = 'rgba(6,182,212,0.18)'; ctx.lineWidth = 1;
      ctx.strokeRect(b.x - b.w/2, b.y - b.h/2 + bob, b.w, b.h);
      /* spine */
      ctx.beginPath(); ctx.moveTo(b.x - b.w/2 + 5, b.y - b.h/2 + bob);
      ctx.lineTo(b.x - b.w/2 + 5, b.y + b.h/2 + bob); ctx.stroke();
      /* text lines */
      ctx.strokeStyle = 'rgba(6,182,212,0.1)';
      for (var l = 0; l < 4; l++) {
        var ly = b.y - b.h/2 + 8 + l*8 + bob;
        ctx.beginPath(); ctx.moveTo(b.x - b.w/2 + 8, ly); ctx.lineTo(b.x + b.w/2 - 3, ly); ctx.stroke();
      }
    });
  }

  function drawNews(ctx, W, H, frame) {
    /* Signal wave rings from two broadcast points */
    var pts = [{x:W*0.08,y:H*0.5},{x:W*0.92,y:H*0.5}];
    pts.forEach(function(p, pi) {
      for (var k = 0; k < 3; k++) {
        var phase = ((frame*0.018 + k*0.6 + pi*0.9) % 1);
        var maxR = 55;
        var rr = phase * maxR;
        var alpha = (1 - phase) * 0.22;
        ctx.beginPath(); ctx.arc(p.x, p.y, rr, 0, Math.PI*2);
        ctx.strokeStyle = 'rgba(59,130,246,'+alpha+')'; ctx.lineWidth = 1; ctx.stroke();
      }
    });
    /* Horizontal ticker line */
    var tx = (frame * 1.2) % (W + 120) - 60;
    ctx.strokeStyle = 'rgba(59,130,246,0.15)'; ctx.lineWidth = 1;
    ctx.setLineDash([6,4]);
    ctx.beginPath(); ctx.moveTo(0, H*0.88); ctx.lineTo(W, H*0.88); ctx.stroke();
    ctx.setLineDash([]);
  }

  function drawQuiz(ctx, W, H, frame) {
    /* Decision tree: 3 nodes connected */
    var nodes2 = [{x:W*0.5,y:H*0.15},{x:W*0.25,y:H*0.72},{x:W*0.75,y:H*0.72}];
    ctx.strokeStyle = 'rgba(168,85,247,0.2)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(nodes2[0].x, nodes2[0].y); ctx.lineTo(nodes2[1].x, nodes2[1].y); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(nodes2[0].x, nodes2[0].y); ctx.lineTo(nodes2[2].x, nodes2[2].y); ctx.stroke();
    nodes2.forEach(function(n, i) {
      var pulse = Math.sin(frame*0.04 + i*1.2)*0.3+0.7;
      ctx.beginPath(); ctx.arc(n.x, n.y, 10, 0, Math.PI*2);
      ctx.strokeStyle = 'rgba(168,85,247,'+(0.3*pulse)+')'; ctx.lineWidth = 1.5; ctx.stroke();
    });
    /* Large ? marks */
    ctx.font = 'bold 36px sans-serif';
    ctx.fillStyle = 'rgba(168,85,247,0.07)';
    ctx.fillText('?', W*0.05, H*0.55);
    ctx.fillText('?', W*0.88, H*0.35);
  }

  function drawBusiness(ctx, W, H, frame) {
    /* Bar chart in bottom-right */
    var bars = [0.35,0.55,0.42,0.70,0.85,0.60];
    var bx = W*0.68, by = H*0.9, bw = 12, gap = 5;
    bars.forEach(function(h2, i) {
      var bh = h2 * H * 0.6;
      var grow = Math.min(1, (frame - i*8) / 60);
      if (grow < 0) return;
      ctx.fillStyle = 'rgba(16,185,129,' + (0.15*grow) + ')';
      ctx.fillRect(bx + i*(bw+gap), by - bh*grow, bw, bh*grow);
      ctx.strokeStyle = 'rgba(16,185,129,' + (0.35*grow) + ')';
      ctx.lineWidth = 1;
      ctx.strokeRect(bx + i*(bw+gap), by - bh*grow, bw, 1);
    });
    /* Trend arrow */
    ctx.strokeStyle = 'rgba(16,185,129,0.2)'; ctx.lineWidth = 1.5;
    ctx.setLineDash([4,3]);
    ctx.beginPath(); ctx.moveTo(W*0.65, H*0.82); ctx.lineTo(W*0.95, H*0.18); ctx.stroke();
    ctx.setLineDash([]);
  }

  function drawCrazy(ctx, W, H, frame) {
    /* Fast flashing lightning bolts */
    var bolts = [
      {pts:[[W*.15,H*.05],[W*.11,H*.3],[W*.14,H*.3],[W*.09,H*.55]],del:0},
      {pts:[[W*.82,H*.08],[W*.78,H*.28],[W*.81,H*.28],[W*.76,H*.48]],del:7},
      {pts:[[W*.5, H*.02],[W*.46,H*.18],[W*.49,H*.18],[W*.44,H*.34]],del:14},
      {pts:[[W*.92,H*.55],[W*.88,H*.72],[W*.91,H*.72],[W*.86,H*.88]],del:5},
    ];
    bolts.forEach(function(b) {
      var flicker = Math.sin(frame*0.18 + b.del)*0.5+0.5;
      if (flicker < 0.3) return;
      ctx.strokeStyle = 'rgba(249,115,22,'+(flicker*0.45)+')';
      ctx.lineWidth = 1.5; ctx.lineJoin = 'round';
      ctx.beginPath(); ctx.moveTo(b.pts[0][0], b.pts[0][1]);
      for (var p=1;p<b.pts.length;p++) ctx.lineTo(b.pts[p][0], b.pts[p][1]);
      ctx.stroke();
    });
    /* Speed lines from center */
    for (var s = 0; s < 6; s++) {
      var angle = (s/6)*Math.PI*2 + frame*0.015;
      var len = 30 + Math.sin(frame*0.08+s)*15;
      ctx.strokeStyle = 'rgba(239,68,68,0.08)'; ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(W/2 + Math.cos(angle)*40, H/2 + Math.sin(angle)*20);
      ctx.lineTo(W/2 + Math.cos(angle)*(40+len), H/2 + Math.sin(angle)*(20+len*0.5));
      ctx.stroke();
    }
  }

  function drawArticles(ctx, W, H, frame) {
    /* Flowing pen stroke across banner */
    var prog = Math.min(1, frame / 180);
    if (prog > 0) {
      ctx.strokeStyle = 'rgba(139,92,246,0.22)'; ctx.lineWidth = 1.5;
      ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.beginPath();
      var pts = [[W*.03,H*.82],[W*.18,H*.35],[W*.35,H*.6],[W*.52,H*.22],[W*.68,H*.5],[W*.82,H*.18],[W*.97,H*.42]];
      var maxI = Math.floor(prog * (pts.length-1));
      ctx.moveTo(pts[0][0], pts[0][1]);
      for (var pi=1; pi<=maxI; pi++) ctx.lineTo(pts[pi][0], pts[pi][1]);
      if (maxI < pts.length-1) {
        var frac = (prog*(pts.length-1)) - maxI;
        ctx.lineTo(pts[maxI][0]+(pts[maxI+1][0]-pts[maxI][0])*frac,
                   pts[maxI][1]+(pts[maxI+1][1]-pts[maxI][1])*frac);
      }
      ctx.stroke();
    }
    /* Quote marks */
    ctx.font = '60px serif'; ctx.fillStyle = 'rgba(232,121,249,0.06)';
    ctx.fillText('"', W*0.02, H*0.5);
    ctx.fillText('"', W*0.9, H*0.85);
  }

  var EXTRA_FNS = {
    drawProducts: drawProducts,
    drawTools:    drawTools,
    drawGuides:   drawGuides,
    drawNews:     drawNews,
    drawQuiz:     drawQuiz,
    drawBusiness: drawBusiness,
    drawCrazy:    drawCrazy,
    drawArticles: drawArticles,
  };

  /* ── Render one banner ── */
  function renderBanner(el) {
    var theme    = el.dataset.theme    || 'products';
    var title    = el.dataset.title    || '';
    var subtitle = el.dataset.subtitle || '';
    var badge    = el.dataset.badge    || '';
    var badgeCol = el.dataset.badgeColor || 'green';
    var btn1txt  = el.dataset.btn1     || '';
    var btn1href = el.dataset.btn1Href || '#';
    var btn2txt  = el.dataset.btn2     || '';
    var btn2href = el.dataset.btn2Href || '#';

    var T = THEMES[theme] || DEFAULT;

    var badgeHTML = badge
      ? '<div class="pc-badge ' + badgeCol + '"><span class="pc-dot"></span>' + badge + '</div>'
      : '';

    var btnsHTML = (btn1txt || btn2txt)
      ? '<div class="pc-btns">'
          + (btn1txt ? '<a href="' + btn1href + '" class="btn-primary">' + btn1txt + '</a>' : '')
          + (btn2txt ? '<a href="' + btn2href + '" class="btn-outline">' + btn2txt + '</a>' : '')
        + '</div>'
      : '';

    el.innerHTML =
      '<canvas class="pc-canvas"></canvas>'
      + '<div class="pc-content">'
      +   badgeHTML
      +   '<h1 class="pc-title">' + title + '</h1>'
      +   (subtitle ? '<p class="pc-sub">' + subtitle + '</p>' : '')
      +   btnsHTML
      + '</div>';

    var cv  = el.querySelector('.pc-canvas');
    var ctx = cv.getContext('2d');
    var W, H, nodes, traces, scanY = 0, frame = 0;
    var extraFn = EXTRA_FNS[T.extra] || drawProducts;

    function resize() {
      W = cv.width  = cv.offsetWidth;
      H = cv.height = cv.offsetHeight;
      init();
    }

    function init() {
      scanY = 0; frame = 0;
      nodes = [];
      for (var i = 0; i < 28; i++) {
        nodes.push({
          x: Math.random()*W, y: Math.random()*H,
          vx: (Math.random()-0.5)*0.4, vy: (Math.random()-0.5)*0.4,
          r:  Math.random()*2+1.4,
          icon: Math.random()<0.28 ? T.icons[Math.floor(Math.random()*T.icons.length)] : null,
          glow: Math.random()*Math.PI*2,
          ring: Math.random()<0.25,
          ringR: Math.random()*20, ringMax: 26+Math.random()*14
        });
      }
      traces = [];
      for (var j = 0; j < 14; j++) {
        var x1=Math.random()*W, y1=Math.random()*H;
        var x2=x1+(Math.random()-0.5)*200, y2=y1+(Math.random()-0.5)*200;
        traces.push({x1:x1,y1:y1,ex:x2,ey:y1,x2:x2,y2:y2,
          alpha:Math.random()*0.3+0.07, dot:Math.random()});
      }
    }

    function draw() {
      frame++;

      /* Background */
      var bg = ctx.createLinearGradient(0,0,W,H);
      bg.addColorStop(0,   T.bg[0]);
      bg.addColorStop(0.5, T.bg[1]);
      bg.addColorStop(1,   T.bg[2]);
      ctx.fillStyle = bg; ctx.fillRect(0,0,W,H);

      /* Grid */
      ctx.strokeStyle = 'rgba('+T.c1+',0.04)'; ctx.lineWidth = 1;
      for (var gx=0;gx<W;gx+=38){ctx.beginPath();ctx.moveTo(gx,0);ctx.lineTo(gx,H);ctx.stroke();}
      for (var gy=0;gy<H;gy+=38){ctx.beginPath();ctx.moveTo(0,gy);ctx.lineTo(W,gy);ctx.stroke();}

      /* Theme extras (drawn behind nodes) */
      extraFn(ctx, W, H, frame);

      /* PCB traces */
      traces.forEach(function(t){
        t.dot=(t.dot+0.0045)%1;
        ctx.strokeStyle='rgba('+T.trace+','+t.alpha+')'; ctx.lineWidth=1;
        ctx.beginPath(); ctx.moveTo(t.x1,t.y1); ctx.lineTo(t.ex,t.ey); ctx.lineTo(t.x2,t.y2); ctx.stroke();
        var td=t.dot, px, py;
        if(td<0.5){px=t.x1+(t.ex-t.x1)*(td*2);py=t.y1;}
        else{px=t.ex+(t.x2-t.ex)*((td-0.5)*2);py=t.ey+(t.y2-t.ey)*((td-0.5)*2);}
        ctx.fillStyle='rgba('+T.c1+',0.9)';
        ctx.beginPath();ctx.arc(px,py,2,0,Math.PI*2);ctx.fill();
      });

      /* Connections */
      for(var i=0;i<nodes.length;i++){
        for(var j=i+1;j<nodes.length;j++){
          var dx=nodes[j].x-nodes[i].x, dy=nodes[j].y-nodes[i].y;
          var d=Math.sqrt(dx*dx+dy*dy);
          if(d<125){
            var a=(1-d/125)*0.32;
            var lg=ctx.createLinearGradient(nodes[i].x,nodes[i].y,nodes[j].x,nodes[j].y);
            lg.addColorStop(0,'rgba('+T.c1+','+a+')');
            lg.addColorStop(0.5,'rgba('+T.c2+','+(a*0.8)+')');
            lg.addColorStop(1,'rgba('+T.c3+','+a+')');
            ctx.strokeStyle=lg; ctx.lineWidth=1;
            ctx.beginPath();ctx.moveTo(nodes[i].x,nodes[i].y);ctx.lineTo(nodes[j].x,nodes[j].y);ctx.stroke();
          }
        }
      }

      /* Nodes */
      nodes.forEach(function(n){
        n.glow+=0.03; var g=Math.sin(n.glow)*0.45+0.55;
        if(n.ring){
          n.ringR=(n.ringR+0.6)%n.ringMax;
          ctx.beginPath();ctx.arc(n.x,n.y,n.ringR,0,Math.PI*2);
          ctx.strokeStyle='rgba('+T.c1+','+(0.5*(1-n.ringR/n.ringMax))+')';
          ctx.lineWidth=1;ctx.stroke();
        }
        var rg=ctx.createRadialGradient(n.x,n.y,0,n.x,n.y,n.r*4);
        rg.addColorStop(0,'rgba('+T.c1+','+g+')');
        rg.addColorStop(1,'rgba('+T.c1+',0)');
        ctx.fillStyle=rg;ctx.beginPath();ctx.arc(n.x,n.y,n.r*4,0,Math.PI*2);ctx.fill();
        ctx.fillStyle='rgba('+T.c1+',1)';
        ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,Math.PI*2);ctx.fill();
        if(n.icon){
          ctx.font='14px sans-serif'; ctx.globalAlpha=0.5*g;
          ctx.fillText(n.icon,n.x-7,n.y-11); ctx.globalAlpha=1;
        }
        n.x+=n.vx;n.y+=n.vy;
        if(n.x<0||n.x>W)n.vx*=-1;
        if(n.y<0||n.y>H)n.vy*=-1;
      });

      /* HUD rings */
      var cx2=W*0.5,cy2=H*0.5,ha=frame*0.008;
      for(var ri=60;ri<=160;ri+=50){
        ctx.beginPath();ctx.arc(cx2,cy2,ri,ha,ha+Math.PI*0.3);
        ctx.strokeStyle=T.hud;ctx.lineWidth=1;ctx.stroke();
        ctx.beginPath();ctx.arc(cx2,cy2,ri,ha+Math.PI,ha+Math.PI*1.3);ctx.stroke();
      }

      /* Scan line */
      scanY=(scanY+1.5)%H;
      var sg=ctx.createLinearGradient(0,scanY-10,0,scanY+10);
      sg.addColorStop(0,'rgba('+T.scan+',0)');
      sg.addColorStop(0.5,'rgba('+T.scan+',0.13)');
      sg.addColorStop(1,'rgba('+T.scan+',0)');
      ctx.fillStyle=sg;ctx.fillRect(0,scanY-10,W,20);

      requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    resize(); draw();
  }

  function init() {
    document.querySelectorAll('.hero-banner').forEach(renderBanner);
  }
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',init);
  } else { init(); }
})();
