/**
 * Climate Mayor — Visual Juice Engine
 * Reusable visual effect utilities for micro-interactions
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
    
    // Stop any existing animation on this element
    if (element._animId) {
      cancelAnimationFrame(element._animId);
    }
    
    const start = performance.now();
    
    // Formatting helper
    function fmt(n) {
      if (n == null) return '0';
      const absN = Math.abs(n);
      
      // Determine prefix
      const prefix = isCurrency ? (n < 0 ? '-$' : '$') : '';
      const displayVal = Math.abs(n);
      
      let formatted = '';
      if (displayVal >= 1e6) {
        formatted = (displayVal / 1e6).toFixed(1) + 'M';
      } else if (displayVal >= 1e3) {
        formatted = (displayVal / 1e3).toFixed(1) + 'K';
      } else {
        formatted = displayVal.toFixed(0); // integers look cleaner for raw values
      }
      
      return prefix + formatted;
    }
    
    // Trigger subtle bump animation on start
    element.classList.remove('stat-value-bump');
    void element.offsetWidth; // trigger reflow
    element.classList.add('stat-value-bump');
    
    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      
      // Cubic ease-out
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
   * Spawns a bursts of glowing particles from a coordinate
   * @param {number} x viewport coordinate
   * @param {number} y viewport coordinate
   * @param {string} color hex/hsl/css color string
   * @param {number} count number of particles
   */
  particleBurst(x, y, color = 'var(--accent)', count = 12) {
    const container = document.body;
    
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'visual-particle';
      p.style.backgroundColor = color;
      p.style.boxShadow = `0 0 8px ${color}`;
      p.style.left = `${x}px`;
      p.style.top = `${y}px`;
      container.appendChild(p);
      
      // Physics factors
      const angle = Math.random() * Math.PI * 2;
      const velocity = 2 + Math.random() * 6;
      const dx = Math.cos(angle) * velocity;
      const dy = Math.sin(angle) * velocity - (Math.random() * 2); // slight upwards gravity bias
      
      let posX = x;
      let posY = y;
      let opacity = 1;
      let scale = 1;
      
      const startTime = performance.now();
      const life = 400 + Math.random() * 400; // ms duration
      
      function step(now) {
        const elapsed = now - startTime;
        const progress = elapsed / life;
        
        if (progress >= 1) {
          p.remove();
          return;
        }
        
        posX += dx;
        posY += dy + (progress * 1.5); // gravity pulling down slowly
        opacity = 1 - progress;
        scale = 1 - (progress * 0.5);
        
        p.style.left = `${posX}px`;
        p.style.top = `${posY}px`;
        p.style.opacity = opacity;
        p.style.transform = `translate(-50%, -50%) scale(${scale})`;
        
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
    void element.offsetWidth; // trigger reflow
    element.classList.add(className);
    
    // Automatically clean up class when animation ends
    element.addEventListener('animationend', function handler() {
      element.classList.remove(className);
      element.removeEventListener('animationend', handler);
    }, { once: true });
  },

  /**
   * Flash the viewport with a cybernetic colored glow
   * @param {string} color hex/rgb color
   * @param {number} duration ms
   */
  screenFlash(color = 'rgba(255,68,68,0.25)', duration = 400) {
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
      
      // Sine wave peak-and-fade
      let opacity = 0;
      if (progress < 0.25) {
        opacity = progress / 0.25; // ramp up
      } else {
        opacity = 1 - ((progress - 0.25) / 0.75); // fade out
      }
      
      flash.style.opacity = opacity;
      requestAnimationFrame(step);
    }
    
    requestAnimationFrame(step);
  }
};

// Export to window
window.Effects = Effects;
