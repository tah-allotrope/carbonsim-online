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
  let time = 0;
  let particles = [];
  let flashOpacity = 0;
  let flashColor = null;

  const TILE_W = 64;
  const TILE_H = 32;
  const GRID_SIZE = 6;
  const MAX_PLOTS = 16;

  let images = {};
  let manifestLoaded = false;
  let plots = [];
  let snapshotCache = null;
  let localCompanyId = null;

  function loadImages() {
    if (typeof AssetLoader === 'undefined') {
      return Promise.reject(new Error('AssetLoader not available'));
    }
    return AssetLoader.load().then(function () {
      images.ground = AssetLoader.getImage('ground');
      images.factory_dirty = AssetLoader.getImage('factory_dirty');
      images.factory_clean = AssetLoader.getImage('factory_clean');
      images.smog = AssetLoader.getImage('smog');
      images.player_marker = AssetLoader.getImage('player_marker');
      images.district = AssetLoader.getImage('district');
      manifestLoaded = true;
    });
  }

  function init(canvasId, snapshot) {
    canvas = document.getElementById(canvasId);
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    resize();
    window.addEventListener('resize', resize);

    loadImages().then(function () {
      update(snapshot);
      if (!reducedMotion) {
        lastFrame = performance.now();
        animId = requestAnimationFrame(loop);
      } else {
        drawStatic();
      }
    });
  }

  function resize() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    dpr = window.devicePixelRatio || 1;
    width = canvas.width = rect.width * dpr;
    height = canvas.height = 260 * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = '260px';
    ctx.scale(dpr, dpr);
    width = rect.width;
    height = 260;
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
    // Sort by row+col for painter-friendly order (back to front).
    positions.sort(function (a, b) {
      return (a.col + a.row) - (b.col + b.row);
    });

    // Shuffle positions deterministically by company hash so different rooms
    // get different layouts, but the same room always gets the same layout.
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
      plots.push({
        col: pos.col,
        row: pos.row,
        company: company,
        isPlayer: company.company_id === localCompanyId,
        isDistrict: false,
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
      plots.push({
        col: pos.col,
        row: pos.row,
        company: { projected_emissions: 0, compliance_gap: 0 },
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
      return;
    }

    const abated = (company.active_abatement_ids || []).length > 0;
    const sprite = abated ? images.factory_clean : images.factory_dirty;
    ctx.drawImage(sprite, pos.x - 32, pos.y - 36);

    // Smog overlay scales with projected emissions.
    const emissions = company.projected_emissions || 0;
    if (emissions > 0 && images.smog) {
      const alpha = Math.min(0.7, emissions / 300);
      ctx.globalAlpha = alpha;
      ctx.drawImage(images.smog, pos.x - 32, pos.y - 36);
      ctx.globalAlpha = 1;
    }

    // Compliance shortfall tint.
    const gap = company.compliance_gap || 0;
    if (gap > 0) {
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

  function spawnParticles() {
    if (reducedMotion || particles.length > 150) return;
    plots.forEach(function (plot) {
      if (plot.isDistrict) return;
      const company = plot.company || {};
      const emissions = company.projected_emissions || 0;
      if (emissions <= 0) return;
      const rate = Math.min(0.3, emissions / 600);
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
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(' + p.color + ',' + (p.life * 0.4) + ')';
      ctx.fill();
    });
  }

  function drawFlash() {
    if (flashOpacity <= 0) return;
    ctx.fillStyle = flashColor + flashOpacity + ')';
    ctx.fillRect(0, 0, width, height);
    flashOpacity -= 0.02;
    if (flashOpacity < 0) flashOpacity = 0;
  }

  function draw() {
    if (!manifestLoaded) return;
    ctx.clearRect(0, 0, width, height);

    // Layer 1: ground tiles, back to front.
    const sorted = plots.slice().sort(function (a, b) {
      return (a.col + a.row) - (b.col + b.row);
    });
    sorted.forEach(drawPlotGround);

    // Layer 2: structures (buildings, smog, tint).
    sorted.forEach(drawPlotStructure);

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
    const delta = timestamp - lastFrame;
    if (delta < FPS_INTERVAL) return;
    lastFrame = timestamp - (delta % FPS_INTERVAL);
    time += delta * 0.001;
    draw();
  }

  function update(snapshot) {
    if (!snapshot) return;
    snapshotCache = snapshot;
    buildPlots(snapshot);
  }

  function burstParticles(plotFilter, color, count, speed) {
    const targets = plots.filter(plotFilter);
    if (targets.length === 0) return;
    targets.forEach(function (plot) {
      const pos = tileToScreen(plot.col, plot.row);
      for (let i = 0; i < count; i++) {
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
