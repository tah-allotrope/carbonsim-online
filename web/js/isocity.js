/**
 * Isocity — retro isometric city renderer for CarbonSim Online.
 *
 * Reuses the skyline.js lifecycle (RAF loop, throttle, DPR resize,
 * reduced-motion fallback, public trigger API) and renders a tile-based
 * isometric city that reflects live engine state.
 */
const Isocity = (function () {
  'use strict';

  let canvas, ctx, animId, width, height, dpr;
  let reducedMotion = false;
  let lastFrame = 0;
  const FPS_INTERVAL = 1000 / 30;

  const TILE_W = 64;
  const TILE_H = 32;
  const GRID_SIZE = 6;

  let images = {};
  let manifestLoaded = false;

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
      manifestLoaded = true;
    });
  }

  function init(canvasId) {
    canvas = document.getElementById(canvasId);
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    resize();
    window.addEventListener('resize', resize);

    loadImages().then(function () {
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

  function drawGroundGrid() {
    if (!images.ground) return;
    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        const pos = tileToScreen(col, row);
        ctx.drawImage(images.ground, pos.x - 32, pos.y - 36);
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    drawGroundGrid();
  }

  function drawStatic() {
    drawGroundGrid();
  }

  function loop(timestamp) {
    animId = requestAnimationFrame(loop);
    const delta = timestamp - lastFrame;
    if (delta < FPS_INTERVAL) return;
    lastFrame = timestamp - (delta % FPS_INTERVAL);
    draw();
  }

  function update(snapshot) {
    // Placeholder for PHASE-02 state mapping.
  }

  function triggerAbatementEffect() {}
  function triggerOffsetEffect() {}
  function triggerYearTransition() {}

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
