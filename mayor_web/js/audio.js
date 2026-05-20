/**
 * Climate Mayor — Cyberpunk Synthesizer Audio Engine
 * Sfx and ambient soundtracks synthesized procedurally via Web Audio API.
 * Lightweight, zero-asset, high-performance, and perfectly on-theme.
 */

const AudioManager = {
  ctx: null,
  masterGain: null,
  ambientNode: null,
  isMuted: false,
  initialized: false,
  ambientRunning: false,
  
  init() {
    if (this.initialized) return;
    
    // Load mute state
    this.isMuted = localStorage.getItem('climate_mayor_muted') === 'true';
    
    // Create AudioContext on demand or on first click
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) {
      console.warn("Web Audio API not supported in this browser.");
      return;
    }
    
    try {
      this.ctx = new AudioContextClass();
      this.masterGain = this.ctx.createGain();
      this.masterGain.connect(this.ctx.destination);
      this.masterGain.gain.setValueAtTime(this.isMuted ? 0 : 0.6, this.ctx.currentTime);
      this.initialized = true;
    } catch (e) {
      console.error("Failed to initialize AudioContext:", e);
    }
  },
  
  ensureCtx() {
    this.init();
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  },
  
  toggleMute() {
    this.ensureCtx();
    this.isMuted = !this.isMuted;
    localStorage.setItem('climate_mayor_muted', this.isMuted ? 'true' : 'false');
    
    if (this.masterGain) {
      // Smooth volume fade to avoid clicks
      const targetVol = this.isMuted ? 0 : 0.6;
      this.masterGain.gain.setTargetAtTime(targetVol, this.ctx.currentTime, 0.08);
    }
    
    // Trigger success SFX as mute feedback if unmuting
    if (!this.isMuted) {
      setTimeout(() => this.playSFX('click'), 100);
    }
    
    return this.isMuted;
  },
  
  getMuteState() {
    return localStorage.getItem('climate_mayor_muted') === 'true';
  },

  /**
   * Procedural SFX Generators
   */
  playSFX(type) {
    this.ensureCtx();
    if (this.isMuted || !this.ctx) return;
    
    const now = this.ctx.currentTime;
    
    switch (type) {
      case 'click': {
        // High-frequency crisp metallic tick
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(2000, now);
        osc.frequency.exponentialRampToValueAtTime(300, now + 0.05);
        
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.06);
        break;
      }
      
      case 'card-draw': {
        // Smooth sweeping filter whoosh
        const noise = this.ctx.createOscillator(); // sweep sine/tri detuned
        const filter = this.ctx.createBiquadFilter();
        const gain = this.ctx.createGain();
        
        noise.type = 'sawtooth';
        noise.frequency.setValueAtTime(80, now);
        noise.frequency.exponentialRampToValueAtTime(600, now + 0.35);
        
        filter.type = 'lowpass';
        filter.Q.setValueAtTime(8, now);
        filter.frequency.setValueAtTime(100, now);
        filter.frequency.exponentialRampToValueAtTime(800, now + 0.35);
        
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.06, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterGain);
        
        noise.start(now);
        noise.stop(now + 0.45);
        break;
      }
      
      case 'card-resolve': {
        // Double electronic coin/bell chime
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(523.25, now); // C5
        osc1.frequency.setValueAtTime(659.25, now + 0.08); // E5
        
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(783.99, now + 0.04); // G5
        osc2.frequency.setValueAtTime(1046.50, now + 0.12); // C6
        
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0.12, now + 0.06);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
        
        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.masterGain);
        
        osc1.start(now);
        osc2.start(now + 0.04);
        osc1.stop(now + 0.32);
        osc2.stop(now + 0.32);
        break;
      }
      
      case 'year-advance': {
        // High-fanfare ascending retro cyber arpeggio
        const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50]; // C major arpeggio
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
        gain.connect(this.masterGain);
        
        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.06);
          osc.connect(gain);
          osc.start(now + idx * 0.06);
          osc.stop(now + idx * 0.06 + 0.2);
        });
        break;
      }
      
      case 'activate': {
        // Analog sub-bass thump & positive validation tone
        const sub = this.ctx.createOscillator();
        const beep = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        sub.type = 'sine';
        sub.frequency.setValueAtTime(90, now);
        sub.frequency.exponentialRampToValueAtTime(45, now + 0.2);
        
        beep.type = 'sine';
        beep.frequency.setValueAtTime(587.33, now); // D5
        beep.frequency.setValueAtTime(880.00, now + 0.08); // A5
        
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
        
        sub.connect(gain);
        beep.connect(gain);
        gain.connect(this.masterGain);
        
        sub.start(now);
        beep.start(now);
        sub.stop(now + 0.3);
        beep.stop(now + 0.3);
        break;
      }
      
      case 'penalty': {
        // Detuned sweeping synthesizer alarm warning
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const filter = this.ctx.createBiquadFilter();
        const gain = this.ctx.createGain();
        
        osc1.type = 'sawtooth';
        osc1.frequency.setValueAtTime(140, now);
        osc1.frequency.linearRampToValueAtTime(80, now + 0.4);
        
        osc2.type = 'sawtooth';
        osc2.frequency.setValueAtTime(143, now); // detune
        osc2.frequency.linearRampToValueAtTime(81, now + 0.4);
        
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(500, now);
        filter.frequency.exponentialRampToValueAtTime(200, now + 0.4);
        
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.linearRampToValueAtTime(0.2, now + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
        
        osc1.connect(filter);
        osc2.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterGain);
        
        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.5);
        osc2.stop(now + 0.5);
        break;
      }
      
      case 'success': {
        // Celestial achievement chime pad
        const root = 349.23; // F4
        const thirds = [root, root * 1.25, root * 1.5, root * 1.875]; // F Major / Major 7 chord
        const gain = this.ctx.createGain();
        
        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.12, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.95);
        gain.connect(this.masterGain);
        
        thirds.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.03);
          osc.connect(gain);
          osc.start(now);
          osc.stop(now + 1.0);
        });
        break;
      }
      
      case 'save': {
        // Digital data transfer chirp
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.setValueAtTime(1760, now + 0.05);
        osc.frequency.setValueAtTime(1320, now + 0.1);
        
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        osc.start(now);
        osc.stop(now + 0.2);
        break;
      }
      
      case 'error': {
        // Flat buzz tone
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        
        osc1.type = 'sawtooth';
        osc1.frequency.setValueAtTime(130, now);
        
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(132, now);
        
        gain.gain.setValueAtTime(0.16, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        
        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.masterGain);
        
        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.25);
        osc2.stop(now + 0.25);
        break;
      }
    }
  },

  /**
   * Generative low-key Cyberpunk Ambient Track
   * Loops chord oscillations dynamically. Zero files required!
   */
  startAmbient() {
    this.ensureCtx();
    if (this.ambientRunning || !this.ctx) return;
    this.ambientRunning = true;
    
    const now = this.ctx.currentTime;
    
    // Create nodes
    const osc1 = this.ctx.createOscillator();
    const osc2 = this.ctx.createOscillator();
    const filter = this.ctx.createBiquadFilter();
    this.ambientNode = this.ctx.createGain();
    
    // Deep drone oscillators
    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(65.41, now); // C2
    
    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(98.00, now); // G2
    
    // Slow sweeping LFO filter
    filter.type = 'lowpass';
    filter.Q.setValueAtTime(3, now);
    filter.frequency.setValueAtTime(120, now);
    
    // Low constant volume
    this.ambientNode.gain.setValueAtTime(0.001, now);
    this.ambientNode.gain.linearRampToValueAtTime(0.25, now + 2.0); // slow fade in
    
    // Connections
    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(this.ambientNode);
    this.ambientNode.connect(this.masterGain);
    
    osc1.start(now);
    osc2.start(now);
    
    // Store variables to stop them later
    this.ambientOscs = [osc1, osc2];
    
    // Start filter modulation sweep
    let phase = 0;
    const sweep = () => {
      if (!this.ambientRunning || !this.ctx) return;
      
      const time = this.ctx.currentTime;
      // Cycle lowpass frequency between 90Hz and 280Hz every 16 seconds
      const nextFreq = 185 + Math.sin(phase) * 95;
      
      filter.frequency.setTargetAtTime(nextFreq, time, 1.0);
      phase += 0.12;
      
      // Schedule next frequency shift
      this.ambientTimer = setTimeout(sweep, 1500);
    };
    
    sweep();
  },
  
  stopAmbient() {
    if (!this.ambientRunning) return;
    this.ambientRunning = false;
    
    clearTimeout(this.ambientTimer);
    
    if (this.ambientNode && this.ctx) {
      const now = this.ctx.currentTime;
      try {
        this.ambientNode.gain.cancelScheduledValues(now);
        this.ambientNode.gain.setValueAtTime(this.ambientNode.gain.value, now);
        this.ambientNode.gain.linearRampToValueAtTime(0.001, now + 1.0); // smooth fade out
        
        setTimeout(() => {
          if (this.ambientOscs) {
            this.ambientOscs.forEach(o => {
              try { o.stop(); } catch(e) {}
            });
            this.ambientOscs = null;
          }
          if (this.ambientNode) {
            this.ambientNode.disconnect();
            this.ambientNode = null;
          }
        }, 1100);
      } catch (e) {
        console.error("Error stopping ambient track:", e);
      }
    }
  }
};

// Export globally
window.AudioManager = AudioManager;
