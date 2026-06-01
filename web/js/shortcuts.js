/**
 * Climate Mayor — Keyboard Shortcuts Engine
 * Captures game keys for quick gameplay moves, save/load, and volume toggles.
 * Provides a sleek hoverable HUD cheat sheet.
 */

const Shortcuts = {
  active: false,
  cheatSheetHtml: `
    <div class="shortcut-sheet-overlay" id="shortcutSheet">
      <h4 style="margin-bottom:10px;font-family:var(--mono);color:var(--accent);font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em">Keyboard Shortcuts</h4>
      <div class="shortcut-row"><span class="shortcut-key">SPACE</span> <span>Advance Year / Action</span></div>
      <div class="shortcut-row"><span class="shortcut-key">S</span> <span>Quick Save Game</span></div>
      <div class="shortcut-row"><span class="shortcut-key">M</span> <span>Toggle Sound (Mute/Unmute)</span></div>
      <div class="shortcut-row"><span class="shortcut-key">ESC</span> <span>Close Active Modal</span></div>
      <div class="shortcut-row"><span class="shortcut-key">1 - 9</span> <span>Activate Abatement 1 to 9</span></div>
    </div>
  `,

  init() {
    if (this.active) return;
    this.active = true;

    // Attach key listener
    window.addEventListener('keydown', (e) => {
      // Ignore when typing in input fields
      const activeEl = document.activeElement;
      if (activeEl && (
        activeEl.tagName === 'INPUT' || 
        activeEl.tagName === 'SELECT' || 
        activeEl.tagName === 'TEXTAREA'
      )) {
        return;
      }

      const key = e.key.toLowerCase();

      // M for mute
      if (key === 'm') {
        e.preventDefault();
        if (window.AudioManager) {
          const isMuted = AudioManager.toggleMute();
          const muteBtn = document.getElementById('muteBtn');
          if (muteBtn) {
            muteBtn.textContent = isMuted ? '🔇' : '🔊';
            muteBtn.setAttribute('title', isMuted ? 'Unmute Sound' : 'Mute Sound');
          }
          if (typeof window.showToast === 'function') {
            showToast(isMuted ? 'Audio muted' : 'Audio unmuted', 'info');
          }
        }
      }

      // S for quick save
      if (key === 's') {
        e.preventDefault();
        if (typeof window.doSave === 'function' && typeof window.GAME_ID !== 'undefined') {
          if (window.gameState && window.gameState.snapshot && window.gameState.snapshot.phase !== 'complete') {
            doSave();
          }
        }
      }

      // ESC for closing modals
      if (e.key === 'Escape') {
        e.preventDefault();
        const modals = ['saveModal', 'loadModal', 'cardModal'];
        modals.forEach(id => {
          const el = document.getElementById(id);
          if (el && !el.classList.contains('hidden')) {
            if (typeof window.closeModal === 'function') {
              closeModal(id);
            } else {
              el.classList.add('hidden');
            }
          }
        });
      }

      // SPACE/ENTER for Advance Year
      if (e.key === ' ' || e.key === 'Enter') {
        // Only advance if no modals are open
        const modalsOpen = ['saveModal', 'loadModal', 'cardModal'].some(id => {
          const el = document.getElementById(id);
          return el && !el.classList.contains('hidden');
        });

        if (!modalsOpen) {
          e.preventDefault();
          const advanceBtn = document.getElementById('advanceBtn');
          if (advanceBtn && !advanceBtn.disabled) {
            if (typeof window.doAdvanceYear === 'function') {
              doAdvanceYear();
            }
          }
        }
      }

      // 1-9 for Abatement activates
      if (e.key >= '1' && e.key <= '9') {
        const index = parseInt(e.key) - 1;
        const buttons = document.querySelectorAll('button[id^="abBtn-"]');
        if (buttons && buttons[index] && !buttons[index].disabled) {
          e.preventDefault();
          buttons[index].click();
        }
      }
    });

    this.injectUI();
  },

  /**
   * Injects key shortcuts cheat sheet trigger into header
   */
  injectUI() {
    const meta = document.querySelector('.header-meta');
    if (!meta) return;

    // Check if trigger already exists
    if (document.getElementById('shortcutTrigger')) return;

    const trigger = document.createElement('div');
    trigger.id = 'shortcutTrigger';
    trigger.className = 'shortcut-sheet-trigger';
    trigger.textContent = '⌨️';
    trigger.setAttribute('title', 'Keyboard Shortcuts');
    trigger.innerHTML = `⌨️ ${this.cheatSheetHtml}`;
    
    // Insert before Quit or Danger button in header-meta if possible
    const quitBtn = meta.querySelector('.btn-danger') || meta.lastElementChild;
    if (quitBtn) {
      meta.insertBefore(trigger, quitBtn);
    } else {
      meta.appendChild(trigger);
    }
  }
};

// Auto initialize on script load if window is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Shortcuts.init());
} else {
  Shortcuts.init();
}

window.Shortcuts = Shortcuts;
