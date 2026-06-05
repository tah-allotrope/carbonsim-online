const Skyline = (function() {
  let canvas, ctx, animId, width, height;
  let buildings = [];
  let particles = [];
  let skyHue = 200;
  let targetSkyHue = 200;
  let smogDensity = 0.3;
  let targetSmogDensity = 0.3;
  let complianceRatio = 1.0;
  let time = 0;
  let reducedMotion = false;
  let lastFrame = 0;
  const FPS_INTERVAL = 1000 / 30;

  function init(canvasId, snapshot) {
    canvas = document.getElementById(canvasId);
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    resize();
    window.addEventListener('resize', resize);
    generateBuildings(snapshot);
    update(snapshot);
    if (!reducedMotion) {
      lastFrame = performance.now();
      animId = requestAnimationFrame(loop);
    } else {
      drawStatic();
    }
  }

  function resize() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    width = canvas.width = rect.width * (window.devicePixelRatio || 1);
    height = canvas.height = 220 * (window.devicePixelRatio || 1);
    canvas.style.width = rect.width + 'px';
    canvas.style.height = '220px';
    ctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);
    width = rect.width;
    height = 220;
  }

  function generateBuildings(snapshot) {
    buildings = [];
    const companies = (snapshot && (snapshot.leaderboard || snapshot.companies)) || [];
    const count = Math.max(companies.length, 6);
    const baseWidth = width / (count + 2);
    for (let i = 0; i < count; i++) {
      const company = companies[i];
      const w = baseWidth * (0.5 + Math.random() * 0.4);
      const h = 40 + Math.random() * 100;
      const x = (i + 1) * (width / (count + 1)) - w / 2;
      const emissions = company ? (company.projected_emissions || company.emissions || 50) : 30 + Math.random() * 70;
      const isPlayer = company && (company.company_id === (snapshot.player_company || {}).company_id);
      buildings.push({
        x, w, h,
        baseH: h,
        emissions: emissions,
        isPlayer: isPlayer,
        windows: Math.floor(3 + Math.random() * 5),
        windowRows: Math.floor(h / 18),
        smokeRate: emissions / 200,
        color: isPlayer ? 'rgba(0,245,255,0.15)' : `rgba(${30 + Math.random()*20},${30 + Math.random()*15},${40 + Math.random()*20},0.9)`,
        borderColor: isPlayer ? 'rgba(0,245,255,0.6)' : `rgba(${60 + Math.random()*30},${60 + Math.random()*20},${70 + Math.random()*20},0.4)`,
        glowPhase: Math.random() * Math.PI * 2,
      });
    }
    buildings.sort((a, b) => a.h - b.h);
  }

  function update(snapshot) {
    if (!snapshot) return;
    const player = snapshot.player_company || snapshot.companies?.[0] || {};
    const projected = player.projected_emissions || 0;
    const allowances = player.allowances || 0;
    const gap = player.compliance_gap || Math.max(0, projected - allowances);
    complianceRatio = projected > 0 ? Math.min(1, allowances / projected) : 1;

    targetSkyHue = complianceRatio >= 0.9 ? 200 : complianceRatio >= 0.7 ? 40 : 0;
    targetSmogDensity = Math.min(1, projected / 300);

    const activeAbatement = (player.active_abatement_ids || []).length;
    const totalMeasures = (player.abatement_menu || []).length;
    if (totalMeasures > 0) {
      const abatementRatio = activeAbatement / totalMeasures;
      targetSmogDensity *= (1 - abatementRatio * 0.6);
    }

    if (buildings.length > 0) {
      const playerBuilding = buildings.find(b => b.isPlayer);
      if (playerBuilding) {
        playerBuilding.smokeRate = targetSmogDensity * 0.5;
      }
    }
  }

  function loop(timestamp) {
    animId = requestAnimationFrame(loop);
    const delta = timestamp - lastFrame;
    if (delta < FPS_INTERVAL) return;
    lastFrame = timestamp - (delta % FPS_INTERVAL);
    time += delta * 0.001;
    draw();
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);
    drawSky();
    drawStars();
    drawBuildings();
    drawSmog();
    drawGround();
    spawnParticles();
    updateParticles();
    drawParticles();
  }

  function drawStatic() {
    drawSky();
    drawStars();
    drawBuildings();
    drawGround();
  }

  function drawSky() {
    skyHue += (targetSkyHue - skyHue) * 0.02;
    smogDensity += (targetSmogDensity - smogDensity) * 0.02;
    const saturation = 30 + (1 - complianceRatio) * 40;
    const lightness = 8 + complianceRatio * 6;
    const grad = ctx.createLinearGradient(0, 0, 0, height);
    grad.addColorStop(0, `hsl(${skyHue}, ${saturation}%, ${lightness * 0.6}%)`);
    grad.addColorStop(0.5, `hsl(${skyHue}, ${saturation * 0.7}%, ${lightness}%)`);
    grad.addColorStop(1, `hsl(${skyHue}, ${saturation * 0.5}%, ${lightness * 1.2}%)`);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);
  }

  function drawStars() {
    const starCount = 30;
    const seed = 42;
    for (let i = 0; i < starCount; i++) {
      const px = ((seed * (i + 1) * 7919) % 10000) / 10000 * width;
      const py = ((seed * (i + 1) * 6271) % 10000) / 10000 * (height * 0.5);
      const twinkle = 0.3 + 0.7 * Math.abs(Math.sin(time * 0.5 + i * 1.3));
      const size = 0.5 + ((seed * (i + 1) * 3571) % 10000) / 10000 * 1.2;
      ctx.beginPath();
      ctx.arc(px, py, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${twinkle * (1 - smogDensity * 0.7)})`;
      ctx.fill();
    }
  }

  function drawBuildings() {
    const groundY = height - 20;
    for (const b of buildings) {
      const bx = b.x;
      const by = groundY - b.h;
      ctx.fillStyle = b.color;
      ctx.fillRect(bx, by, b.w, b.h);
      ctx.strokeStyle = b.borderColor;
      ctx.lineWidth = 1;
      ctx.strokeRect(bx, by, b.w, b.h);

      if (b.isPlayer) {
        ctx.shadowColor = 'rgba(0,245,255,0.3)';
        ctx.shadowBlur = 12 + Math.sin(time * 2 + b.glowPhase) * 4;
        ctx.strokeStyle = 'rgba(0,245,255,0.5)';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(bx, by, b.w, b.h);
        ctx.shadowBlur = 0;
      }

      const winW = 3;
      const winH = 4;
      const winGapX = (b.w - 6) / Math.max(b.windows, 1);
      for (let row = 0; row < b.windowRows; row++) {
        for (let col = 0; col < b.windows; col++) {
          const wx = bx + 4 + col * winGapX;
          const wy = by + 8 + row * 18;
          if (wy + winH > groundY - 4) continue;
          const lit = Math.sin(time * 0.3 + row * 2.1 + col * 3.7 + b.glowPhase) > 0.1;
          ctx.fillStyle = lit
            ? (b.isPlayer ? 'rgba(0,245,255,0.6)' : 'rgba(255,220,120,0.5)')
            : 'rgba(20,20,30,0.6)';
          ctx.fillRect(wx, wy, winW, winH);
        }
      }
    }
  }

  function drawSmog() {
    if (smogDensity < 0.05) return;
    const layers = 3;
    for (let l = 0; l < layers; l++) {
      const y = height * 0.3 + l * 25;
      const alpha = smogDensity * (0.08 + l * 0.04);
      const drift = Math.sin(time * 0.2 + l * 1.5) * 20;
      ctx.fillStyle = `rgba(180,160,140,${alpha})`;
      ctx.beginPath();
      for (let x = -50; x <= width + 50; x += 30) {
        const waveY = y + Math.sin((x + drift + time * 15) * 0.02) * 8 + l * 5;
        if (x === -50) ctx.moveTo(x, waveY);
        else ctx.lineTo(x, waveY);
      }
      ctx.lineTo(width + 50, height);
      ctx.lineTo(-50, height);
      ctx.closePath();
      ctx.fill();
    }
  }

  function drawGround() {
    const groundY = height - 20;
    const grad = ctx.createLinearGradient(0, groundY, 0, height);
    grad.addColorStop(0, 'rgba(15,15,20,0.95)');
    grad.addColorStop(1, 'rgba(10,10,15,1)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, groundY, width, 20);
    ctx.strokeStyle = complianceRatio >= 0.9 ? 'rgba(57,255,20,0.3)' : complianceRatio >= 0.7 ? 'rgba(255,170,0,0.3)' : 'rgba(255,68,68,0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, groundY);
    ctx.lineTo(width, groundY);
    ctx.stroke();
  }

  function spawnParticles() {
    for (const b of buildings) {
      if (Math.random() > b.smokeRate * 0.3) continue;
      const groundY = height - 20;
      particles.push({
        x: b.x + b.w * 0.3 + Math.random() * b.w * 0.4,
        y: groundY - b.h - 2,
        vx: (Math.random() - 0.5) * 0.3,
        vy: -0.3 - Math.random() * 0.5,
        life: 1,
        decay: 0.005 + Math.random() * 0.01,
        size: 1.5 + Math.random() * 2.5,
        color: b.isPlayer ? [0, 245, 255] : [180, 160, 140],
      });
    }
    if (particles.length > 150) particles.splice(0, particles.length - 150);
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
    for (const p of particles) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color[0]},${p.color[1]},${p.color[2]},${p.life * 0.4})`;
      ctx.fill();
    }
  }

  function triggerAbatementEffect() {
    targetSmogDensity = Math.max(0, targetSmogDensity - 0.15);
    for (let i = 0; i < 8; i++) {
      const b = buildings.find(b => b.isPlayer) || buildings[0];
      if (!b) continue;
      const groundY = height - 20;
      particles.push({
        x: b.x + b.w / 2,
        y: groundY - b.h,
        vx: (Math.random() - 0.5) * 2,
        vy: -1 - Math.random() * 2,
        life: 1,
        decay: 0.02,
        size: 3,
        color: [57, 255, 20],
      });
    }
  }

  function triggerOffsetEffect() {
    for (let i = 0; i < 12; i++) {
      particles.push({
        x: Math.random() * width,
        y: height - 30 - Math.random() * 40,
        vx: (Math.random() - 0.5) * 1.5,
        vy: -0.5 - Math.random(),
        life: 1,
        decay: 0.015,
        size: 2 + Math.random() * 2,
        color: [0, 245, 255],
      });
    }
  }

  function triggerYearTransition() {
    targetSmogDensity = targetSmogDensity;
    skyHue = 280;
    setTimeout(() => { skyHue = targetSkyHue; }, 500);
  }

  function destroy() {
    if (animId) cancelAnimationFrame(animId);
    window.removeEventListener('resize', resize);
  }

  return { init, update, destroy, triggerAbatementEffect, triggerOffsetEffect, triggerYearTransition };
})();
