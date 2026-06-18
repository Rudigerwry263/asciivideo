/* charvid.js - browser runtime for character/terminal animations.
 * Mirrors the Python engine: a monospace character grid drawn on Canvas 2D,
 * with a blurred additive "phosphor" glow layer, CJK double-width glyphs, and
 * the same element + animation semantics. Driven by a seekable timeline.
 * Public API:  Charvid.play(spec, opts, mountSelector)
 */
(function (global) {
  "use strict";

  // ---- deterministic PRNG (string-seeded) --------------------------------
  function xmur3(str) {
    let h = 1779033703 ^ str.length;
    for (let i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    return function () {
      h = Math.imul(h ^ (h >>> 16), 2246822507);
      h = Math.imul(h ^ (h >>> 13), 3266489909);
      h ^= h >>> 16;
      return h >>> 0;
    };
  }
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function rng() {
    const seed = Array.prototype.join.call(arguments, "|");
    const s = xmur3(seed);
    const next = mulberry32(s());
    return {
      random: next,
      uniform: function (a, b) { return a + (b - a) * next(); },
      randrange: function (n) { return Math.floor(next() * n); },
    };
  }

  // ---- East Asian width --------------------------------------------------
  function isWide(ch) {
    const c = ch.codePointAt(0);
    return (
      (c >= 0x1100 && c <= 0x115f) || (c >= 0x2e80 && c <= 0x303e) ||
      (c >= 0x3041 && c <= 0x33ff) || (c >= 0x3400 && c <= 0x4dbf) ||
      (c >= 0x4e00 && c <= 0x9fff) || (c >= 0xa000 && c <= 0xa4cf) ||
      (c >= 0xac00 && c <= 0xd7a3) || (c >= 0xf900 && c <= 0xfaff) ||
      (c >= 0xfe30 && c <= 0xfe4f) || (c >= 0xff00 && c <= 0xff60) ||
      (c >= 0xffe0 && c <= 0xffe6) || (c >= 0x20000 && c <= 0x3fffd)
    );
  }
  function charCells(ch) { return isWide(ch) ? 2 : 1; }
  function lineCells(s) {
    let n = 0;
    for (const ch of s) n += charCells(ch);
    return n;
  }

  // ---- easing ------------------------------------------------------------
  function clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  const EASE = {
    linear: (t) => t,
    ease_in: (t) => t * t,
    ease_out: (t) => 1 - (1 - t) * (1 - t),
    ease_in_out: (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
    ease_out_cubic: (t) => 1 - Math.pow(1 - t, 3),
    ease_in_out_cubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    ease_out_quart: (t) => 1 - Math.pow(1 - t, 4),
    ease_out_expo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
    ease_out_back: (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    ease_out_elastic: (t) => { if (t <= 0) return 0; if (t >= 1) return 1; const c4 = (2 * Math.PI) / 3; return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1; },
  };
  function ease(name) { return EASE[name] || EASE.ease_out_cubic; }

  const SCRAMBLE = "!@#$%^&*()_+-={}[]|;:<>?/01XY01<>~";

  // ---- canvas wrapper ----------------------------------------------------
  function CharCanvas(spec) {
    this.w = spec.width; this.h = spec.height;
    this.cw = spec.cell_w; this.ch = spec.cell_h;
    this.cols = spec.cols; this.rows = spec.rows;
    this.fontSize = spec.font_size;
    this.glowRadius = spec.glow_radius; this.glowGain = spec.glow_gain;
    this.fontStack = '"SF Mono", SFMono-Regular, ui-monospace, Menlo, Consolas, ' +
      '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", monospace';

    this.base = document.createElement("canvas");
    this.base.width = this.w; this.base.height = this.h;
    this.glow = document.createElement("canvas");
    this.glow.width = this.w; this.glow.height = this.h;
    this.bx = this.base.getContext("2d");
    this.gx = this.glow.getContext("2d");
    this._setFont(this.bx); this._setFont(this.gx);
  }
  CharCanvas.prototype._setFont = function (ctx) {
    ctx.font = this.fontSize + "px " + this.fontStack;
    ctx.textBaseline = "top";
  };
  CharCanvas.prototype.begin = function () {
    this.bx.clearRect(0, 0, this.w, this.h);
    this.gx.clearRect(0, 0, this.w, this.h);
    this.bx.globalAlpha = 1; this.gx.globalAlpha = 1;
  };
  CharCanvas.prototype.glyph = function (x, y, ch, color, alpha, glow) {
    if (alpha <= 0 || ch === " " || ch === "") return;
    const wide = isWide(ch);
    const px = wide ? x + this.cw : x;
    const align = wide ? "center" : "left";
    this.bx.globalAlpha = alpha; this.bx.fillStyle = color;
    this.bx.textAlign = align; this.bx.textBaseline = "top";
    this.bx.fillText(ch, px, y);
    if (glow > 0) {
      this.gx.globalAlpha = alpha * glow; this.gx.fillStyle = color;
      this.gx.textAlign = align; this.gx.textBaseline = "top";
      this.gx.fillText(ch, px, y);
    }
  };
  CharCanvas.prototype.glyphCentered = function (cx, cy, ch, color, alpha, glow) {
    if (alpha <= 0 || ch === " " || ch === "") return;
    this.bx.globalAlpha = alpha; this.bx.fillStyle = color;
    this.bx.textAlign = "center"; this.bx.textBaseline = "middle";
    this.bx.fillText(ch, cx, cy);
    if (glow > 0) {
      this.gx.globalAlpha = alpha * glow; this.gx.fillStyle = color;
      this.gx.textAlign = "center"; this.gx.textBaseline = "middle";
      this.gx.fillText(ch, cx, cy);
    }
  };
  CharCanvas.prototype.line = function (col, row, text, color, alpha, glow) {
    let x = col * this.cw; const y = row * this.ch;
    for (const ch of text) {
      if (ch !== " ") this.glyph(x, y, ch, color, alpha, glow);
      x += charCells(ch) * this.cw;
    }
  };
  CharCanvas.prototype.block = function (lines, oc, orow, color, alpha, glow) {
    for (let r = 0; r < lines.length; r++) this.line(oc, orow + r, lines[r], color, alpha, glow);
  };
  CharCanvas.prototype.composite = function (view, bg) {
    view.globalCompositeOperation = "source-over";
    view.globalAlpha = 1; view.filter = "none";
    view.fillStyle = bg; view.fillRect(0, 0, this.w, this.h);
    if (this.glowRadius > 0 && this.glowGain > 0) {
      view.save();
      view.globalCompositeOperation = "lighter";
      view.filter = "blur(" + this.glowRadius + "px)";
      view.globalAlpha = Math.min(1, this.glowGain);
      view.drawImage(this.glow, 0, 0);
      view.restore();
    }
    view.globalCompositeOperation = "source-over";
    view.globalAlpha = 1; view.filter = "none";
    view.drawImage(this.base, 0, 0);
  };

  // ---- glyph layout ------------------------------------------------------
  function layout(lines) {
    const glyphs = []; let ncols = 0;
    for (let ri = 0; ri < lines.length; ri++) {
      let d = 0;
      for (const ch of lines[ri]) {
        if (ch !== " ") glyphs.push([d, ri, ch]);
        d += charCells(ch);
      }
      if (d > ncols) ncols = d;
    }
    return { glyphs: glyphs, ncols: ncols };
  }

  function windowOf(el, t) {
    const end = el.start + el.dur;
    if (t < el.start - 1e-6 || t > end + 1e-6) return null;
    const local = t - el.start;
    return {
      in_p: clamp01(local / el.in_dur),
      out_p: clamp01((end - t) / el.out_dur),
      local: local,
    };
  }

  // ---- element drawing ---------------------------------------------------
  function drawGlyph(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    if (!el._lay) el._lay = layout(el.lines);
    let lines = el.lines, lay = el._lay;
    // blink idle swaps to the alternate frame
    if (el.idle === "blink" && el.blink_lines && (t % el.blink_every) < 0.14) {
      lines = el.blink_lines;
      if (!el._layBlink) el._layBlink = layout(el.blink_lines);
      lay = el._layBlink;
    }
    const glyphs = lay.glyphs, ncols = lay.ncols, nrows = lines.length;
    const cw = C.cw, ch = C.ch;

    // origin (top-left in cells)
    let oc, orow;
    if (el.col != null && el.row != null) { oc = el.col; orow = el.row; }
    else if (el.cx != null && el.cy != null) { oc = el.cx - ncols / 2; orow = el.cy - nrows / 2; }
    else { oc = (C.cols - ncols) / 2; orow = (C.rows - nrows) / 2; }

    // idle offset / alpha
    if (el.idle === "bob") orow += Math.sin(t * 2) * 0.18;
    let baseA = el.alpha;
    if (el.idle === "flicker") baseA *= 0.78 + 0.22 * rng(el.seed, Math.floor(t * 12)).random();

    const ox = oc * cw, oy = orow * ch;
    const ei = ease(el.ease_in), eo = ease(el.ease_out);
    const outFactor = (el.anim_out === "fade" || el.anim_out === "dissolve" || el.anim_out === "scatter") ? eo(w.out_p) : 1;
    const col = el.color, glow = el.glow;

    if (el.anim_in === "scatter" && w.in_p < 1) return scatter(C, el, glyphs, ox, oy, cw, ch, ei(w.in_p), baseA, outFactor, false);
    if (el.anim_in === "scramble" && w.in_p < 1) return scramble(C, el, glyphs, ox, oy, cw, ch, w.in_p, baseA, outFactor);
    if (el.anim_in === "type" && w.in_p < 1) return typeIn(C, el, glyphs, ox, oy, cw, ch, w.in_p, baseA, outFactor);
    if (el.anim_in === "wipe" && w.in_p < 1) return wipe(C, el, glyphs, ox, oy, cw, ch, ei(w.in_p), baseA, outFactor, nrows);
    if ((el.anim_in === "rise" || el.anim_in === "drop" || el.anim_in === "slide_left" || el.anim_in === "slide_right") && w.in_p < 1)
      return slide(C, el, lines, oc, orow, ei(w.in_p), baseA, outFactor);

    let a = baseA * outFactor;
    if (el.anim_in === "fade" && w.in_p < 1) a *= ei(w.in_p);
    if (el.anim_out === "dissolve" && w.out_p < 1) return dissolve(C, el, glyphs, ox, oy, cw, ch, w.out_p, baseA);
    if (el.anim_out === "scatter" && w.out_p < 1) return scatter(C, el, glyphs, ox, oy, cw, ch, w.out_p, baseA, 1, true);
    C.block(lines, oc, orow, col, a, glow);
  }

  function slide(C, el, lines, oc, orow, p, baseA, outFactor) {
    const travel = 1.6;
    if (el.anim_in === "rise") orow += travel * (1 - p);
    else if (el.anim_in === "drop") orow -= travel * (1 - p);
    else if (el.anim_in === "slide_left") oc += travel * (1 - p);
    else oc -= travel * (1 - p);
    C.block(lines, oc, orow, el.color, baseA * p * outFactor, el.glow);
  }
  function typeIn(C, el, glyphs, ox, oy, cw, ch, in_p, baseA, outFactor) {
    const n = glyphs.length, revealed = Math.round(in_p * n);
    const order = glyphs.map((g, i) => i).sort((a, b) => (glyphs[a][1] - glyphs[b][1]) || (glyphs[a][0] - glyphs[b][0]));
    const a = baseA * outFactor;
    for (let k = 0; k < revealed && k < n; k++) {
      const g = glyphs[order[k]];
      C.glyph(ox + g[0] * cw, oy + g[1] * ch, g[2], el.color, a, el.glow);
    }
  }
  function wipe(C, el, glyphs, ox, oy, cw, ch, p, baseA, outFactor, nrows) {
    const cutoff = p * nrows, a = baseA * outFactor;
    for (const g of glyphs) {
      if (g[1] <= cutoff) C.glyph(ox + g[0] * cw, oy + g[1] * ch, g[2], el.color, a * clamp01(cutoff - g[1]), el.glow);
    }
  }
  function scatter(C, el, glyphs, ox, oy, cw, ch, p, baseA, outFactor, reverse) {
    const r = rng(el.seed, "scatter");
    const spread = Math.max(C.w, C.h) * 0.3;
    const pp = reverse ? 1 - p : p;
    const a = baseA * outFactor * (reverse ? pp : clamp01(p * 1.4));
    for (const g of glyphs) {
      const ang = r.uniform(0, 2 * Math.PI), dist = r.uniform(0.25, 1) * spread;
      const sx = ox + g[0] * cw + Math.cos(ang) * dist;
      const sy = oy + g[1] * ch + Math.sin(ang) * dist;
      const tx = ox + g[0] * cw, ty = oy + g[1] * ch;
      C.glyph(lerp(sx, tx, p), lerp(sy, ty, p), g[2], el.color, a, el.glow);
    }
  }
  function scramble(C, el, glyphs, ox, oy, cw, ch, in_p, baseA, outFactor) {
    const r = rng(el.seed, "scramble"), resolve = [];
    for (let i = 0; i < glyphs.length; i++) resolve.push(r.uniform(0, 0.7));
    const tick = Math.floor(in_p * 30), a = baseA * outFactor;
    for (let i = 0; i < glyphs.length; i++) {
      const g = glyphs[i], rt = resolve[i];
      if (in_p >= rt + 0.18) C.glyph(ox + g[0] * cw, oy + g[1] * ch, g[2], el.color, a, el.glow);
      else if (in_p >= rt - 0.05) {
        const rc = SCRAMBLE[rng(el.seed, g[0], g[1], tick).randrange(SCRAMBLE.length)];
        C.glyph(ox + g[0] * cw, oy + g[1] * ch, rc, el.color, a * 0.75, el.glow);
      }
    }
  }
  function dissolve(C, el, glyphs, ox, oy, cw, ch, out_p, baseA) {
    const r = rng(el.seed, "dissolve");
    for (const g of glyphs) {
      if (out_p > r.random()) C.glyph(ox + g[0] * cw, oy + g[1] * ch, g[2], el.color, baseA * out_p, el.glow);
    }
  }

  function drawLoadbar(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    const fillDur = el.fill_dur != null ? el.fill_dur : el.dur - el.out_dur;
    const p = ease(el.ease_in)(clamp01(w.local / Math.max(1e-4, fillDur)));
    const pct = Math.round(p * 100), filled = Math.round(p * el.width);
    const bar = "[" + el.fill_char.repeat(filled) + el.empty_char.repeat(el.width - filled) + "]";
    const head = el.label + " " + pct + "%";
    const a = el.alpha * ease(el.ease_in)(w.in_p) * (el.anim_out === "fade" ? w.out_p : 1);
    const cx = el.cx != null ? el.cx : C.cols / 2, cy = el.cy != null ? el.cy : C.rows / 2;
    C.line(cx - lineCells(head) / 2, cy - 1, head, el.label_color, a, el.glow);
    C.line(cx - lineCells(bar) / 2, cy, bar, el.fill_color, a, el.glow);
  }

  function drawParticles(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    const aEnv = el.alpha * EASE.ease_out(w.in_p) * (el.anim_out === "fade" ? w.out_p : 1);
    const reg = el.region || [0, 0, C.cols, C.rows];
    const c0 = reg[0], r0 = reg[1], c1 = reg[2], r1 = reg[3];
    const cw = C.cw, ch = C.ch;
    for (let i = 0; i < el.count; i++) {
      const r = rng(el.seed, "p", i);
      const bx = r.uniform(c0, c1), by = r.uniform(r0, r1);
      const vy = r.uniform(-1, 1) * el.speed, vx = r.uniform(-1, 1) * el.speed * 0.4;
      let x = bx + vx * w.local, y = by + vy * w.local;
      x = c0 + (((x - c0) % Math.max(1e-3, c1 - c0)) + (c1 - c0)) % Math.max(1e-3, c1 - c0);
      y = r0 + (((y - r0) % Math.max(1e-3, r1 - r0)) + (r1 - r0)) % Math.max(1e-3, r1 - r0);
      const chr = el.chars[r.randrange(el.chars.length)];
      const col = el.colors[r.randrange(el.colors.length)];
      let tw = 1;
      if (el.twinkle) tw = 0.45 + 0.55 * (0.5 + 0.5 * Math.sin(t * 2.4 + i));
      C.glyph(x * cw, y * ch, chr, col, aEnv * tw, el.glow);
    }
  }

  function drawBorder(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    const m = el.margin, cols = C.cols, rows = C.rows, cells = [];
    for (let c = m; c < cols - m; c++) { cells.push([c, m]); cells.push([c, rows - m - 1]); }
    for (let r = m; r < rows - m; r++) { cells.push([m, r]); cells.push([cols - m - 1, r]); }
    const a = el.alpha * (el.anim_out === "fade" ? w.out_p : 1);
    const reveal = el.draw_on ? ease(el.ease_in)(w.in_p) : 1;
    const nshow = Math.floor(reveal * cells.length), sym = el.symbol || "|";
    for (let idx = 0; idx < cells.length; idx++) {
      if (el.draw_on && idx > nshow) continue;
      const c = cells[idx][0], r = cells[idx][1];
      C.glyph(c * C.cw, r * C.ch, sym[idx % sym.length], el.color, a, el.glow);
    }
  }

  function drawSymgrid(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    const cx = el.cx != null ? el.cx : C.cols / 2, cy = el.cy != null ? el.cy : C.rows / 2;
    const c0 = cx - el.cols_n / 2, r0 = cy - el.rows_n / 2;
    const a = el.alpha * (el.anim_out === "fade" ? w.out_p : 1);
    const cw = C.cw, ch = C.ch, sy = el.symbols;
    for (let rr = 0; rr < el.rows_n; rr++) {
      for (let cc = 0; cc < el.cols_n; cc++) {
        if (el.hollow && cc > 0 && cc < el.cols_n - 1 && rr > 0 && rr < el.rows_n - 1) continue;
        const r = rng(el.seed, cc, rr), resolve = r.uniform(0, 0.6);
        let sym, aa;
        if (el.anim_in === "scramble" && w.in_p < resolve + 0.18) {
          if (w.in_p < resolve - 0.05) continue;
          const tick = Math.floor(w.in_p * 24);
          sym = sy[rng(el.seed, cc, rr, tick).randrange(sy.length)]; aa = a * 0.7;
        } else { sym = sy[r.randrange(sy.length)]; aa = a; }
        const tw = 0.82 + 0.18 * Math.sin(t * 2 + cc + rr);
        C.glyph((c0 + cc) * cw, (r0 + rr) * ch, sym, el.color, aa * tw, el.glow);
      }
    }
  }

  function drawClock(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    const a = el.alpha * ease(el.ease_in)(w.in_p) * (el.anim_out === "fade" ? w.out_p : 1);
    const cw = C.cw, ch = C.ch;
    const cx = (el.cx != null ? el.cx : C.cols / 2) * cw;
    const cy = (el.cy != null ? el.cy : C.rows / 2) * ch;
    const R = el.radius * cw;
    for (let k = 0; k < 60; k++) {
      const ang = -Math.PI / 2 + (2 * Math.PI * k) / 60, major = k % 5 === 0;
      const rr = major ? R * 1.04 : R;
      C.glyphCentered(cx + Math.cos(ang) * rr, cy + Math.sin(ang) * rr,
        major ? el.tick_char : el.ring_char, el.color, a * (major ? 1 : 0.5), el.glow);
    }
    const hc = el.hand_color || el.color;
    const ma = -Math.PI / 2 + 2 * Math.PI * (w.local / el.period);
    const ha = -Math.PI / 2 + 2 * Math.PI * (w.local / (el.period * 12));
    [0.22, 0.40, 0.58, 0.76, 0.92].forEach((f) =>
      C.glyphCentered(cx + Math.cos(ma) * R * f, cy + Math.sin(ma) * R * f, el.hand_char, hc, a, el.glow));
    [0.20, 0.40, 0.60].forEach((f) =>
      C.glyphCentered(cx + Math.cos(ha) * R * 0.6 * f, cy + Math.sin(ha) * R * 0.6 * f, el.hand_char, hc, a, el.glow));
    C.glyphCentered(cx, cy, "O", hc, a, el.glow);
  }

  function drawTimer(C, el, t) {
    const w = windowOf(el, t); if (!w) return;
    const secs = Math.floor(el.from_s + w.local * el.rate);
    const pad = (n) => (n < 10 ? "0" + n : "" + n);
    const txt = el.prefix + pad(Math.floor(secs / 60)) + ":" + pad(secs % 60);
    const a = el.alpha * ease(el.ease_in)(w.in_p) * (el.anim_out === "fade" ? w.out_p : 1);
    const cx = el.cx != null ? el.cx : C.cols / 2, cy = el.cy != null ? el.cy : C.rows / 2;
    C.line(cx - lineCells(txt) / 2, cy, txt, el.color, a, el.glow);
  }

  const DRAW = {
    glyph: drawGlyph, loadbar: drawLoadbar, particles: drawParticles,
    border: drawBorder, symgrid: drawSymgrid, clock: drawClock, timer: drawTimer,
  };

  // ---- player ------------------------------------------------------------
  function play(spec, opts, mount) {
    opts = opts || {};
    const root = typeof mount === "string" ? document.querySelector(mount) : mount;
    const C = new CharCanvas(spec);

    const view = document.createElement("canvas");
    view.width = spec.width; view.height = spec.height;
    view.className = "charvid-canvas";
    const vx = view.getContext("2d");
    root.appendChild(view);

    const total = spec.scenes.reduce((s, sc) => s + sc.duration, 0);
    const bounds = []; let acc = 0;
    for (const sc of spec.scenes) { bounds.push([acc, acc + sc.duration, sc]); acc += sc.duration; }

    function sceneAt(t) {
      for (let i = 0; i < bounds.length; i++) {
        if (t < bounds[i][1] || i === bounds.length - 1) return [bounds[i][2], t - bounds[i][0]];
      }
      return [bounds[bounds.length - 1][2], 0];
    }
    function renderAt(t) {
      const [scene, local] = sceneAt(t);
      C.begin();
      for (const el of scene.elements) {
        const fn = DRAW[el.kind];
        if (fn) fn(C, el, local);
      }
      C.composite(vx, scene.bg);
    }

    const player = {
      t: 0, playing: opts.autoplay !== false, loop: opts.loop !== false,
      total: total, view: view,
      seek: function (t) { this.t = Math.max(0, Math.min(total, t)); renderAt(this.t); },
      pause: function () { this.playing = false; },
      resume: function () { this.playing = true; },
      toggle: function () { this.playing = !this.playing; if (this.t >= total) this.t = 0; },
      replay: function () { this.t = 0; this.playing = true; },
    };

    let last = performance.now();
    function frame(now) {
      const dt = Math.min(0.1, (now - last) / 1000); last = now;
      if (player.playing) {
        player.t += dt;
        if (player.t >= total) {
          if (player.loop) player.t = player.t % total;
          else { player.t = total; player.playing = false; }
        }
      }
      renderAt(player.t);
      if (player.onframe) player.onframe(player.t, total, player.playing);
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    return player;
  }

  global.Charvid = { play: play, CharCanvas: CharCanvas, isWide: isWide, rng: rng };
})(window);
