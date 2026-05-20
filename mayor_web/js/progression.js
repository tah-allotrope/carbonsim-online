/**
 * Climate Mayor — Progression & Engagement Engine
 * Calculates player XP, levels, compliance streaks, and performance grades.
 * Synchronizes real-time game data with localStorage.
 */

const Progression = {
  // Thresholds for Level 1 to 10
  LEVEL_THRESHOLDS: [
    0,     // Level 1
    100,   // Level 2
    250,   // Level 3
    450,   // Level 4
    700,   // Level 5
    1000,  // Level 6
    1400,  // Level 7
    1900,  // Level 8
    2500,  // Level 9
    3200   // Level 10
  ],

  /**
   * Translates XP value to level details
   * @param {number} xp 
   * @returns {object} { level, currentXp, nextLevelXp, percent }
   */
  getLevelInfo(xp) {
    let level = 1;
    for (let i = 0; i < this.LEVEL_THRESHOLDS.length; i++) {
      if (xp >= this.LEVEL_THRESHOLDS[i]) {
        level = i + 1;
      } else {
        break;
      }
    }

    const currentLevelThreshold = this.LEVEL_THRESHOLDS[level - 1] || 0;
    const nextLevelThreshold = this.LEVEL_THRESHOLDS[level] || this.LEVEL_THRESHOLDS[this.LEVEL_THRESHOLDS.length - 1] + 1000;
    
    const xpInLevel = xp - currentLevelThreshold;
    const levelRange = nextLevelThreshold - currentLevelThreshold;
    const percent = Math.min(100, Math.max(0, (xpInLevel / levelRange) * 100));

    return {
      level,
      currentXp: xp,
      xpInLevel,
      levelRange,
      nextLevelXp: nextLevelThreshold,
      percent: Math.round(percent)
    };
  },

  /**
   * Core XP scoring calculation for single-player session
   * @param {object} g game state response
   */
  calculateXP(g) {
    if (!g) return 0;
    const s = g.snapshot || {};
    const player = s.player_company || s.companies?.[0] || {};
    
    const currentYear = g.current_year || 0;
    const activeAbatementsCount = (player.active_abatement_ids || []).length;
    const achievementsCount = (g.achievements || []).length;
    const cumulativePenalties = player.cumulative_penalties || player.penalty_due || 0;
    
    // 1. Year progression
    let yearXP = currentYear * 15;
    
    // 2. Compliance history scanning
    let complianceXP = 0;
    const history = player.year_results || [];
    history.forEach(res => {
      if ((res.shortfall || 0) <= 0) {
        complianceXP += 25; // Compliant year bonus
      } else {
        complianceXP -= 10; // Shortfall penalty
      }
    });

    // 3. Abatement activation
    const abatementXP = activeAbatementsCount * 10;

    // 4. Achievements unlocked
    const achievementXP = achievementsCount * 100;

    // 5. Penalty deductions
    const penaltyXP = -Math.floor(cumulativePenalties / 10000); // deduct 1 XP per $10k in penalties

    const total = yearXP + complianceXP + abatementXP + achievementXP + penaltyXP;
    return Math.max(0, total);
  },

  /**
   * Tracks real-time active session XP and synces delta with global player lifetime XP
   * @param {string} gameId 
   * @param {object} g gameState
   * @returns {object} { activeXp, levelInfo, lifetimeXp, lifetimeLevelInfo }
   */
  syncProgress(gameId, g) {
    this.initLifetime();
    if (!gameId || !g) {
      const lifetimeXp = parseInt(localStorage.getItem('climate_mayor_lifetime_xp')) || 0;
      return {
        activeXp: 0,
        levelInfo: this.getLevelInfo(0),
        lifetimeXp,
        lifetimeLevelInfo: this.getLevelInfo(lifetimeXp)
      };
    }

    const activeXp = this.calculateXP(g);
    
    // Get last tracked XP for this game
    const lastGameXpKey = `climate_mayor_game_xp_${gameId}`;
    const lastGameXp = parseInt(localStorage.getItem(lastGameXpKey)) || 0;
    
    // Calculate delta and add to lifetime XP
    const delta = activeXp - lastGameXp;
    
    let lifetimeXp = parseInt(localStorage.getItem('climate_mayor_lifetime_xp')) || 0;
    if (delta !== 0) {
      lifetimeXp = Math.max(0, lifetimeXp + delta);
      localStorage.setItem('climate_mayor_lifetime_xp', lifetimeXp.toString());
      localStorage.setItem(lastGameXpKey, activeXp.toString());
    }

    return {
      activeXp,
      levelInfo: this.getLevelInfo(activeXp),
      lifetimeXp,
      lifetimeLevelInfo: this.getLevelInfo(lifetimeXp)
    };
  },

  /**
   * Resolves compliance streak statistics
   * @param {object} g gameState
   * @returns {object} { currentStreak, maxStreak }
   */
  getStreakInfo(g) {
    if (!g) return { currentStreak: 0, maxStreak: 0 };
    const s = g.snapshot || {};
    const player = s.player_company || s.companies?.[0] || {};
    const history = player.year_results || [];

    let currentStreak = 0;
    let maxStreak = 0;

    history.forEach(res => {
      if ((res.shortfall || 0) <= 0) {
        currentStreak++;
        if (currentStreak > maxStreak) maxStreak = currentStreak;
      } else {
        currentStreak = 0; // reset streak on shortfall
      }
    });

    // If current phase is decision_window or year_start, the current year is still active
    // We only count finalised year compliance in history
    return { currentStreak, maxStreak };
  },

  /**
   * Initializes lifetime XP variables in localStorage if missing
   */
  initLifetime() {
    if (localStorage.getItem('climate_mayor_lifetime_xp') === null) {
      localStorage.setItem('climate_mayor_lifetime_xp', '0');
    }
  },

  /**
   * Computes S/A/B/C/D grade out of 100 points
   * @param {object} g gameState
   * @returns {object} { score, grade, gradeClass, gradeLabel }
   */
  evaluatePerformance(g) {
    if (!g) return { score: 0, grade: 'D', gradeClass: 'badge-red', gradeLabel: 'Consultant' };
    
    const s = g.snapshot || {};
    const player = s.player_company || s.companies?.[0] || {};
    const history = player.year_results || [];
    const playedYears = history.length || 1;
    const cumulativePenalties = player.cumulative_penalties || player.penalty_due || 0;
    
    // 1. Compliance score (max 50 points)
    const compliantYears = history.filter(r => (r.shortfall || 0) <= 0).length;
    const complianceScore = (compliantYears / playedYears) * 50;

    // 2. Financial health score (max 25 points)
    const startingCash = player.starting_cash || 500000; // typical starting cash fallback
    const currentCash = player.cash || 0;
    const financialScore = Math.min(25, Math.max(0, (currentCash / startingCash) * 25));

    // 3. Penalties score (max 25 points)
    // Scale penalties: $500k in penalties completely wipes this out
    const penaltiesScore = Math.max(0, 25 - (cumulativePenalties / 20000));

    const totalScore = Math.round(complianceScore + financialScore + penaltiesScore);

    let grade = 'D';
    let gradeClass = 'badge-red';
    let gradeLabel = 'Discredited Mayor';

    if (totalScore >= 95) {
      grade = 'S';
      gradeClass = 'badge-blue pulse-glow-cyan';
      gradeLabel = 'Global Green Innovator';
    } else if (totalScore >= 80) {
      grade = 'A';
      gradeClass = 'badge-green';
      gradeLabel = 'Carbon Neutral Leader';
    } else if (totalScore >= 65) {
      grade = 'B';
      gradeClass = 'badge-orange';
      gradeLabel = 'Standard Compliance Mayor';
    } else if (totalScore >= 50) {
      grade = 'C';
      gradeClass = 'badge-orange';
      gradeLabel = 'Struggling Transitioneer';
    }

    return {
      score: totalScore,
      grade,
      gradeClass,
      gradeLabel
    };
  },

  /**
   * Save a game score and return if it represents a personal best for the difficulty
   * @param {string} difficulty 
   * @param {number} score 
   * @returns {boolean} isNewPersonalBest
   */
  checkAndSavePersonalBest(difficulty, score) {
    if (!difficulty) return false;
    const key = `climate_mayor_pb_${difficulty}`;
    const previousPB = parseInt(localStorage.getItem(key)) || 0;
    
    if (score > previousPB) {
      localStorage.setItem(key, score.toString());
      return true;
    }
    
    return false;
  }
};

// Export globally
window.Progression = Progression;
