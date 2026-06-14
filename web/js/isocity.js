/**
 * Isocity — retro isometric city renderer for CarbonSim Online.
 *
 * Reuses the legacy renderer lifecycle (RAF loop, throttle, DPR resize,
 * reduced-motion fallback, public trigger API) and renders a tile-based
 * isometric city that reflects live engine state.
 */
const Isocity = (function () {
  'use strict';

  let canvas, ctx, animId, width, height, dpr;
  let reducedMotion = false;
  let lastFrame = 0;
  const FPS_INTERVAL = 1000 / 30;
  let particles = [];
  let motionQuery = null;
  let motionHandler = null;
  let resizeObserver = null;
  let citizens = [];
  let citizenMeta = null;
  let flashOpacity = 0;
  let flashColor = null;

  const TILE_W = 64;
  const TILE_H = 32;
  const GRID_SIZE = 6;
  const MAX_PLOTS = 16;
  const MAX_DPR = 2; // cap over-rendering on high-DPR mobile
  const BASE_MAX_PARTICLES = 40;
  const PARTICLES_PER_PLOT = 8;
  const ABSOLUTE_MAX_PARTICLES = 150;

  let images = {};
  let manifestLoaded = false;
  let plots = [];
  let snapshotCache = null;
  let localCompanyId = null;
  let resizeTimer = null;

  function loadImages() {
    if (typeof AssetLoader === 'undefined') {
      return Promise.reject(new Error('AssetLoader not available'));
    }
    return AssetLoader.load().then(function () {
      images.ground = AssetLoader.getImage('ground');
      ['thermal', 'steel', 'cement', 'generic'].forEach(function (k) {
        images['bldg_' + k + '_dirty'] = AssetLoader.getImage('bldg_' + k + '_dirty');
        images['bldg_' + k + '_clean'] = AssetLoader.getImage('bldg_' + k + '_clean');
      });
      images.smog = AssetLoader.getImage('smog');
      images.player_marker = AssetLoader.getImage('player_marker');
      images.district = AssetLoader.getImage('district');
      images.decor_tree = AssetLoader.getImage('decor_tree');
      images.citizens = AssetLoader.getImage('citizens');
      citizenMeta = AssetLoader.getAsset('citizens');
      manifestLoaded = true;
    });
  }

  function init(canvasId, snapshot) {
    canvas = document.getElementById(canvasId);
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    reducedMotion = motionQuery.matches;

    // Size synchronously so the very first paint has real dimensions; only the
    // window resize event is debounced (see resize()).
    doResize();
    window.addEventListener('resize', resize);

    // Re-measure whenever the container actually gets/changes width. This is the
    // robust fix for a blank city: init can run before layout settles (loading
    // overlay, fonts, responsive changes), and without this the canvas would
    // stay stuck at a wrong/zero size forever.
    if (typeof ResizeObserver !== 'undefined' && canvas.parentElement) {
      resizeObserver = new ResizeObserver(function () {
        doResize();
        draw();
      });
      resizeObserver.observe(canvas.parentElement);
    }

    motionHandler = function (e) {
      reducedMotion = e.matches;
      if (reducedMotion) {
        if (animId) cancelAnimationFrame(animId);
        animId = null;
        drawStatic();
      } else {
        lastFrame = performance.now();
        animId = requestAnimationFrame(loop);
      }
    };
    if (motionQuery.addEventListener) {
      motionQuery.addEventListener('change', motionHandler);
    } else if (motionQuery.addListener) {
      motionQuery.addListener(motionHandler);
    }

    loadImages().then(function () {
      update(snapshot);
      // Always paint an initial frame. The RAF loop early-returns while the tab
      // is hidden, so don't rely on it for the first paint.
      drawStatic();
      if (!reducedMotion) {
        lastFrame = performance.now();
        animId = requestAnimationFrame(loop);
      }
    });
  }

  function doResize() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    if (rect.width < 1) return;  // not laid out yet; the ResizeObserver re-fires when it is
    dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    width = canvas.width = Math.floor(rect.width * dpr);
    height = canvas.height = Math.floor(260 * dpr);
    canvas.style.width = rect.width + 'px';
    canvas.style.height = '260px';
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    width = rect.width;
    height = 260;
  }

  function resize() {
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(doResize, 100);
  }

  function tileToScreen(col, row) {
    const centerCol = (GRID_SIZE - 1) / 2;
    const centerRow = (GRID_SIZE - 1) / 2;
    const originX = width / 2;
    const originY = height / 2 + 40;
    const x = originX + (col - row) * (TILE_W / 2);
    const y = originY + (col + row) * (TILE_H / 2);
    return { x, y };
  }

  /**
   * Deterministic hash of a company_id string into a 32-bit integer.
   * Stably assigns companies to plots across frames and reconnects.
   */
  function hashCompanyId(companyId) {
    const str = String(companyId || '');
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
    }
    return h >>> 0;
  }

  const SECTOR_KEYS = ['thermal', 'steel', 'cement'];
  function sectorKey(label) {
    const s = String(label || '').toLowerCase();
    for (let i = 0; i < SECTOR_KEYS.length; i++) {
      if (s.indexOf(SECTOR_KEYS[i]) >= 0) return SECTOR_KEYS[i];
    }
    return 'generic';
  }

  /**
   * Build a deterministic list of plot positions from the snapshot.
   * Up to MAX_PLOTS individual company plots; remaining companies are
   * aggregated into one or more district tiles.
   */
  function buildPlots(snapshot) {
    plots = [];
    if (!snapshot) return;

    const companies = snapshot.leaderboard || snapshot.companies || [];
    localCompanyId = (snapshot.player_company || {}).company_id || null;

    // Candidate grid positions in the central 6x6 area, ordered back-to-front.
    const positions = [];
    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        positions.push({ col, row });
      }
    }
    // Assign plots deterministically by company-id hash so the same room
    // always produces the same layout (draw() handles painter ordering).
    const used = new Set();
    const individual = [];
    const remainder = [];

    companies.forEach(function (company, index) {
      if (index < MAX_PLOTS) {
        individual.push(company);
      } else {
        remainder.push(company);
      }
    });

    // Only player_company carries emissions + abatement state; the leaderboard
    // entries are slim (sector_label + compliance only). Enrich the player plot.
    const pc = snapshot.player_company || {};
    const playerAbated = (pc.abatement_menu || []).some(function (m) { return m.active; });

    individual.forEach(function (company) {
      let hash = hashCompanyId(company.company_id);
      let pos;
      let attempts = 0;
      do {
        pos = positions[hash % positions.length];
        hash = hashCompanyId(String(hash));
        attempts++;
      } while (used.has(pos.col + ',' + pos.row) && attempts < positions.length);

      used.add(pos.col + ',' + pos.row);
      const isPlayer = company.company_id === localCompanyId;
      const co = isPlayer
        ? Object.assign({}, company, {
            projected_emissions: pc.projected_emissions != null
              ? pc.projected_emissions : company.projected_emissions,
          })
        : company;
      plots.push({
        col: pos.col,
        row: pos.row,
        company: co,
        isPlayer: isPlayer,
        isDistrict: false,
        sectorKey: sectorKey(company.sector_label),
        abated: isPlayer ? playerAbated : false,
      });
    });

    if (remainder.length > 0) {
      // Place one district tile for the aggregated remainder.
      let hash = 0x9e3779b9;
      let pos;
      let attempts = 0;
      do {
        pos = positions[hash % positions.length];
        hash = hashCompanyId(String(hash));
        attempts++;
      } while (used.has(pos.col + ',' + pos.row) && attempts < positions.length);
      used.add(pos.col + ',' + pos.row);
      const districtEmissions = remainder.reduce(function (sum, c) {
        return sum + (c.projected_emissions || 0);
      }, 0);
      plots.push({
        col: pos.col,
        row: pos.row,
        company: { projected_emissions: districtEmissions, compliance_gap: 0 },
        isPlayer: false,
        isDistrict: true,
        districtCount: remainder.length,
      });
    }
  }

  function drawPlotGround(plot) {
    if (!images.ground) return;
    const pos = tileToScreen(plot.col, plot.row);
    ctx.drawImage(images.ground, pos.x - 32, pos.y - 36);
  }

  function drawPlotStructure(plot) {
    if (!manifestLoaded) return;
    const pos = tileToScreen(plot.col, plot.row);
    const company = plot.company || {};

    if (plot.isDistrict) {
      ctx.drawImage(images.district, pos.x - 32, pos.y - 36);
    } else {
      const key = plot.sectorKey || 'generic';
      const variant = plot.abated ? 'clean' : 'dirty';
      const sprite = images['bldg_' + key + '_' + variant]
        || images['bldg_generic_' + variant]
        || images['bldg_generic_dirty'];
      if (sprite) ctx.drawImage(sprite, pos.x - 32, pos.y - 36);
    }

    // Smog overlay scales with projected emissions — districts aggregate the
    // emissions of every company they stand in for, so they smog too.
    const emissions = company.projected_emissions || 0;
    if (emissions > 0 && images.smog) {
      const alpha = Math.min(0.7, emissions / 300);
      ctx.globalAlpha = alpha;
      ctx.drawImage(images.smog, pos.x - 32, pos.y - 36);
      ctx.globalAlpha = 1;
    }

    // Compliance shortfall tint (individual plots only).
    const gap = company.compliance_gap || 0;
    if (!plot.isDistrict && gap > 0) {
      ctx.fillStyle = 'rgba(181, 74, 63, 0.25)';
      ctx.beginPath();
      ctx.ellipse(pos.x, pos.y, 28, 14, 0, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawPlotMarker(plot) {
    if (!manifestLoaded || !plot.isPlayer || !images.player_marker) return;
    const pos = tileToScreen(plot.col, plot.row);
    ctx.drawImage(images.player_marker, pos.x - 32, pos.y - 64);
  }

  function maxParticles() {
    return Math.min(
      ABSOLUTE_MAX_PARTICLES,
      BASE_MAX_PARTICLES + plots.length * PARTICLES_PER_PLOT
    );
  }

  function spawnParticles() {
    const cap = maxParticles();
    if (reducedMotion || particles.length >= cap) return;
    plots.forEach(function (plot) {
      if (particles.length >= cap) return;
      const company = plot.company || {};
      const emissions = company.projected_emissions || 0;
      if (emissions <= 0) return;
      const rate = Math.min(0.25, emissions / 800);
      if (Math.random() > rate) return;
      const pos = tileToScreen(plot.col, plot.row);
      particles.push({
        x: pos.x + (Math.random() - 0.5) * 24,
        y: pos.y - 30 - Math.random() * 20,
        vx: (Math.random() - 0.5) * 0.3,
        vy: -0.2 - Math.random() * 0.4,
        life: 1,
        decay: 0.005 + Math.random() * 0.01,
        size: 1.5 + Math.random() * 2,
        color: '120,100,90',
      });
    });
  }

  function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx += (Math.random() - 0.5) * 0.05;
      p.life -= p.decay;
      if (p.life <= 0) particles.splice(i, 1);
    }
  }

  function drawParticles() {
    particles.forEach(function (p) {
      const size = Math.max(1, Math.floor(p.size * p.life));
      const drawX = Math.floor(p.x / size) * size;
      const drawY = Math.floor(p.y / size) * size;
      ctx.fillStyle = 'rgba(' + p.color + ',' + (p.life * 0.55) + ')';
      ctx.fillRect(drawX, drawY, size, size);
    });
  }

  function drawFlash() {
    if (flashOpacity <= 0) return;
    ctx.fillStyle = flashColor + flashOpacity + ')';
    ctx.fillRect(0, 0, width, height);
    flashOpacity -= 0.02;
    if (flashOpacity < 0) flashOpacity = 0;
  }

  /* --- Sprite-sheet frame animation core (Sprint 3) --- */
  function drawSprite(img, fw, fh, col, row, dx, dy, flip) {
    if (!img) return;
    const sx = col * fw, sy = row * fh;
    if (flip) {
      ctx.save();
      ctx.translate(Math.round(dx + fw), Math.round(dy));
      ctx.scale(-1, 1);
      ctx.drawImage(img, sx, sy, fw, fh, 0, 0, fw, fh);
      ctx.restore();
    } else {
      ctx.drawImage(img, sx, sy, fw, fh, Math.round(dx), Math.round(dy), fw, fh);
    }
  }

  // Walk-cycle frame index derived from wall-clock so it is stable under the
  // 30fps throttle (and idle when reduced motion freezes the loop).
  function walkFrame() {
    const n = (citizenMeta && citizenMeta.frames) || 1;
    if (reducedMotion) return 0;
    return Math.floor(performance.now() / 150) % n;
  }

  /* --- Citizens (Sprint 3) --- */
  function cityBounds() {
    if (!plots.length) {
      return { x0: 20, x1: width - 20, y0: height * 0.45, y1: height - 12 };
    }
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    plots.forEach(function (p) {
      const s = tileToScreen(p.col, p.row);
      if (s.x < x0) x0 = s.x;
      if (s.x > x1) x1 = s.x;
      if (s.y < y0) y0 = s.y;
      if (s.y > y1) y1 = s.y;
    });
    return { x0: x0 - 10, x1: x1 + 10, y0: y0 - 4, y1: y1 + 16 };
  }

  function spawnCitizens(count) {
    citizens = [];
    if (!images.citizens || !citizenMeta) return;
    const b = cityBounds();
    const variants = citizenMeta.variants || 1;
    for (let i = 0; i < count; i++) {
      citizens.push({
        x: b.x0 + Math.random() * (b.x1 - b.x0),
        y: b.y0 + Math.random() * (b.y1 - b.y0),
        tx: b.x0 + Math.random() * (b.x1 - b.x0),
        ty: b.y0 + Math.random() * (b.y1 - b.y0),
        speed: 0.25 + Math.random() * 0.35,
        variant: i % variants,
        phase: Math.floor(Math.random() * 4),
        flip: false,
      });
    }
  }

  function updateCitizens() {
    if (reducedMotion || !citizens.length) return;
    const b = cityBounds();
    citizens.forEach(function (c) {
      const dx = c.tx - c.x, dy = c.ty - c.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 2) {
        c.tx = b.x0 + Math.random() * (b.x1 - b.x0);
        c.ty = b.y0 + Math.random() * (b.y1 - b.y0);
        return;
      }
      c.x += (dx / dist) * c.speed;
      c.y += (dy / dist) * c.speed;
      c.flip = dx < 0;
    });
  }

  function drawCitizen(c) {
    if (!images.citizens || !citizenMeta) return;
    const fw = citizenMeta.frameW || 16, fh = citizenMeta.frameH || 16;
    const n = citizenMeta.frames || 1;
    const frame = (walkFrame() + c.phase) % n;
    drawSprite(images.citizens, fw, fh, frame, c.variant, c.x - fw / 2, c.y - fh + 2, c.flip);
  }

  function draw() {
    if (!manifestLoaded) return;
    ctx.clearRect(0, 0, width, height);

    // Layer 1: ground tiles, back to front.
    const sorted = plots.slice().sort(function (a, b) {
      return (a.col + a.row) - (b.col + b.row);
    });
    sorted.forEach(drawPlotGround);

    // Layer 2: structures + citizens, depth-sorted by screen-y so citizens
    // pass correctly in front of / behind buildings.
    const ents = [];
    sorted.forEach(function (p) { ents.push({ y: tileToScreen(p.col, p.row).y, b: p }); });
    citizens.forEach(function (c) { ents.push({ y: c.y, c: c }); });
    ents.sort(function (a, z) { return a.y - z.y; });
    ents.forEach(function (e) { if (e.b) drawPlotStructure(e.b); else drawCitizen(e.c); });

    // Layer 3: particles (smoke + effect bursts).
    spawnParticles();
    updateParticles();
    drawParticles();

    // Layer 4: player markers above everything.
    sorted.forEach(drawPlotMarker);

    // Layer 5: transition flash overlay.
    drawFlash();
  }

  function drawStatic() {
    draw();
  }

  function loop(timestamp) {
    animId = requestAnimationFrame(loop);
    if (document.hidden) {
      // Background tabs naturally pause RAF, but guard anyway.
      lastFrame = timestamp;
      return;
    }
    const delta = timestamp - lastFrame;
    if (delta < FPS_INTERVAL) return;
    lastFrame = timestamp - (delta % FPS_INTERVAL);
    updateCitizens();
    draw();
  }

  function update(snapshot) {
    if (!snapshot) return;
    snapshotCache = snapshot;
    buildPlots(snapshot);
    // Stable across refreshes: only (re)spawn when the desired count changes.
    const desired = Math.min(plots.length * 2, 14);
    if (citizens.length !== desired) spawnCitizens(desired);
    if (reducedMotion) drawStatic();
  }

  function burstParticles(plotFilter, color, count, speed) {
    const targets = plots.filter(plotFilter);
    if (targets.length === 0) return;
    const cap = maxParticles();
    targets.forEach(function (plot) {
      const pos = tileToScreen(plot.col, plot.row);
      for (let i = 0; i < count; i++) {
        if (particles.length >= cap) return;
        particles.push({
          x: pos.x,
          y: pos.y - 30,
          vx: (Math.random() - 0.5) * speed,
          vy: -Math.random() * speed - 1,
          life: 1,
          decay: 0.02,
          size: 2 + Math.random() * 2,
          color: color,
        });
      }
    });
  }

  function triggerAbatementEffect() {
    burstParticles(function (p) { return p.isPlayer; }, '90,143,78', 16, 3);
  }

  function triggerOffsetEffect() {
    burstParticles(function (p) { return p.isPlayer; }, '59,111,118', 14, 2.5);
  }

  function triggerYearTransition() {
    flashColor = 'rgba(239,228,208,';
    flashOpacity = 0.6;
  }

  function destroy() {
    if (animId) cancelAnimationFrame(animId);
    window.removeEventListener('resize', resize);
    if (resizeTimer) clearTimeout(resizeTimer);
    if (resizeObserver) {
      resizeObserver.disconnect();
      resizeObserver = null;
    }
    if (motionQuery && motionHandler) {
      if (motionQuery.removeEventListener) {
        motionQuery.removeEventListener('change', motionHandler);
      } else if (motionQuery.removeListener) {
        motionQuery.removeListener(motionHandler);
      }
    }
  }

  return {
    init,
    update,
    destroy,
    triggerAbatementEffect,
    triggerOffsetEffect,
    triggerYearTransition,
  };
})();

// Expose globally — a top-level `const` is a lexical binding, NOT a window
// property, so screens referencing `window.Isocity` would otherwise get
// undefined and never initialize the renderer.
window.Isocity = Isocity;
