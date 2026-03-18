/* ═══════════════════════════════════════════════════════════════
   HeroBanner Component — binah.co.il
   Renders thematic animated hero banners from data attributes.
   Usage: <div class="hero-banner" data-theme="tools"
                data-title="כל כלי ה-AI"
                data-subtitle="..."
                data-badge="..." data-badge-color="green|purple|cyan">
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ── Base network node positions (percent of 100×50 viewBox) ── */
  var NP = [
    [5,20],[18,72],[30,32],[46,85],[58,18],[70,60],[83,25],[93,75],
    [12,50],[40,55],[65,38],[77,85],[88,12],[52,48],[23,88],
    [68,12],[38,22],[85,50],[8,65],[60,90],[42,42],[95,35],[28,45]
  ];

  /* ── Generate SVG connection lines ── */
  function makeConnections() {
    var lines = '';
    var threshold = 28; // percent distance
    for (var i = 0; i < NP.length; i++) {
      for (var j = i + 1; j < NP.length; j++) {
        var dx = NP[j][0] - NP[i][0], dy = (NP[j][1] - NP[i][1]) * 2;
        var dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < threshold) {
          var alpha = (1 - dist/threshold) * 0.28;
          lines += '<line x1="'+NP[i][0]+'%" y1="'+NP[i][1]+'%" x2="'+NP[j][0]+'%" y2="'+NP[j][1]+'%"'
            + ' stroke="rgba(139,92,246,'+alpha.toFixed(2)+')" stroke-width="1"/>';
        }
      }
    }
    return lines;
  }

  /* ── Generate base network nodes ── */
  function makeNodes(accentEvery) {
    var nodes = '';
    accentEvery = accentEvery || 4;
    NP.forEach(function(p, i) {
      var isAccent = i % accentEvery === 0;
      var col = isAccent ? 'rgba(6,182,212,' : 'rgba(139,92,246,';
      var r = isAccent ? 3.2 : 2.4;
      var delay = (i * 0.22).toFixed(2);
      var dur   = (2.8 + (i % 5) * 0.4).toFixed(1);
      // glow halo
      nodes += '<circle cx="'+p[0]+'%" cy="'+p[1]+'%"'
        + ' r="'+(r*3.5)+'"'
        + ' fill="'+col+'0.12)"/>';
      // core dot
      nodes += '<circle cx="'+p[0]+'%" cy="'+p[1]+'%"'
        + ' r="'+r+'"'
        + ' fill="'+col+'0.85)"'
        + ' style="animation:hb-float '+dur+'s '+delay+'s ease-in-out infinite"/>';
    });
    return nodes;
  }

  /* ── Base SVG wrapper ── */
  function baseSVG(inner) {
    return '<svg class="hb-bg" viewBox="0 0 100 50" preserveAspectRatio="xMidYMid slice"'
      + ' xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0;width:100%;height:100%">'
      + inner + '</svg>';
  }

  /* ════════════════════════════════
     THEME SHAPES
  ════════════════════════════════ */

  /* ── Gear shape path (8 teeth) ── */
  function gearPath(cx, cy, ro, ri, teeth) {
    var pts = '', step = Math.PI / teeth;
    for (var i = 0; i < teeth * 2; i++) {
      var a = i * step - Math.PI/2;
      var r = i % 2 === 0 ? ro : ri;
      pts += (i===0?'M':'L') + (cx + r*Math.cos(a)).toFixed(2) + ',' + (cy + r*Math.sin(a)).toFixed(2);
    }
    return pts + 'Z';
  }

  function themeTools() {
    var shapes = '';
    // gear specs: [cx,cy,outer,inner,teeth,speed_s,dir,delay_s]
    var gears = [
      [8,  25, 8, 5.5, 8, 12, 1,  0],
      [88, 20, 6, 4,   6, 9,  -1, 1.5],
      [15, 80, 5, 3.5, 7, 15, 1,  0.8],
      [78, 78, 7, 5,   8, 11, -1, 0.3],
      [50, 10, 4, 2.8, 6, 8,  1,  0.5],
    ];
    gears.forEach(function(g) {
      var col = g[6] > 0 ? '#8b5cf6' : '#06b6d4';
      var spin = g[6] > 0 ? 'hb-spin-cw' : 'hb-spin-ccw';
      shapes += '<path d="'+gearPath(g[0],g[1],g[2],g[3],g[4])+'"'
        + ' fill="none" stroke="'+col+'" stroke-width="0.5" stroke-linejoin="round"'
        + ' style="transform-origin:'+g[0]+'px '+g[1]+'px;'
        +   'animation:'+spin+' '+g[5]+'s '+g[7]+'s linear infinite;opacity:0.2"/>';
      // inner hub circle
      shapes += '<circle cx="'+g[0]+'" cy="'+g[1]+'" r="1.5"'
        + ' fill="'+col+'" opacity="0.25"'
        + ' style="transform-origin:'+g[0]+'px '+g[1]+'px;'
        +   'animation:'+spin+' '+g[5]+'s '+g[7]+'s linear infinite"/>';
    });
    // bracket shapes { }
    shapes += '<text x="94" y="45" font-size="6" fill="rgba(6,182,212,0.15)" font-family="monospace"'
      + ' style="animation:hb-float 5s 0.5s ease-in-out infinite">{ }</text>';
    shapes += '<text x="2" y="42" font-size="5" fill="rgba(139,92,246,0.15)" font-family="monospace"'
      + ' style="animation:hb-float 4s 1s ease-in-out infinite">[ ]</text>';
    return shapes;
  }

  function themeGuides() {
    var shapes = '';
    // Books (closed rectangle + spine + lines)
    var books = [
      {x:6,  y:15, w:7, h:10, col:'#8b5cf6', d:0},
      {x:85, y:22, w:6,  h:9, col:'#06b6d4', d:0.8},
      {x:10, y:70, w:8, h:11, col:'#8b5cf6', d:1.2},
      {x:82, y:68, w:7, h:10, col:'#06b6d4', d:0.4},
    ];
    books.forEach(function(b) {
      // Cover rectangle
      shapes += '<rect x="'+b.x+'" y="'+b.y+'" width="'+b.w+'" height="'+b.h+'"'
        + ' fill="none" stroke="'+b.col+'" stroke-width="0.6" rx="0.3" opacity="0.22"'
        + ' style="animation:hb-float 4.5s '+b.d+'s ease-in-out infinite"/>';
      // Spine line (left edge)
      shapes += '<line x1="'+(b.x+1.2)+'" y1="'+b.y+'" x2="'+(b.x+1.2)+'" y2="'+(b.y+b.h)+'"'
        + ' stroke="'+b.col+'" stroke-width="0.8" opacity="0.18"'
        + ' style="animation:hb-float 4.5s '+b.d+'s ease-in-out infinite"/>';
      // Text lines inside book
      for (var l = 0; l < 3; l++) {
        var ly = b.y + 2.5 + l * 2.2;
        shapes += '<line x1="'+(b.x+2)+'" y1="'+ly+'" x2="'+(b.x+b.w-1)+'" y2="'+ly+'"'
          + ' stroke="'+b.col+'" stroke-width="0.5" opacity="0.13"'
          + ' style="animation:hb-float 4.5s '+b.d+'s ease-in-out infinite"/>';
      }
    });
    // Graduation cap hint (simple lines)
    shapes += '<line x1="48" y1="8" x2="55" y2="8" stroke="rgba(6,182,212,0.18)" stroke-width="1.5" stroke-linecap="round"/>';
    shapes += '<line x1="51.5" y1="8" x2="51.5" y2="12" stroke="rgba(6,182,212,0.15)" stroke-width="1"/>';
    // Scattered text line hints
    [[20,50,25],[60,35,18],[70,78,22]].forEach(function(tl,i) {
      shapes += '<line x1="'+tl[0]+'" y1="'+tl[1]+'" x2="'+(tl[0]+tl[2])+'" y2="'+tl[1]+'"'
        + ' stroke="rgba(139,92,246,0.1)" stroke-width="0.8" stroke-linecap="round"'
        + ' style="animation:hb-float 5s '+(i*0.6)+'s ease-in-out infinite"/>';
    });
    // Lightbulb hint: circle + rays
    shapes += '<circle cx="92" cy="12" r="2.5" fill="none" stroke="rgba(255,200,0,0.2)" stroke-width="0.7"'
      + ' style="animation:hb-float 3.8s 0.4s ease-in-out infinite"/>';
    return shapes;
  }

  function themeNews() {
    var shapes = '';
    // Newspaper column grid lines
    var cols = [15, 35, 55, 72];
    cols.forEach(function(cx) {
      shapes += '<line x1="'+cx+'" y1="5" x2="'+cx+'" y2="45"'
        + ' stroke="rgba(139,92,246,0.07)" stroke-width="0.8"/>';
    });
    // Horizontal row dividers
    [12,22,32].forEach(function(ry) {
      shapes += '<line x1="5" y1="'+ry+'" x2="95" y2="'+ry+'"'
        + ' stroke="rgba(6,182,212,0.07)" stroke-width="0.6"/>';
    });
    // Signal wave rings (3 pulses from a point)
    [[80,25],[18,40]].forEach(function(pt, pi) {
      [0,1,2].forEach(function(k) {
        var dur = 3 + k * 0.5;
        var del = (pi * 1.5 + k * 1.0).toFixed(1);
        shapes += '<circle cx="'+pt[0]+'" cy="'+pt[1]+'" r="3"'
          + ' fill="none" stroke="'+(k%2===0?'#8b5cf6':'#06b6d4')+'" stroke-width="0.8"'
          + ' style="animation:hb-wave-ring '+dur+'s '+del+'s ease-out infinite;opacity:0"/>';
      });
    });
    // "NEW" text hints
    shapes += '<text x="5" y="48" font-size="3.5" fill="rgba(6,182,212,0.18)" font-family="monospace" font-weight="700"'
      + ' style="animation:hb-flash 4s 0.5s ease-in-out infinite">LIVE</text>';
    // Traveling data line
    shapes += '<line x1="0" y1="3" x2="100" y2="3" stroke="rgba(6,182,212,0.15)" stroke-width="0.6"'
      + ' stroke-dasharray="8 4"/>';
    return shapes;
  }

  function themeQuiz() {
    var shapes = '';
    // Left arrow
    shapes += '<path d="M22,25 L10,25 M14,21 L10,25 L14,29"'
      + ' stroke="#8b5cf6" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round"'
      + ' opacity="0.3" style="animation:hb-float 3.5s ease-in-out infinite"/>';
    // Right arrow
    shapes += '<path d="M78,25 L90,25 M86,21 L90,25 L86,29"'
      + ' stroke="#06b6d4" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round"'
      + ' opacity="0.3" style="animation:hb-float 3.5s 0.6s ease-in-out infinite"/>';
    // Checkmark (left)
    shapes += '<path d="M7,42 L10,46 L17,38"'
      + ' stroke="rgba(0,255,136,0.4)" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"'
      + ' style="animation:hb-float 4s 0.3s ease-in-out infinite"/>';
    // X mark (right)
    shapes += '<path d="M83,38 L89,44 M89,38 L83,44"'
      + ' stroke="rgba(239,68,68,0.35)" stroke-width="1.5" fill="none" stroke-linecap="round"'
      + ' style="animation:hb-float 4s 0.9s ease-in-out infinite"/>';
    // Question marks
    [[50,8],[50,44]].forEach(function(q,i) {
      shapes += '<text x="'+q[0]+'" y="'+q[1]+'" text-anchor="middle" font-size="6"'
        + ' fill="rgba(139,92,246,0.15)" font-weight="900" font-family="sans-serif"'
        + ' style="animation:hb-float '+(4+i)+'s '+(i*0.8)+'s ease-in-out infinite">?</text>';
    });
    // Decision nodes + connecting lines
    var dnodes = [[30,20],[70,20],[50,38]];
    dnodes.forEach(function(n) {
      shapes += '<circle cx="'+n[0]+'" cy="'+n[1]+'" r="2.5"'
        + ' fill="none" stroke="rgba(139,92,246,0.25)" stroke-width="0.8"/>';
    });
    shapes += '<line x1="30" y1="20" x2="50" y2="38" stroke="rgba(139,92,246,0.12)" stroke-width="0.7"/>';
    shapes += '<line x1="70" y1="20" x2="50" y2="38" stroke="rgba(6,182,212,0.12)" stroke-width="0.7"/>';
    return shapes;
  }

  function themeBusiness() {
    var shapes = '';
    // Bar chart at bottom-right
    var bars = [
      {x:65, h:18, col:'#8b5cf6', d:0.2},
      {x:70, h:28, col:'#8b5cf6', d:0.4},
      {x:75, h:22, col:'#06b6d4', d:0.6},
      {x:80, h:35, col:'#8b5cf6', d:0.8},
      {x:85, h:42, col:'#06b6d4', d:1.0},
      {x:90, h:30, col:'#8b5cf6', d:1.2},
    ];
    // Baseline
    shapes += '<line x1="63" y1="47" x2="93" y2="47" stroke="rgba(139,92,246,0.2)" stroke-width="0.7"/>';
    bars.forEach(function(b) {
      shapes += '<rect x="'+b.x+'" y="'+(47-b.h)+'" width="3.5" height="'+b.h+'"'
        + ' fill="'+b.col+'" opacity="0.18"'
        + ' style="transform-origin:'+b.x+'px 47px;'
        +   'animation:hb-bar-grow 1.4s '+b.d+'s cubic-bezier(0.34,1.4,0.64,1) forwards;'
        +   'opacity:0"/>';
      // Cap line
      shapes += '<line x1="'+b.x+'" y1="'+(47-b.h)+'" x2="'+(b.x+3.5)+'" y2="'+(47-b.h)+'"'
        + ' stroke="'+b.col+'" stroke-width="0.8" opacity="0.4"'
        + ' style="animation:hb-bar-grow 1.4s '+b.d+'s forwards"/>';
    });
    // Trend arrow (up-right)
    shapes += '<path d="M65,42 Q75,28 90,14"'
      + ' fill="none" stroke="rgba(0,255,136,0.25)" stroke-width="1.2" stroke-linecap="round"'
      + ' stroke-dasharray="3 2"/>';
    shapes += '<path d="M87,11 L90,14 L87,17" fill="none" stroke="rgba(0,255,136,0.3)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>';
    // Briefcase outline (left)
    shapes += '<rect x="6" y="32" width="14" height="10" rx="1" fill="none" stroke="rgba(139,92,246,0.2)" stroke-width="0.7"'
      + ' style="animation:hb-float 5s 0.3s ease-in-out infinite"/>';
    shapes += '<path d="M10,32 L10,30 Q10,28 12,28 L14,28 Q16,28 16,30 L16,32"'
      + ' fill="none" stroke="rgba(139,92,246,0.2)" stroke-width="0.7"'
      + ' style="animation:hb-float 5s 0.3s ease-in-out infinite"/>';
    shapes += '<line x1="6" y1="37" x2="20" y2="37" stroke="rgba(139,92,246,0.12)" stroke-width="0.6"'
      + ' style="animation:hb-float 5s 0.3s ease-in-out infinite"/>';
    // Percent signs
    shapes += '<text x="88" y="49" font-size="4" fill="rgba(6,182,212,0.2)" font-family="monospace">%</text>';
    return shapes;
  }

  function themeCrazy() {
    var shapes = '';
    // Lightning bolts
    var bolts = [
      {d:'M20,4 L16,18 L19,18 L14,32', col:'rgba(255,200,0,0.25)', del:0},
      {d:'M75,2 L70,16 L74,16 L68,30', col:'rgba(255,150,0,0.22)', del:0.7},
      {d:'M88,28 L85,38 L87,38 L83,48', col:'rgba(255,200,0,0.2)',  del:1.4},
      {d:'M8,30 L5,42 L8,42 L4,49',    col:'rgba(255,180,50,0.18)', del:0.4},
      {d:'M55,3 L52,13 L54,13 L50,22', col:'rgba(255,220,0,0.2)',   del:1.1},
    ];
    bolts.forEach(function(b) {
      shapes += '<path d="'+b.d+'" fill="none" stroke="'+b.col+'" stroke-width="1.5"'
        + ' stroke-linecap="round" stroke-linejoin="round"'
        + ' style="animation:hb-flash 2.5s '+b.del+'s ease-in-out infinite"/>';
    });
    // Explosion sparks (star lines from center)
    var cx = 50, cy = 25;
    for (var a = 0; a < 360; a += 45) {
      var rad = a * Math.PI / 180;
      var ex = (cx + 8 * Math.cos(rad)).toFixed(1);
      var ey = (cy + 4 * Math.sin(rad)).toFixed(1);
      shapes += '<line x1="'+cx+'" y1="'+cy+'" x2="'+ex+'" y2="'+ey+'"'
        + ' stroke="rgba(255,200,0,0.12)" stroke-width="0.8" stroke-linecap="round"'
        + ' style="animation:hb-flash '+(2+a/180*0.4).toFixed(1)+'s '+(a/360).toFixed(2)+'s ease-in-out infinite"/>';
    }
    // ! marks
    ['4,14', '93,38', '14,6'].forEach(function(pos, i) {
      shapes += '<text x="'+pos.split(',')[0]+'" y="'+pos.split(',')[1]+'"'
        + ' font-size="7" fill="rgba(255,160,0,0.2)" font-weight="900" font-family="sans-serif"'
        + ' style="animation:hb-flash '+(2.5+i*0.3)+'s '+(i*0.5)+'s ease-in-out infinite">!</text>';
    });
    return shapes;
  }

  function themeArticles() {
    var shapes = '';
    // Pen/quill stroke (long curved path)
    shapes += '<path d="M5,45 Q20,20 40,30 Q55,38 70,15 Q80,5 92,8"'
      + ' fill="none" stroke="rgba(139,92,246,0.28)" stroke-width="1.5" stroke-linecap="round"'
      + ' stroke-dasharray="300" stroke-dashoffset="300"'
      + ' style="animation:hb-pen-draw 3.5s 0.3s ease-out forwards"/>';
    // Pen nib at end
    shapes += '<path d="M88,10 L92,8 L90,12 Z"'
      + ' fill="rgba(139,92,246,0.25)"/>';
    // Text line blocks (paragraphs)
    [[5,20,40],[5,24,32],[5,28,36],[52,20,38],[52,24,28],[52,28,33]].forEach(function(tl,i) {
      shapes += '<rect x="'+tl[0]+'" y="'+tl[1]+'" width="'+tl[2]+'" height="1.2"'
        + ' rx="0.6" fill="rgba(6,182,212,0.1)"'
        + ' style="animation:hb-float '+(4+i*0.3)+'s '+(i*0.25)+'s ease-in-out infinite"/>';
    });
    // Quote marks
    shapes += '<text x="5" y="12" font-size="10" fill="rgba(139,92,246,0.12)" font-family="serif">"</text>';
    shapes += '<text x="88" y="48" font-size="10" fill="rgba(6,182,212,0.1)" font-family="serif">"</text>';
    return shapes;
  }

  function themeProducts() {
    var shapes = '';
    // Circuit board traces (orthogonal lines)
    var traces = [
      'M5,10 L20,10 L20,25 L35,25',
      'M5,38 L15,38 L15,20 L30,20',
      'M80,8  L90,8  L90,22 L75,22',
      'M72,40 L85,40 L85,30',
      'M40,5  L40,15 L55,15',
      'M60,45 L60,35 L75,35',
    ];
    traces.forEach(function(d,i) {
      shapes += '<path d="'+d+'" fill="none" stroke="rgba(0,255,136,0.18)" stroke-width="0.8"'
        + ' stroke-linecap="round" stroke-linejoin="round"'
        + ' stroke-dasharray="60" stroke-dashoffset="60"'
        + ' style="animation:hb-dash-travel 3s '+(i*0.5)+'s ease-in-out infinite alternate"/>';
      // Endpoint dot
      var pts = d.match(/L(\d+),(\d+)$/);
      if (pts) {
        shapes += '<circle cx="'+pts[1]+'" cy="'+pts[2]+'" r="1.5"'
          + ' fill="rgba(0,255,136,0.4)"'
          + ' style="animation:hb-float '+(3.5+i*0.3)+'s '+(i*0.4)+'s ease-in-out infinite"/>';
      }
    });
    // HUD rings
    [[50,25,8],[50,25,14],[50,25,20]].forEach(function(r,i) {
      shapes += '<circle cx="'+r[0]+'" cy="'+r[1]+'" r="'+r[2]+'"'
        + ' fill="none" stroke="rgba(0,255,136,0.08)" stroke-width="0.5"'
        + ' stroke-dasharray="'+(i%2===0?'4 3':'2 5')+'"'
        + ' style="animation:hb-spin-cw '+(20+i*8)+'s linear infinite"/>';
    });
    return shapes;
  }

  function themeHome() {
    // Neural/brain network — enhanced base network
    var shapes = '';
    // Extra large central glow
    shapes += '<circle cx="50" cy="25" r="18" fill="rgba(139,92,246,0.04)"/>';
    shapes += '<circle cx="50" cy="25" r="10" fill="rgba(6,182,212,0.04)"/>';
    // Orbital rings
    [[50,25,20],[50,25,30]].forEach(function(r,i) {
      shapes += '<ellipse cx="'+r[0]+'" cy="'+r[1]+'" rx="'+r[2]+'" ry="'+(r[2]*0.45)+'"'
        + ' fill="none" stroke="rgba(139,92,246,0.07)" stroke-width="0.6"'
        + ' style="animation:hb-spin-cw '+(18+i*12)+'s linear infinite"/>';
    });
    return shapes;
  }

  /* ── Map theme key → shape generator ── */
  var THEME_MAP = {
    'tools':    themeTools,
    'guides':   themeGuides,
    'news':     themeNews,
    'quiz':     themeQuiz,
    'business': themeBusiness,
    'crazy':    themeCrazy,
    'articles': themeArticles,
    'products': themeProducts,
    'home':     themeHome,
  };

  /* ── Badge color defaults per theme ── */
  var BADGE_COLOR = {
    'tools': 'purple', 'guides': 'cyan', 'news': 'cyan',
    'quiz': 'purple', 'business': 'green', 'crazy': 'purple',
    'articles': 'cyan', 'products': 'green', 'home': 'purple',
  };

  /* ── Main render ── */
  function render(el) {
    var theme    = el.dataset.theme    || 'home';
    var title    = el.dataset.title    || '';
    var subtitle = el.dataset.subtitle || '';
    var badge    = el.dataset.badge    || '';
    var badgeCol = el.dataset.badgeColor || BADGE_COLOR[theme] || 'purple';

    var shapeFn  = THEME_MAP[theme] || themeHome;
    var themeShapes = shapeFn();
    var connections = makeConnections();
    var nodes       = makeNodes(theme === 'crazy' ? 3 : 4);

    /* Badge HTML */
    var badgeHTML = badge
      ? '<div class="hb-badge ' + badgeCol + '">'
          + '<span class="hb-badge-dot"></span>'
          + badge
        + '</div>'
      : '';

    /* Title — keep any existing <span> or <br> in the title string */
    var subtitleHTML = subtitle
      ? '<p class="hb-subtitle">' + subtitle + '</p>'
      : '';

    el.innerHTML =
      /* SVG layer */
      '<svg class="hb-bg" viewBox="0 0 100 50" preserveAspectRatio="xMidYMid slice"'
      + ' xmlns="http://www.w3.org/2000/svg">'
      + connections
      + themeShapes
      + nodes
      + '</svg>'
      /* Content */
      + '<div class="hb-content">'
      +   badgeHTML
      +   '<h1 class="hb-title">' + title + '</h1>'
      +   subtitleHTML
      + '</div>';
  }

  /* ── Init all banners on page ── */
  function init() {
    document.querySelectorAll('.hero-banner').forEach(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
