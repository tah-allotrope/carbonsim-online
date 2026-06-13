/**
 * CarbonSim Online — Retro Chiptune SFX Engine
 * Procedural Web Audio SFX voiced for an 8/16-bit tycoon register.
 * Zero samples, zero assets, lightweight.
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

    this.isMuted = localStorage.getItem('climate_mayor_muted') === 'true';

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) {
      console.warn("Web Audio API not supported in this browser.");
      return;
    }

    try {
      this.ctx = new AudioContextClass();
      this.masterGain = this.ctx.createGain();
      this.masterGain.connect(this.ctx.destination);
      this.masterGain.gain.setValueAtTime(this.isMuted ? 0 : 0.5, this.ctx.currentTime);
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
      const targetVol = this.isMuted ? 0 : 0.5;
      this.masterGain.gain.setTargetAtTime(targetVol, this.ctx.currentTime, 0.05);
    }

    if (!this.isMuted) {
      setTimeout(() => this.playSFX('click'), 100);
    }

    return this.isMuted;
  },

  getMuteState() {
    return localStorage.getItem('climate_mayor_muted') === 'true';
  },

  /**
   * Procedural Chiptune SFX Generators
   */
  playSFX(type) {
    this.ensureCtx();
    if (this.isMuted || !this.ctx) return;

    const now = this.ctx.currentTime;

    switch (type) {
      case 'click': {
        // Sharp square blip
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(220, now + 0.04);

        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(now);
        osc.stop(now + 0.06);
        break;
      }

      case 'card-draw': {
        // Quick upward square arpeggio
        const notes = [220, 293.66, 440];
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
        gain.connect(this.masterGain);

        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          osc.type = 'square';
          osc.frequency.setValueAtTime(freq, now + idx * 0.04);
          osc.connect(gain);
          osc.start(now + idx * 0.04);
          osc.stop(now + idx * 0.04 + 0.08);
        });
        break;
      }

      case 'card-resolve': {
        // Major triad blip
        const notes = [523.25, 659.25, 783.99];
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
        gain.connect(this.masterGain);

        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          osc.type = idx === 0 ? 'square' : 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.02);
          osc.connect(gain);
          osc.start(now + idx * 0.02);
          osc.stop(now + idx * 0.02 + 0.18);
        });
        break;
      }

      case 'year-advance': {
        // Fast ascending major arpeggio — retro level-up fanfare
        const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50];
        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.55);
        gain.connect(this.masterGain);

        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          osc.type = idx % 2 === 0 ? 'square' : 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.05);
          osc.connect(gain);
          osc.start(now + idx * 0.05);
          osc.stop(now + idx * 0.05 + 0.14);
        });
        break;
      }

      case 'activate': {
        // Positive square + triangle confirmation
        const sq = this.ctx.createOscillator();
        const tri = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        sq.type = 'square';
        sq.frequency.setValueAtTime(523.25, now);
        sq.frequency.exponentialRampToValueAtTime(1046.50, now + 0.12);

        tri.type = 'triangle';
        tri.frequency.setValueAtTime(659.25, now);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);

        sq.connect(gain);
        tri.connect(gain);
        gain.connect(this.masterGain);

        sq.start(now);
        tri.start(now);
        sq.stop(now + 0.2);
        tri.stop(now + 0.2);
        break;
      }

      case 'penalty': {
        // Detuned square alarm
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc1.type = 'square';
        osc1.frequency.setValueAtTime(150, now);
        osc1.frequency.setValueAtTime(100, now + 0.15);
        osc1.frequency.setValueAtTime(150, now + 0.3);

        osc2.type = 'square';
        osc2.frequency.setValueAtTime(153, now);
        osc2.frequency.setValueAtTime(102, now + 0.15);
        osc2.frequency.setValueAtTime(153, now + 0.3);

        gain.gain.setValueAtTime(0.14, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.masterGain);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.5);
        osc2.stop(now + 0.5);
        break;
      }

      case 'success': {
        // Major 7th victory chime
        const root = 349.23; // F4
        const notes = [root, root * 1.25, root * 1.5, root * 1.875];
        const gain = this.ctx.createGain();

        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.12, now + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
        gain.connect(this.masterGain);

        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          osc.type = idx === 0 ? 'square' : 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.02);
          osc.connect(gain);
          osc.start(now);
          osc.stop(now + 0.6);
        });
        break;
      }

      case 'save': {
        // 8-bit data chirp
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = 'square';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.setValueAtTime(1760, now + 0.04);
        osc.frequency.setValueAtTime(1320, now + 0.08);

        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(now);
        osc.stop(now + 0.14);
        break;
      }

      case 'error': {
        // Flat square buzz
        const osc1 = this.ctx.createOscillator();
        const osc2 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc1.type = 'square';
        osc1.frequency.setValueAtTime(130, now);

        osc2.type = 'square';
        osc2.frequency.setValueAtTime(132, now);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);

        osc1.connect(gain);
        osc2.connect(gain);
        gain.connect(this.masterGain);

        osc1.start(now);
        osc2.start(now);
        osc1.stop(now + 0.2);
        osc2.stop(now + 0.2);
        break;
      }
    }
  },

  /**
   * Generative retro ambient drone.
   * Slow triangle pulse with a very low filter sweep.
   */
  startAmbient() {
    this.ensureCtx();
    if (this.ambientRunning || !this.ctx) return;
    this.ambientRunning = true;

    const now = this.ctx.currentTime;

    const osc1 = this.ctx.createOscillator();
    const osc2 = this.ctx.createOscillator();
    const filter = this.ctx.createBiquadFilter();
    this.ambientNode = this.ctx.createGain();

    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(65.41, now);

    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(98.00, now);

    filter.type = 'lowpass';
    filter.Q.setValueAtTime(2, now);
    filter.frequency.setValueAtTime(120, now);

    this.ambientNode.gain.setValueAtTime(0.001, now);
    this.ambientNode.gain.linearRampToValueAtTime(0.18, now + 2.0);

    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(this.ambientNode);
    this.ambientNode.connect(this.masterGain);

    osc1.start(now);
    osc2.start(now);

    this.ambientOscs = [osc1, osc2];

    let phase = 0;
    const sweep = () => {
      if (!this.ambientRunning || !this.ctx) return;

      const time = this.ctx.currentTime;
      const nextFreq = 180 + Math.sin(phase) * 80;

      filter.frequency.setTargetAtTime(nextFreq, time, 1.2);
      phase += 0.1;

      this.ambientTimer = setTimeout(sweep, 1800);
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
        this.ambientNode.gain.linearRampToValueAtTime(0.001, now + 1.0);

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

window.AudioManager = AudioManager;
