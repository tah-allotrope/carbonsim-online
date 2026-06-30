/**
 * CarbonSim Online — Pixel-Style Visual Effects Engine
 * Blocky, stepped micro-interactions for the retro tycoon aesthetic.
 */

const Effects = {
  /**
   * Animates a numeric text content from one value to another smoothly
   * @param {HTMLElement} element
   * @param {number} from
   * @param {number} to
   * @param {number} duration ms
   * @param {boolean} isCurrency prepend $
   */
  animateCounter(element, from, to, duration = 800, isCurrency = false) {
    if (!element) return;

    if (element._animId) {
      cancelAnimationFrame(element._animId);
    }

    const start = performance.now();

    function fmt(n) {
      // 2026-06-30 PHASE-02: delegate to the shared formatters. Currency
      // animations use the abbreviated form so the count-up fits in the
      // stat tile width; non-currency uses the abbreviated tonnes form.
      if (n == null) return '0';
      if (isCurrency) {
        const sign = n < 0 ? '-' : '';
        const abs = Math.abs(n);
        if (abs >= 1e12) return sign + (abs / 1e12).toFixed(1) + 'T đ';
        if (abs >= 1e9) return sign + (abs / 1e9).toFixed(1) + 'B đ';
        if (abs >= 1e6) return sign + (abs / 1e6).toFixed(1) + 'M đ';
        if (abs >= 1e3) return sign + (abs / 1e3).toFixed(1) + 'K đ';
        return sign + abs.toFixed(0) + ' đ';
      }
      const abs = Math.abs(n);
      const sign = n < 0 ? '-' : '';
      if (abs >= 1e6) return sign + (abs / 1e6).toFixed(1) + 'M';
      if (abs >= 1e3) return sign + (abs / 1e3).toFixed(1) + 'K';
      return sign + abs.toFixed(0);
    }

    element.classList.remove('stat-value-bump');
    void element.offsetWidth;
    element.classList.add('stat-value-bump');

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = from + (to - from) * ease;

      element.textContent = fmt(current);

      if (progress < 1) {
        element._animId = requestAnimationFrame(update);
      } else {
        element.textContent = fmt(to);
        element._animId = null;
        setTimeout(() => element.classList.remove('stat-value-bump'), 100);
      }
    }

    element._animId = requestAnimationFrame(update);
  },

  /**
   * Pixel-palette map for effect bursts.
   */
  _pixelPalette: {
    accent: '#3b6f76',
    green: '#5a8f4e',
    red: '#b54a3f',
    orange: '#d4883a',
    ink: '#1f1912',
    paper: '#fffdf9',
  },

  /**
   * Resolves a CSS variable or named color to a hex for canvas/DOM particles.
   */
  _resolveColor(color) {
    if (!color) return this._pixelPalette.accent;
    if (color.startsWith('var(')) {
      const name = color.replace(/var\(--([^)]+)\)/, '$1');
      return this._pixelPalette[name] || this._pixelPalette.accent;
    }
    return color;
  },

  /**
   * Spawns a burst of blocky pixel particles from a coordinate.
   * @param {number} x viewport coordinate
   * @param {number} y viewport coordinate
   * @param {string} color hex or var(--token) name
   * @param {number} count number of particles
   */
  particleBurst(x, y, color = 'var(--accent)', count = 14) {
    const container = document.body;
    const resolved = this._resolveColor(color);

    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'visual-particle';
      p.style.backgroundColor = resolved;
      p.style.left = `${Math.floor(x)}px`;
      p.style.top = `${Math.floor(y)}px`;
      container.appendChild(p);

      const size = 4 + Math.floor(Math.random() * 4);
      p.style.width = `${size}px`;
      p.style.height = `${size}px`;

      const angle = Math.random() * Math.PI * 2;
      const velocity = 2 + Math.random() * 5;
      let dx = Math.cos(angle) * velocity;
      let dy = Math.sin(angle) * velocity - (Math.random() * 2);

      let posX = Math.floor(x);
      let posY = Math.floor(y);
      let life = 1;
      const decay = 0.02 + Math.random() * 0.03;
      const gravity = 0.18;

      const startTime = performance.now();
      const maxLife = 350 + Math.random() * 300;

      function step(now) {
        const elapsed = now - startTime;
        const progress = elapsed / maxLife;

        if (progress >= 1) {
          p.remove();
          return;
        }

        // Stepped pixel motion
        dx *= 0.96;
        dy += gravity;
        posX += dx;
        posY += dy;

        const drawX = Math.floor(posX / size) * size;
        const drawY = Math.floor(posY / size) * size;
        life = 1 - progress;

        p.style.left = `${drawX}px`;
        p.style.top = `${drawY}px`;
        p.style.opacity = life.toFixed(2);
        p.style.transform = `translate(-50%, -50%)`;

        requestAnimationFrame(step);
      }

      requestAnimationFrame(step);
    }
  },

  /**
   * Temporarily pulses border glow of an element
   * @param {HTMLElement} element
   * @param {'cyan'|'green'|'red'} color
   */
  glowPulse(element, color = 'cyan') {
    if (!element) return;

    const className = `pulse-glow-${color}`;
    element.classList.remove('pulse-glow-cyan', 'pulse-glow-green', 'pulse-glow-red');
    void element.offsetWidth;
    element.classList.add(className);

    element.addEventListener('animationend', function handler() {
      element.classList.remove(className);
      element.removeEventListener('animationend', handler);
    }, { once: true });
  },

  /**
   * Flash the viewport with a retro colored glow
   * @param {string} color hex/rgb color
   * @param {number} duration ms
   */
  screenFlash(color = 'rgba(181,74,63,0.25)', duration = 400) {
    const flash = document.createElement('div');
    flash.className = 'screen-flash-overlay';
    flash.style.backgroundColor = color;
    document.body.appendChild(flash);

    const start = performance.now();

    function step(now) {
      const elapsed = now - start;
      const progress = elapsed / duration;

      if (progress >= 1) {
        flash.remove();
        return;
      }

      let opacity = 0;
      if (progress < 0.25) {
        opacity = progress / 0.25;
      } else {
        opacity = 1 - ((progress - 0.25) / 0.75);
      }

      flash.style.opacity = opacity;
      requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }
};

window.Effects = Effects;
