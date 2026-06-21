PHASE_LOBBY = "lobby"
PHASE_YEAR_START = "year_start"
PHASE_DECISION_WINDOW = "decision_window"
PHASE_COMPLIANCE = "compliance"
PHASE_COMPLETE = "complete"
PHASE_PAUSED = "paused"

DEFAULT_PHASE_DURATIONS = {
    PHASE_YEAR_START: 5,
    PHASE_DECISION_WINDOW: 20,
    PHASE_COMPLIANCE: 5,
}

DEFAULT_OFFSET_USAGE_CAP = 0.1
DEFAULT_AUCTION_COUNT = 2
DEFAULT_AUCTION_PRICE_FLOOR = 80.0
DEFAULT_AUCTION_PRICE_CEILING = 300.0
DEFAULT_AUCTION_SHARE_OF_CAP = 0.12
DEFAULT_TRADE_EXPIRY_SECONDS = 20
DEFAULT_OFFSET_PRICE = 25.0
DEFAULT_PENALTY_RATE = 200.0

BOT_STRATEGY_CONSERVATIVE = "conservative"
BOT_STRATEGY_MODERATE = "moderate"
BOT_STRATEGY_AGGRESSIVE = "aggressive"
BOT_STRATEGY_OPPORTUNISTIC = "opportunistic"
BOT_STRATEGY_SPECULATOR = "speculator"

# Strategy profiles drive engine/agents.py:CompanyAgent.
# Legacy fields (abatement_threshold_fraction, offset_gap_fraction,
# auction_bid_fraction, trade_likelihood) are preserved for backward
# compatibility with saved games. Sprint 3 adds horizon and instrument-appetite
# fields the goal-driven agent reads:
#   horizon_years        — planning lookahead (1-3); >1 enables forward/VCM hedging
#   cash_target_fraction — fraction of starting cash the agent keeps in reserve
#   forward_appetite     — 0-1, how much of projected future gap to pre-buy as forwards
#   vcm_appetite         — 0-1, propensity to invest in multi-year VCM credit streams
#   otc_appetite         — 0-1, propensity to propose/accept bilateral OTC trades
#   preferred_instruments— ordered hint list, surfaced as competitor intelligence
BOT_STRATEGIES = {
    BOT_STRATEGY_CONSERVATIVE: {
        "label": "Conservative",
        "description": "Activates cheap abatement early, buys small offsets to cover gap, bids conservatively in auctions, avoids trades.",
        "abatement_threshold_fraction": 0.5,
        "offset_gap_fraction": 0.3,
        "auction_bid_fraction": 0.6,
        "trade_likelihood": 0.0,
        "horizon_years": 2,
        "cash_target_fraction": 0.4,
        "forward_appetite": 0.0,
        "vcm_appetite": 0.0,
        "otc_appetite": 0.1,
        "preferred_instruments": ["abatement", "offsets"],
    },
    BOT_STRATEGY_MODERATE: {
        "label": "Moderate",
        "description": "Activates all immediate abatement, buys offsets for half the remaining gap, bids at mid-range in auctions, occasionally trades.",
        "abatement_threshold_fraction": 1.0,
        "offset_gap_fraction": 0.5,
        "auction_bid_fraction": 0.8,
        "trade_likelihood": 0.3,
        "horizon_years": 2,
        "cash_target_fraction": 0.3,
        "forward_appetite": 0.2,
        "vcm_appetite": 0.2,
        "otc_appetite": 0.3,
        "preferred_instruments": ["abatement", "offsets", "auction"],
    },
    BOT_STRATEGY_AGGRESSIVE: {
        "label": "Aggressive",
        "description": "Activates all abatement, buys offsets aggressively, bids high in auctions, actively seeks trades.",
        "abatement_threshold_fraction": 1.0,
        "offset_gap_fraction": 0.8,
        "auction_bid_fraction": 1.0,
        "trade_likelihood": 0.5,
        "horizon_years": 2,
        "cash_target_fraction": 0.15,
        "forward_appetite": 0.3,
        "vcm_appetite": 0.3,
        "otc_appetite": 0.5,
        "preferred_instruments": ["abatement", "auction", "offsets"],
    },
    BOT_STRATEGY_OPPORTUNISTIC: {
        "label": "Opportunistic",
        "description": "Exploits price dips: buys forwards when spot is cheap, invests in VCM streams, proposes aggressive OTC trades, plans three years out.",
        "abatement_threshold_fraction": 0.9,
        "offset_gap_fraction": 0.5,
        "auction_bid_fraction": 0.7,
        "trade_likelihood": 0.6,
        "horizon_years": 3,
        "cash_target_fraction": 0.2,
        "forward_appetite": 0.6,
        "vcm_appetite": 0.4,
        "otc_appetite": 0.6,
        "preferred_instruments": ["forwards", "vcm", "offsets", "otc"],
    },
    BOT_STRATEGY_SPECULATOR: {
        "label": "Speculator",
        "description": "Minimal abatement, banks allowances, builds VCM credit streams, and sells surplus OTC at a premium in later years.",
        "abatement_threshold_fraction": 0.35,
        "offset_gap_fraction": 0.25,
        "auction_bid_fraction": 0.5,
        "trade_likelihood": 0.7,
        "horizon_years": 3,
        "cash_target_fraction": 0.25,
        "forward_appetite": 0.1,
        "vcm_appetite": 0.6,
        "otc_appetite": 0.8,
        "preferred_instruments": ["vcm", "otc", "banking"],
    },
}

YEARLY_ALLOCATION_FACTORS = {1: 0.92, 2: 0.88, 3: 0.84}

PHASE_LABELS = {
    PHASE_LOBBY: "Lobby",
    PHASE_YEAR_START: "Year Start",
    PHASE_DECISION_WINDOW: "Decision Window",
    PHASE_COMPLIANCE: "Compliance Review",
    PHASE_COMPLETE: "Session Complete",
    PHASE_PAUSED: "Paused",
}
