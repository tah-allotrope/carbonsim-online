# Research Brief: Molleindustria's *McDonald's Video Game* vs. CarbonSim

**Date:** 2026-06-14
**Purpose:** Understand the design of *The McDonald's Videogame* (Molleindustria, 2006) and compare it to the current CarbonSim repo, to inform a gap analysis toward adopting its most compelling mechanics.

---

## 1. What the McDonald's Video Game is

A 2006 Flash "anti-advergame" by the Italian collective Molleindustria — a satirical management/tycoon sim where you run McDonald's for profit and are pushed, by the game's incentive structure, to externalize environmental and social costs. Its design intent is **procedural rhetoric**: the *mechanics themselves* make the argument (you *feel* the pressure to cut corners), not the text.

## 2. Core mechanics (concrete)

- **Four interconnected sectors**, switched between as panels:
  1. **Agriculture / pasture** — grow soy + raise cattle; land **degrades with overuse**, forcing rotation or buying new land by **clearing rainforest or bulldozing villages**.
  2. **Feedlot / slaughterhouse** — fatten & slaughter cattle; toggle **hormones, animal-based feed, industrial waste** → more yield but disease risk (mad cow).
  3. **Restaurant** — hire cashiers/grill staff, manage **morale** (badges / firing), serve burgers, manage queues.
  4. **Headquarters** — advertising, PR, and **"special operations": bribe** health inspectors / politicians / climatologists / nutritionists; run greenwashing & pro-obesity / third-world ad campaigns.
- **Continuous time with pause** — months auto-advance; you pause to plan, unpause to run. Creates ongoing pressure (vs. discrete turns).
- **Money loop** — profits accrue monthly; **game over at ~ -$30,000 debt**.
- **Detractor / backlash escalation** — health, environmental, and labor groups spawn **detractors** that escalate **warning → protest → boycott**, requiring damage-control spend or corruption to suppress.
- **Visible externalities** — cleared rainforest, demolished villages, sick cattle, obese customers: the harm is shown on screen.

## 3. CarbonSim today (repo)

- **Single company you control** (plus bot competitors) in a carbon ETS market.
- **Discrete turn-based years**: a `decision_window` where you **activate abatement**, **buy offsets**, then **Advance Year**; a declining **allowance cap**; **penalties** for compliance shortfall; end-of-game **grade**.
- **Competitive multiplayer** (room codes, lobby, leaderboard) + **isometric city** visual (smog ∝ emissions).
- Framing is a **neutral educational compliance sim** ("teaches ETS mechanics" per `AGENTS.md`), not satire.

## 4. Similarity matrix

| Dimension | McDonald's Video Game | CarbonSim today | Gap to "get there" |
|---|---|---|---|
| Genre | Management/tycoon sim | Management/compliance sim | ✅ shared DNA |
| Externalities theme | Env/social costs externalized | Carbon emissions vs. cap | ✅ shared; CarbonSim narrower |
| Structure | **4 interconnected sectors** (supply chain) | **1 sector** (your firm's decisions) | ❌ no multi-sector chain |
| Time | **Real-time w/ pause**, monthly | Discrete annual turns | ❌ different loop feel |
| Consequence system | **Detractors → protest → boycott** | Cash penalties only | ❌ no stakeholder/public-opinion backlash |
| Influence layer | **Bribery / PR / greenwashing** "special ops" | none | ❌ no influence/dirty-options layer |
| Resource chains | Land degradation, cattle maturation, staff morale | none | ❌ no interlinked resources |
| Procedural rhetoric | Core design goal (you feel the perverse incentive) | Neutral/educational | ◐ partial (smog visual) |
| Visible harm feedback | Strong (rainforest, villages, obesity) | Moderate (smog/city tint) | ◐ partial |

## 4b. The core message: structural futility (the design thesis)

The McDonald's Video Game is, at its heart, **unwinnable in any clean sense** — the system is rigged so that maximizing profit *requires* externalizing harm; "good play" just delays collapse. The procedural-rhetoric point is that **the structure itself is the problem**, not the player's choices within it.

**Carbon analog (the thesis CarbonSim should encode):** a carbon market — ETS caps, offsets, compliance trading — **cannot solve climate change on its own.** It rewards *paper compliance* (buy offsets, trade allowances, lobby the cap) over *real decarbonization*; a player can "win" — stay compliant, earn a high grade — while atmospheric emissions and the planetary trajectory keep worsening, because the market only reallocates a budget it cannot, alone, shrink fast enough. The market is **necessary but insufficient.** This is not anti-ETS; it is the honest systemic frame: individual market success ≠ a solved climate.

This futility must live in the **core loop and the endgame**, not as a tacked-on message — e.g. a planetary climate trajectory that keeps deteriorating largely independent of the player's compliance, a visible divergence between "market success" and "real-world outcome," and an ending that makes the insufficiency *felt*.

## 5. What "getting there" means (target for gap analysis)

Adopt the McDonald's Video Game's **compelling, opinionated tycoon design** — adapted to the carbon-compliance domain — without abandoning CarbonSim's educational core. **Pillar 0 (the spine):** encode the structural-futility thesis above — the market alone can't solve it. Then the supporting systems:
1. **Multi-sector supply chain** the player juggles (e.g. energy generation → industry → market/HQ) where decisions in one ripple to others.
2. **Real-time-with-pause loop** (or a faster tick) to replace the static annual turn and create ongoing pressure.
3. **Stakeholder / public-opinion backlash system** — regulators, communities, NGOs, investors that escalate from warning → protest → divestment/boycott, paralleling detractors.
4. **Influence / integrity layer** — lobbying, greenwashing, offset-quality gaming, regulator capture as *tempting but risky* options (the procedural-rhetoric hook: feel the pull to externalize, then face consequences).
5. **Visible, reactive externalities** — extend the isometric city so harm and reform are legible and emotionally felt.

> Note: CarbonSim's `AGENTS.md` says "game first … engaging, legible learning experience." The McD game shows how to make externality economics *visceral* — that's the design lesson to import, framed for carbon/ETS rather than anti-corporate satire.

## Sources
- [Molleindustria — McDonald's Videogame](https://www.molleindustria.org/mcdonalds/)
- [Wikipedia — McDonald's Video Game](https://en.wikipedia.org/wiki/McDonald's_Video_Game)
- [Jay is Games — review/walkthrough](https://jayisgames.com/review/mcdonalds-videogame.php)
- [TV Tropes — McDonald's Video Game](https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/McDonaldsVideoGame)
