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

BOT_STRATEGIES = {
    BOT_STRATEGY_CONSERVATIVE: {
        "label": "Conservative",
        "description": "Activates cheap abatement early, buys small offsets to cover gap, bids conservatively in auctions, avoids trades.",
        "abatement_threshold_fraction": 0.5,
        "offset_gap_fraction": 0.3,
        "auction_bid_fraction": 0.6,
        "trade_likelihood": 0.0,
    },
    BOT_STRATEGY_MODERATE: {
        "label": "Moderate",
        "description": "Activates all immediate abatement, buys offsets for half the remaining gap, bids at mid-range in auctions, occasionally trades.",
        "abatement_threshold_fraction": 1.0,
        "offset_gap_fraction": 0.5,
        "auction_bid_fraction": 0.8,
        "trade_likelihood": 0.3,
    },
    BOT_STRATEGY_AGGRESSIVE: {
        "label": "Aggressive",
        "description": "Activates all abatement, buys offsets aggressively, bids high in auctions, actively seeks trades.",
        "abatement_threshold_fraction": 1.0,
        "offset_gap_fraction": 0.8,
        "auction_bid_fraction": 1.0,
        "trade_likelihood": 0.5,
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
