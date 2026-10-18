/* A view of the synthetic engine. Screen geometry never changes model velocities. */
(function (global) {
  'use strict';
  var ns = global.JPWCapitalCurrents = global.JPWCapitalCurrents || {};
  function create(canvas) {
    var ctx = canvas.getContext('2d'), background = document.createElement('canvas'), bg = background.getContext('2d');
    var width = 0, height = 0, ratio = 1, plot, dead = false, cacheKey = '', streamCount = 0, vectorCount = 0;
    function point(s) { return { x: plot.x + (s.q + 1) * plot.w / 2, y: plot.y + (6 - s.p) * plot.h / 12 }; }
    function arrow(c, x, y, dx, dy, max, color, weight) {
      var magnitude = Math.hypot(dx, dy); if (magnitude < .001) return;
      var scale = Math.min(1, max / magnitude); dx *= scale; dy *= scale;
      var a = Math.atan2(dy, dx), head = Math.min(4, Math.hypot(dx, dy) * .35);
      c.strokeStyle = color; c.lineWidth = weight || 1; c.beginPath(); c.moveTo(x - dx / 2, y - dy / 2); c.lineTo(x + dx / 2, y + dy / 2); c.stroke();
      c.beginPath(); c.moveTo(x + dx / 2 - head * Math.cos(a - .5), y + dy / 2 - head * Math.sin(a - .5)); c.lineTo(x + dx / 2, y + dy / 2); c.lineTo(x + dx / 2 - head * Math.cos(a + .5), y + dy / 2 - head * Math.sin(a + .5)); c.stroke();
    }
    function resize() {
      if (dead) return false;
      var r = { width: canvas.clientWidth, height: canvas.clientHeight }, nextRatio = Math.min(global.devicePixelRatio || 1, 3);
      if (Math.abs(r.width - width) < .5 && Math.abs(r.height - height) < .5 && nextRatio === ratio) return false;
      width = Math.max(1, r.width); height = Math.max(1, r.height); ratio = nextRatio;
      canvas.width = background.width = Math.round(width * ratio); canvas.height = background.height = Math.round(height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0); bg.setTransform(ratio, 0, 0, ratio, 0, 0);
      plot = { x: width < 500 ? 44 : 58, y: 32, w: Math.max(1, width - (width < 500 ? 64 : 90)), h: Math.max(1, height - 101) }; cacheKey = ''; return true;
    }
    function clip(c) { c.beginPath(); c.rect(plot.x, plot.y, plot.w, plot.h); c.clip(); }
    function staticField(params, layers) {
      var key = JSON.stringify([params, layers.vectors, layers.streamlines]); if (key === cacheKey) return; cacheKey = key;
      bg.fillStyle = '#091a2c'; bg.fillRect(0, 0, width, height); bg.font = '11px system-ui, sans-serif'; bg.textBaseline = 'middle';
      for (var p = -6; p <= 6; p += 2) {
        var y = point({ q: 0, p: p }).y; bg.strokeStyle = p === 0 ? '#42566d' : '#1c3046'; bg.lineWidth = 1; bg.beginPath(); bg.moveTo(plot.x, y); bg.lineTo(plot.x + plot.w, y); bg.stroke(); bg.fillStyle = '#9db3ca'; bg.textAlign = 'right'; bg.fillText((p > 0 ? '+' : '') + p, plot.x - 9, y);
      }
      [-1, -.5, 0, .5, 1].forEach(function (q) {
        var x = point({ q: q, p: 0 }).x; bg.strokeStyle = q === 0 ? '#8da5bc' : '#1c3046'; bg.lineWidth = q === 0 ? 1.25 : 1; bg.beginPath(); bg.moveTo(x, plot.y); bg.lineTo(x, plot.y + plot.h); bg.stroke(); bg.fillStyle = '#9db3ca'; bg.textAlign = 'center'; bg.fillText(String(q).replace('.', ','), x, plot.y + plot.h + 16);
      });
      bg.fillStyle = '#c9d8e8'; bg.textAlign = 'left'; bg.fillText(width < 280 ? 'p · preço (pontos) ↑' : width < 500 ? 'p · preço (pontos fictícios) ↑' : 'p · deslocamento do preço (pontos fictícios) ↑', plot.x, 14);
      bg.textAlign = 'center'; bg.fillText(width < 280 ? 'q · pressão →' : 'q · pressão líquida efetiva →', plot.x + plot.w / 2, height - 29);
      bg.save(); clip(bg); streamCount = 0;
      if (layers.streamlines) {
        bg.strokeStyle = 'rgba(58,137,177,.28)'; bg.lineWidth = .8;
        for (var row = 0; row < 9; row++) for (var col = 0; col < 9; col++) {
          var path = ns.engine.trace({ q: -.98 + col * .245, p: -5.95 + row * 1.48, t: 0 }, params, { steps: 260, dt: .04 });
          bg.beginPath(); var previous = null, moved = false;
          path.forEach(function (s) { var xy = point(s); if (!previous) bg.moveTo(xy.x, xy.y); else if (Math.hypot(xy.x - previous.x, xy.y - previous.y) > .001) { bg.lineTo(xy.x, xy.y); moved = true; } previous = xy; }); if (moved) { bg.stroke(); streamCount++; }
        }
      }
      vectorCount = 0;
      if (layers.vectors) {
        var cols = width < 500 ? 13 : 23, rows = 17;
        for (var j = 0; j < rows; j++) for (var i = 0; i < cols; i++) {
          var s = { q: -.95 + i * 1.9 / (cols - 1), p: -5.8 + j * 11.6 / (rows - 1), t: 0 }, f = ns.engine.fieldAt(s, params), xy = point(s);
          // One common visual interval (0.055 s) across ALL arrows, capped at 28px.
          arrow(bg, xy.x, xy.y, f.dq * plot.w / 2 * .055, -f.dp * plot.h / 12 * .055, 28, '#59bfe0', 1.1); vectorCount++;
        }
      }
      bg.restore();
    }
    function draw(model) {
      if (dead) return; resize(); staticField(model.params, model.layers);
      ctx.clearRect(0, 0, width, height); ctx.drawImage(background, 0, 0, width, height); ctx.save(); clip(ctx);
      if (model.layers.trail && model.trail.length > 1) {
        ctx.strokeStyle = '#ffbf72'; ctx.lineWidth = 2.2; ctx.beginPath(); model.trail.forEach(function (s, i) { var xy = point(s); if (i) ctx.lineTo(xy.x, xy.y); else ctx.moveTo(xy.x, xy.y); }); ctx.stroke();
      }
      if (model.layers.particles) { ctx.fillStyle = '#cce8f8'; model.particles.forEach(function (s) { var xy = point(s); ctx.beginPath(); ctx.arc(xy.x, xy.y, 1.65, 0, Math.PI * 2); ctx.fill(); }); }
      var xy = point(model.state), f = ns.engine.fieldAt(model.state, model.params);
      // A diamond and a thick amber arrow distinguish the selected scenario without color alone.
      ctx.fillStyle = '#ffcc86'; ctx.strokeStyle = '#20192a'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(xy.x, xy.y - 7); ctx.lineTo(xy.x + 7, xy.y); ctx.lineTo(xy.x, xy.y + 7); ctx.lineTo(xy.x - 7, xy.y); ctx.closePath(); ctx.fill(); ctx.stroke();
      arrow(ctx, xy.x, xy.y, f.dq * plot.w / 2 * .055, -f.dp * plot.h / 12 * .055, 28, '#ffbd77', 2.3);
      ctx.restore();
    }
    function pick(x, y) {
      if (!plot || dead || x < plot.x || x > plot.x + plot.w || y < plot.y || y > plot.y + plot.h) return null;
      return { q: (x - plot.x) * 2 / plot.w - 1, p: 6 - (y - plot.y) * 12 / plot.h, t: 0 };
    }
    return { draw: draw, pick: pick, resize: resize, snapshot: function () { return { vectors: vectorCount, streamlines: streamCount }; }, destroy: function () { dead = true; canvas.width = canvas.height = background.width = background.height = 0; } };
  }
  ns.renderer = Object.freeze({ create: create });
})(window);
