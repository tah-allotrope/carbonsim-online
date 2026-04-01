# Building an open-source CarbonSim replica: complete technical specification

EDF's CarbonSim is an AI-enhanced, multiplayer, real-time emissions trading simulation where **~242 virtual companies** (typically 21 human-controlled and 221 AI bots) compete across 3 virtual years, each compressed into 20–30 minutes of real time. Players start long emissions and short allowances, then must comply at the lowest possible cost through abatement investments, government auctions, exchange trading, and OTC deals. This document provides every technical detail needed to build it from scratch.

The specification covers the rules engine (cap-and-trade mechanics, compliance, penalties, abatement), all three market systems (sealed-bid auctions, continuous double-auction exchange, bilateral OTC), real-time multiplayer architecture (WebSocket state sync, game state machine, timer management), data models with full schemas, matching algorithm pseudocode, and a recommended open-source tech stack with specific GitHub repositories.

---

## Part 1: The ETS rules engine and game mechanics

### How the emissions cap drives the entire simulation

The cap is the foundation. CarbonSim models a declining cap-and-trade system parameterized by real-world programs. A sample game uses a **total cap of 355,850,000 tonnes**, declining at **3% per year** (9% total over 3 years), while business-as-usual (BAU) emissions grow **2–6% per year** per sector. This widening gap between emissions and available allowances is the core driver that forces player action and creates rising carbon prices.

Real-world programs provide parameterization references. The EU ETS Phase 4 uses a linear reduction factor of **4.3% per year** (2024–2027), rising to **4.4%** (2028–2030), applied to a ~2,084 Mt baseline. California's cap-and-trade historically declined **3% per year**, and RGGI's 2025 Model Rule cuts its cap by approximately **10.5% of the 2025 budget annually** through 2033. For simulation purposes, the 3% annual decline is a proven default that creates meaningful strategic tension across 3 years without overwhelming new players.

The cap translates into allowances. Each allowance is a license to emit one tonne of CO₂. **90% of the cap** is distributed as free allocation (mimicking EU ETS industrial allocation or California's EITE provisions), while the remaining **10%** enters government-sponsored auctions. Free allocation uses benchmarking in the real EU ETS — where the top 10% most efficient installations per product define the benchmark — but CarbonSim simplifies this to a percentage of each company's verified historical emissions, configurable by the admin per sector.

```
cap[year] = cap[year-1] × (1 - capDeclineRate)
freeAllocation[company][year] = cap[year] × freeAllocationShare × company.sectorWeight
auctionVolume[year] = cap[year] × (1 - freeAllocationShare)
```

### Allowance vintages, banking, and borrowing

Allowances carry **vintage years** corresponding to game years. A Year 1 vintage allowance can be used in Year 1 or **banked** for use in Year 2 or beyond. Future-year allowances (e.g., Year 3 vintage) can be bought and sold on the exchange and at auction, but **cannot be used for compliance in prior years**. This mirrors California's system, where advance auctions sell allowances 3 years ahead of their vintage.

**Banking** — carrying unused allowances forward — is permitted up to **100% of the compliance obligation** in sample CarbonSim configurations. This creates a powerful incentive to over-comply early and accumulate a strategic reserve. The EU ETS allows unlimited banking; California imposes entity-level holding limits; RGGI allows unlimited banking but adjusts the cap to account for accumulated bank. For the simulation, the configurable banking limit as a percentage of compliance obligation is the cleanest mechanism.

**Borrowing** — using future-year allowances for current compliance — is **not permitted** in CarbonSim, consistent with all major real-world programs (EU ETS, California, RGGI all prohibit it). Future-vintage allowances can be traded but not surrendered for current-year compliance.

### Offsets: the secondary compliance instrument

Offsets differ from allowances in two critical ways: they are created by the **private sector** (not government), and they have **no vintage** — usable in any year. Each offset represents one tonne of CO₂ reduced from a source outside the ETS. CarbonSim caps offset usage at **10% of a company's compliance obligation**, matching the upper range of real-world limits (California allows 4–6%, RGGI allows 3.3%, China allows 5%).

Both allowances and offsets trade on the exchange and OTC markets, but only allowances are available at auction. The offset limit creates a strategic pricing wedge: if offsets trade at a discount to allowances (reflecting lower perceived quality or limited usability), rational players buy offsets up to their limit before purchasing additional allowances.

### Compliance calculation and penalty mechanics

At year-end, each company's compliance position is assessed:

```
effectiveEmissions = bauEmissions × (1 + growthRate) - activeAbatementReductions
totalAllowances = freeAllocation + auctionPurchases + exchangePurchases 
                  + otcPurchases + bankedFromPrior - sold
offsetsUsable = min(offsetsHeld, effectiveEmissions × offsetLimit)
compliancePosition = totalAllowances + offsetsUsable - effectiveEmissions
```

If `compliancePosition ≥ 0`, the company is compliant and surplus allowances are banked. If negative, the shortfall triggers a **penalty of $300 per missing allowance** plus a **make-good obligation** — the missing allowances must still be surrendered the following year. This dual penalty (cash + deferred surrender) mirrors real-world mechanisms: the EU ETS charges **€100/tCO₂** plus mandatory next-year surrender, while California imposes a punishing **4:1 make-good ratio** (surrender 4 allowances for each 1 missing). The $300 penalty in CarbonSim is deliberately set above the auction ceiling ($300) to ensure non-compliance is never economically rational.

Allowance surrender can be configured as **automatic** (system deducts optimally) or **manual** (player decides which vintage/type to surrender), adding another layer of strategic depth.

### Scoring: marginal cost of compliance drives the leaderboard

Players are ranked by **marginal cost of compliance** — the total cost spent to achieve compliance divided by the tonnes brought into compliance. This metric captures both abatement investment costs and net trading costs (purchases minus sales revenue). Lower is better.

```
marginalCostOfCompliance = (totalAbatementCost + totalPurchaseCost - totalSalesRevenue) 
                           / effectiveEmissions
```

The leaderboard displays both **annual rankings** and **cumulative overall rankings** across all years. The admin can toggle leaderboard visibility on or off. This scoring mechanism rewards efficient portfolio management over raw spending power.

---

## Part 2: Abatement mechanics and the MAC curve

### The abatement menu: sector-specific emission reduction options

Each company sees a **menu of abatement options** specific to its industrial sector (power, steel, cement, etc.). Each option has defined attributes:

```typescript
interface AbatementOption {
  id: string;
  name: string;                        // "Waste Heat Recovery System"
  category: 'EFFICIENCY' | 'FUEL_SWITCH' | 'PROCESS_CHANGE' | 'END_OF_PIPE' | 'SHUTDOWN';
  sectorApplicability: string[];       // ["power", "cement"]
  capitalCost: number;                 // upfront investment ($)
  annualOperatingCostDelta: number;    // change in opex (negative = savings)
  annualAbatementTonnes: number;       // CO2 reduced per year
  percentReduction: number;            // % of facility BAU reduced
  implementationDelayYears: number;    // turns before activation (0 = immediate)
  lifetime: number;                    // years the reduction persists
  macPerTonne: number;                 // annualized cost / annual abatement
  isIrreversible: boolean;             // once built, permanent
  maxPerFacility: number;              // stacking limit
}
```

Abatement categories follow the standard MAC curve ordering from cheapest to most expensive. **Energy efficiency** measures (LED retrofits, waste heat recovery, motor optimization) often have **negative** marginal costs — they save money while reducing emissions, typically $-50 to $0/tCO₂ with 5–20% reduction potential and immediate or 1-year implementation. **Fuel switching** (coal-to-gas, electrification) costs $15–60/tCO₂ with 30–50% reduction potential and 1–2 year delay. **Process changes** cost $20–80/tCO₂. **End-of-pipe controls and CCS** cost $50–150+/tCO₂ with up to 90% capture rates but 2–3 year delays. **Temporary shutdown** requires no capital but sacrifices production revenue — it represents an immediate, drastic option.

### The MAC curve as decision framework

The Marginal Abatement Cost Curve plots all available options sorted left-to-right by cost per tonne. Each bar's **width** represents abatement potential (tonnes) and **height** represents cost ($/tonne). The decision rule is simple: **implement all options whose MAC falls below the current market price of allowances**. For remaining emissions, buy allowances.

In a multi-year simulation, this creates compounding dynamics. A player who invests in efficiency (delay=0) in Year 1 gains immediate reductions. A fuel-switching investment (delay=1) ordered in Year 1 activates in Year 2. By Year 3, both investments compound — the player may be long enough to sell surplus allowances at what are now elevated prices. **Players who abate early** develop a structural advantage as the declining cap pushes prices higher in later years. This is CarbonSim's most important strategic lesson.

Abatements are noted as **irreversible** in CarbonSim — once invested, they cannot be un-invested. This creates commitment risk: if market prices fall (e.g., after a recession shock event), the abatement investment becomes a sunk cost.

---

## Part 3: The multi-year simulation state machine

### State transitions and the game clock

The simulation follows a deterministic state machine with timer-driven transitions. Each virtual year runs for a configurable 20–30 real-time minutes, during which players make all decisions simultaneously:

```
LOBBY → GAME_STARTING → YEAR_START → YEAR_ACTIVE → YEAR_END → [repeat or GAME_OVER]

Within YEAR_ACTIVE:
  ├── AUCTION_1_OPEN → AUCTION_1_CLEARING → OPEN_TRADING_1
  ├── AUCTION_2_OPEN → AUCTION_2_CLEARING → OPEN_TRADING_2  
  ├── AUCTION_3_OPEN → AUCTION_3_CLEARING → OPEN_TRADING_3
  ├── AUCTION_4_OPEN → AUCTION_4_CLEARING → YEAR_END_TRADING
  └── (Exchange + OTC + Abatement available continuously)
```

A recommended time allocation for a 30-minute year: **Year start** (90 seconds — allocation display, position assessment), **4 auction windows** of 3 minutes each (~40% of year), interspersed with **open trading periods** of ~3.5 minutes each (~47%), and a **compliance/settlement phase** (90 seconds). The server is authoritative on all timers, broadcasting `timer_tick` events every 5–10 seconds.

### Year-start events

When a new year begins, the server executes these operations in sequence:

1. **Calculate new cap**: `cap[y] = cap[y-1] × (1 - declineRate)`
2. **Grow BAU emissions** per company: `bau[c][y] = bau[c][y-1] × (1 + growthRate[c])`
3. **Distribute free allocation** proportional to sector weights
4. **Activate delayed abatements** ordered in previous years
5. **Calculate and broadcast** each player's compliance position (shortfall = emissions - allocation - banked - active abatements)
6. **Apply any shock events** configured for this year
7. **Generate auction schedule** with supply volumes and vintages
8. **Clear the order book** from the previous year
9. **Start the year timer**

### Year-end events and compliance settlement

When the year timer expires:

1. **Cancel all open orders** on the exchange
2. **Calculate final emissions** per company (BAU - abatements)
3. **Surrender allowances** (automatic or manual, oldest vintage first)
4. **Apply offset limits** (max 10% of obligation)
5. **Assess penalties** for non-compliant companies ($300/tonne + carry-forward obligation)
6. **Bank surplus** allowances (up to banking limit)
7. **Update leaderboard** with annual and cumulative scores
8. **Broadcast compliance results** to all players
9. **Transition** to next YEAR_START or GAME_OVER

### Shock events: mid-simulation parameter changes

CarbonSim supports admin-triggered **shock events** that change simulation parameters during play, testing player adaptability. Typical shocks include:

- **Cap adjustment**: One-off reduction simulating new climate legislation (mirrors EU's 117M allowance rebase)
- **Emission growth rate change**: Simulating recession (-5%) or economic boom (+3%)
- **New abatement unlock**: Breakthrough technology becomes available at lower cost
- **Offset invalidation**: Percentage of held offsets voided (simulating reversal/fraud)
- **Fuel price shock**: Changes the MAC of fuel-switching options
- **Allocation change**: Shifting from 90% free to 80% free mid-simulation

Shocks are configured by the admin before or during the game and triggered at YEAR_START or at a scheduled mid-year point.

---

## Part 4: Company and unit data model

### Entity structure

The simulation models a hierarchy of **sectors → companies → units (facilities)**. In a typical 242-entity game, sectors might include thermal power (40% of entities), steel (25%), cement (20%), and chemicals (15%). Each sector has distinct emission profiles, growth rates, and abatement menus.

```typescript
interface Sector {
  id: string;
  name: string;                      // "Thermal Power"
  fractionalEmissions: number;       // share of total system emissions
  minGrowthRate: number;             // e.g., 0.02
  maxGrowthRate: number;             // e.g., 0.06
  freeAllocationShare: number;       // sector-specific allocation rate
  maxAbatements: number;             // max abatement options per company
  aiDistribution: number;            // how many AI bots in this sector
  abatementOptions: AbatementOption[];
}

interface Company {
  id: string;
  gameId: string;
  name: string;
  sectorId: string;
  userId: string | null;             // null = AI bot
  isAI: boolean;
  cashBalance: number;               // starting capital
  canBorrow: boolean;                // admin-configurable
  borrowInterestRate: number;        // e.g., 0.05
  units: Unit[];
}

interface Unit {
  id: string;
  companyId: string;
  sectorId: string;
  name: string;                      // "Plant Alpha"
  baselineEmissions: number;         // Year 0 BAU
  currentEmissions: number;          // after growth + abatements
  growthRate: number;                // assigned from sector range
  isShutdown: boolean;               // temporary shutdown flag
  activeAbatements: string[];        // IDs of installed abatements
}
```

### AI bot behavior model

AI bots (typically ~221 out of 242 companies) are essential for market liquidity and realistic price discovery. While EDF's exact algorithms are proprietary, a rational-agent model works well:

1. **Abatement decisions**: Bot computes its MAC curve, compares to expected market price (moving average of recent trades), invests in all options below market price
2. **Auction bidding**: Bot bids at its marginal abatement cost (the cost of its next cheapest uninvested option), with some random noise (±10%) to create price diversity
3. **Exchange trading**: If long, bot posts sell limit orders at or slightly above current market price. If short, posts buy limit orders at or slightly below. Market-making bots can post both sides to create depth.
4. **OTC**: Bots can auto-accept OTC offers from human players if the price is favorable relative to their MAC

The key insight: with heterogeneous MAC curves across sectors and companies, bot behavior naturally produces realistic supply/demand dynamics and equilibrium price discovery.

---

## Part 5: The exchange — continuous double-auction order book

### Order book data structure

The exchange implements a standard **continuous double-auction** with **price-time priority** (FIFO within price levels). The data structure requires four key components working together:

```typescript
interface OrderBook {
  instrument: string;               // e.g., "ALLOWANCE-Y1", "OFFSET"
  bids: SortedMap<number, PriceLevel>;    // price → level, descending
  asks: SortedMap<number, PriceLevel>;    // price → level, ascending
  orderIndex: Map<string, Order>;         // orderId → order, O(1) lookup
  stopBuys: SortedMap<number, Order[]>;   // trigger price → orders
  stopSells: SortedMap<number, Order[]>;  // trigger price → orders
  lastTradePrice: number;
  bestBid: PriceLevel | null;             // cached, O(1) access
  bestAsk: PriceLevel | null;             // cached, O(1) access
}

interface PriceLevel {
  price: number;
  totalVolume: number;
  orders: DoublyLinkedList<Order>;        // FIFO queue
}

interface Order {
  id: string;
  companyId: string;
  side: 'BUY' | 'SELL';
  type: 'LIMIT' | 'MARKET' | 'STOP_LOSS';
  price: number;
  quantity: number;
  remainingQty: number;
  timeInForce: 'GTC' | 'IOC' | 'FOK';
  stopPrice?: number;
  timestamp: number;
  status: 'OPEN' | 'PARTIALLY_FILLED' | 'FILLED' | 'CANCELLED';
}
```

The sorted map (red-black tree or B-tree) per side gives **O(log n) insert/delete** of price levels. The doubly-linked list at each level gives **O(1) append and removal** of individual orders. The hash map gives **O(1) lookup** for cancel/modify by order ID. Cached best bid/ask pointers give **O(1) top-of-book access**.

### Price-time priority matching algorithm

```
FUNCTION matchOrder(book, incoming):
  trades = []
  oppositeSide = (incoming.side == BUY) ? book.asks : book.bids
  
  WHILE incoming.remainingQty > 0:
    bestLevel = oppositeSide.first()
    IF bestLevel == null: BREAK
    IF incoming.side == BUY AND bestLevel.price > incoming.price: BREAK
    IF incoming.side == SELL AND bestLevel.price < incoming.price: BREAK
    
    WHILE incoming.remainingQty > 0 AND bestLevel has orders:
      resting = bestLevel.orders.head()
      fillQty = MIN(incoming.remainingQty, resting.remainingQty)
      fillPrice = resting.price   // maker's price
      
      trade = createTrade(fillPrice, fillQty, incoming, resting)
      trades.push(trade)
      
      incoming.remainingQty -= fillQty
      resting.remainingQty -= fillQty
      
      IF resting.remainingQty == 0:
        bestLevel.orders.removeHead()
        book.orderIndex.delete(resting.id)
    
    IF bestLevel is empty: oppositeSide.delete(bestLevel.price)
  
  // Handle time-in-force
  IF incoming.timeInForce == FOK AND incoming.remainingQty > 0:
    ROLLBACK all trades; RETURN []
  IF incoming.timeInForce == IOC:
    RETURN trades  // cancel unfilled remainder
  
  // GTC: rest unfilled portion on the book
  IF incoming.remainingQty > 0 AND incoming.type == LIMIT:
    addToBook(book, incoming)
  
  // Trigger stop orders if any trades occurred
  IF trades.length > 0:
    book.lastTradePrice = trades.last().price
    triggerStopOrders(book)
  
  RETURN trades
```

### Exchange price variation limit (volatility cap)

CarbonSim enforces a **10% price band** around the last trade price. Orders submitted outside this band are rejected:

```typescript
function validateOrder(order: Order, book: OrderBook): boolean {
  if (!book.lastTradePrice) return true; // no reference price yet
  const upperBound = book.lastTradePrice * 1.10;
  const lowerBound = book.lastTradePrice * 0.90;
  if (order.price > upperBound || order.price < lowerBound) return false;
  return true;
}
```

This prevents flash crashes in thin simulation markets. The band is configurable by the admin. Real-world exchanges use similar mechanisms: the SEC's Limit Up/Limit Down uses 5–10% bands, and carbon exchanges like ICE Endex use daily price limits.

### Candlestick data generation from trade stream

Every executed trade feeds into a candle generator that buckets trades into time intervals:

```typescript
class CandleGenerator {
  processTrade(trade: Trade): void {
    const bucket = Math.floor(trade.timestamp / this.intervalMs) * this.intervalMs;
    if (!this.current || bucket > this.current.timestamp) {
      if (this.current) this.completed.push(this.current);
      this.current = {
        timestamp: bucket,
        open: trade.price, high: trade.price,
        low: trade.price, close: trade.price,
        volume: trade.quantity, tradeCount: 1
      };
    } else {
      this.current.high = Math.max(this.current.high, trade.price);
      this.current.low = Math.min(this.current.low, trade.price);
      this.current.close = trade.price;
      this.current.volume += trade.quantity;
      this.current.tradeCount++;
    }
  }
}
```

Generate candles at multiple granularities simultaneously (10-second, 1-minute, 5-minute) by running parallel generators. Higher intervals can be built from lower ones via hierarchical rollup. For simulation periods of 20–30 minutes, **30-second candles** provide the best balance of visual density and readability.

---

## Part 6: The auction — uniform-price sealed-bid primary market

### Auction clearing algorithm

CarbonSim runs **4 auctions per year**, each lasting approximately 3 minutes. The mechanism is a **sealed-bid, single-round, uniform-price auction** where all winning bidders pay the same clearing price. Multiple bids per player are allowed.

```
FUNCTION clearAuction(bids[], supply, priceFloor, priceCeiling):
  // Step 1: Filter by price collar
  validBids = bids.filter(b => b.price >= priceFloor AND b.price <= priceCeiling)
  
  // Step 2: Sort by price descending
  validBids.sort(descending by price, then random tiebreak)
  
  // Step 3: Accumulate demand to find clearing price
  cumulativeDemand = 0
  clearingPrice = priceFloor
  
  FOR EACH bid IN validBids:
    cumulativeDemand += bid.quantity
    IF cumulativeDemand >= supply:
      clearingPrice = bid.price    // marginal bidder sets the price
      BREAK
  
  // Step 4: Handle under-subscription
  IF cumulativeDemand < supply:
    clearingPrice = MAX(lowest bid price, priceFloor)
    allocate full quantity to all bidders
    RETURN
  
  // Step 5: Allocate full fill to all bids ABOVE clearing price
  allocated = 0
  FOR EACH bid WHERE bid.price > clearingPrice:
    bid.awardedQty = bid.quantity
    allocated += bid.quantity
  
  // Step 6: Pro-rata for bids AT clearing price
  remaining = supply - allocated
  marginalBids = bids WHERE price == clearingPrice
  totalMarginalDemand = SUM(marginalBids.quantity)
  FOR EACH marginalBid:
    marginalBid.awardedQty = FLOOR(marginalBid.quantity / totalMarginalDemand × remaining)
  
  // Step 7: All winners pay clearingPrice (uniform price)
  RETURN { clearingPrice, allocations }
```

### Auction configuration

The admin configures: number of auctions per year (**default 4**), duration of each auction window, supply per auction (split from the 10% non-free-allocation pool), **vintages offered** (current year + future years), and price collar (**floor $100, ceiling $300** in sample games). The price collar maps directly to real-world mechanisms: California's 2025 floor is **$25.87** (growing at 5% + inflation/year), and RGGI's floor is **$2.62** (growing at 7%/year). CarbonSim's $100/$300 range is deliberately compressed for pedagogical clarity.

Results are broadcast to all participants immediately after clearing, showing: clearing price, total demand vs. supply, each player's awarded quantity, and total revenue raised. This mirrors EU ETS auctions run on the European Energy Exchange, which publish results within minutes of clearing.

---

## Part 7: OTC market — bilateral negotiation

### Trade workflow

The OTC market is the simplest but least efficient mechanism — direct negotiation between one buyer and one seller:

```
Initiator creates offer → Sends to specific counterparty → 
Counterparty ACCEPTS / REJECTS / COUNTERS → Trade confirms → Settlement
```

```typescript
interface OTCOffer {
  id: string;
  initiatorId: string;
  counterpartyId: string;
  side: 'BUY' | 'SELL';          // from initiator's perspective
  instrument: string;              // "ALLOWANCE-Y2" or "OFFSET"
  quantity: number;
  pricePerUnit: number;
  expiresAt: number;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'COUNTERED' | 'EXPIRED';
  parentOfferId?: string;          // links counter-offers to originals
}
```

Settlement is instant upon acceptance: allowances transfer from seller to buyer, cash transfers from buyer to seller. OTC trades are reported to all participants in the public trade feed (maintaining market transparency) but without revealing counterparty identities.

---

## Part 8: Real-time WebSocket architecture

### Snapshot-plus-delta broadcasting pattern

The industry-standard pattern used by every major exchange (Binance, Kraken, Kalshi) is **initial snapshot plus incremental deltas** with sequence numbers:

1. On WebSocket connect: send full order book snapshot + game state snapshot
2. Ongoing: send only delta updates (price level insert/update/delete, new trades, state changes)
3. Every message carries a monotonically-increasing **sequence number** — if client detects a gap, it requests a new snapshot
4. A delta with volume `0` at a price level means that level has been removed

### Channel topology

Organize subscriptions into logical channels:

- **`orderbook:{instrument}`** — Per-instrument book snapshots + deltas (public)
- **`trades:{instrument}`** — Executed trade notifications (public)
- **`auction:{auctionId}`** — Auction lifecycle events (public)
- **`game:{gameId}`** — State machine events: year_start, year_end, shock, timer_tick (public)
- **`user:{userId}`** — Private: order fills, compliance alerts, portfolio updates
- **`leaderboard:{gameId}`** — Periodic ranking broadcasts (public)

### Concurrency model: single-threaded command queue

For a simulation handling ~200 users across ~38 sessions, a **single-threaded command queue per game session** eliminates all race conditions. All order submissions funnel into a FIFO queue; a single event loop processes them sequentially. This is exactly how the LMAX Exchange operates (processing 5M+ ops/sec on a single thread via the Disruptor ring buffer pattern). Node.js's single-threaded event loop makes this architecture natural — each game session runs as an isolated processing loop.

### State synchronization for late-joining players

When a player connects mid-game: (1) send full game state snapshot (current year, time remaining, their portfolio, compliance position), (2) send order book snapshots for each active instrument, (3) send the last N trade history entries, (4) subscribe to delta channels and apply updates on top. The sequence number system ensures no gaps or duplication.

### Event schema

```typescript
interface GameEvent {
  id: string;
  type: string;         // "trade_executed" | "year_start" | "auction_result" | ...
  seq: number;          // per-channel monotonic counter
  timestamp: number;    // server-assigned Unix ms
  gameId: string;
  year?: number;
  payload: Record<string, any>;
}
```

All state changes are persisted as an **event log** (event sourcing pattern), enabling full replay for crash recovery, audit trails, and post-game analysis.

---

## Part 9: Database schema

The following PostgreSQL schema supports the full simulation data model:

```sql
CREATE TABLE games (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  state VARCHAR(50) NOT NULL DEFAULT 'LOBBY',
  current_year INT DEFAULT 0,
  total_years INT NOT NULL,
  config JSONB NOT NULL,            -- all game parameters
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  ended_at TIMESTAMP
);

CREATE TABLE sectors (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  name VARCHAR(100) NOT NULL,
  base_emissions DECIMAL(15,2),
  growth_rate_min DECIMAL(5,4),
  growth_rate_max DECIMAL(5,4),
  free_allocation_share DECIMAL(5,4),
  abatement_options JSONB           -- array of AbatementOption
);

CREATE TABLE companies (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  sector_id UUID REFERENCES sectors(id),
  name VARCHAR(255) NOT NULL,
  user_id UUID,                     -- NULL for AI bots
  is_ai BOOLEAN DEFAULT false,
  cash_balance DECIMAL(15,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE units (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  name VARCHAR(255),
  baseline_emissions DECIMAL(15,2),
  growth_rate DECIMAL(5,4),
  is_shutdown BOOLEAN DEFAULT false
);

CREATE TABLE allowance_ledger (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  from_company_id UUID,             -- NULL for initial allocation
  to_company_id UUID,
  vintage_year INT NOT NULL,
  quantity INT NOT NULL,
  transfer_type VARCHAR(50),        -- ALLOCATION, TRADE, AUCTION, SURRENDER, PENALTY
  reference_id UUID,                -- trade_id or auction_id
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  company_id UUID REFERENCES companies(id),
  instrument VARCHAR(100) NOT NULL,
  side VARCHAR(4) NOT NULL,
  order_type VARCHAR(20) NOT NULL,
  price DECIMAL(10,2),
  quantity INT NOT NULL,
  filled_quantity INT DEFAULT 0,
  status VARCHAR(20) DEFAULT 'OPEN',
  time_in_force VARCHAR(10) DEFAULT 'GTC',
  stop_price DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE trades (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  instrument VARCHAR(100) NOT NULL,
  buy_order_id UUID REFERENCES orders(id),
  sell_order_id UUID REFERENCES orders(id),
  buyer_id UUID REFERENCES companies(id),
  seller_id UUID REFERENCES companies(id),
  price DECIMAL(10,2) NOT NULL,
  quantity INT NOT NULL,
  market_type VARCHAR(20) NOT NULL,  -- EXCHANGE, OTC, AUCTION
  year INT NOT NULL,
  executed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE auctions (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  year INT NOT NULL,
  supply INT NOT NULL,
  reserve_price DECIMAL(10,2),
  ceiling_price DECIMAL(10,2),
  clearing_price DECIMAL(10,2),
  status VARCHAR(20) DEFAULT 'PENDING',
  opened_at TIMESTAMP,
  closed_at TIMESTAMP
);

CREATE TABLE auction_bids (
  id UUID PRIMARY KEY,
  auction_id UUID REFERENCES auctions(id),
  company_id UUID REFERENCES companies(id),
  price DECIMAL(10,2) NOT NULL,
  quantity INT NOT NULL,
  awarded_quantity INT DEFAULT 0,
  submitted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE abatement_investments (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  unit_id UUID REFERENCES units(id),
  option_id VARCHAR(100),
  year_invested INT,
  year_active INT,                   -- year + implementation delay
  annual_reduction DECIMAL(15,2),
  capital_cost DECIMAL(15,2),
  is_active BOOLEAN DEFAULT false
);

CREATE TABLE compliance_records (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  company_id UUID REFERENCES companies(id),
  year INT NOT NULL,
  total_emissions DECIMAL(15,2),
  allowances_surrendered INT,
  offsets_used INT,
  shortfall INT DEFAULT 0,
  penalty_amount DECIMAL(15,2) DEFAULT 0,
  banked_forward INT DEFAULT 0,
  marginal_cost DECIMAL(10,2),
  is_compliant BOOLEAN
);

CREATE TABLE events (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  seq BIGINT NOT NULL,
  type VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(game_id, seq)
);
```

Allowance balances are computed from the **ledger** (double-entry accounting pattern): `SELECT SUM(CASE WHEN to_company_id = $1 THEN quantity ELSE -quantity END) FROM allowance_ledger WHERE (to_company_id = $1 OR from_company_id = $1)`. A materialized view or Redis cache can accelerate balance lookups during active trading.

---

## Part 10: Recommended tech stack and open-source building blocks

### Backend: Node.js + TypeScript with Colyseus

**Colyseus** (github.com/colyseus/colyseus, ~5K+ stars, MIT license) is the recommended game server framework. It provides room-based architecture where each game session is a Colyseus "room" with automatic binary delta state synchronization, built-in matchmaking, reconnection handling, and WebSocket transport — almost perfectly aligned with this use case. For 200 users across 38 sessions on a single Node.js process, Colyseus handles this trivially.

Alternative: raw `ws` library + custom pub-sub logic, which gives more control but requires implementing state sync, reconnection, and delta compression from scratch.

### Matching engine: fasenderos/nodejs-order-book

**fasenderos/nodejs-order-book** (github.com/fasenderos/nodejs-order-book, ~195 stars, TypeScript) supports limit orders, market orders, stop-limit, stop-market, OCO orders, GTC/FOK/IOC time-in-force, snapshots, and journaling. This is the **best starting point** for a TypeScript matching engine — fork and extend with the 10% price band validation and carbon-specific instrument types.

Other notable matching engine references for architecture patterns:

| Repository | Language | Stars | Notes |
|-----------|----------|-------|-------|
| exchange-core/exchange-core | Java | ~3,500+ | Ultra-fast LMAX Disruptor-based, production-grade reference architecture |
| i25959341/orderbook | Go | ~400+ | Clean API, red-black tree internals |
| joaquinbejar/OrderBook-rs | Rust | ~40+ | Thread-safe, lock-free, supports iceberg/trailing-stop |
| ridulfo/tslob | TypeScript | ~20+ | Minimal but fast (1.1M orders/sec) |
| 7u83/OpenSeSim | Java | — | Open-source stock exchange **simulator** with bot-driven markets, closest to this use case |

### Database: PostgreSQL with Prisma ORM

PostgreSQL provides ACID transactions for compliance calculations, complex queries for leaderboard ranking, and JSONB for flexible game configuration. **Prisma** (or Drizzle ORM) provides type-safe database access in TypeScript. Active order books live **in memory** within the Node.js process; only completed trades and state snapshots persist to PostgreSQL.

For single-server self-hosting simplicity, **SQLite** (via Turso/libSQL) is viable and eliminates a separate database process.

### Frontend: React + TradingView Lightweight Charts

**TradingView Lightweight Charts** (github.com/tradingview/lightweight-charts, ~10K+ stars, Apache 2.0) is purpose-built for financial data: only ~40KB, renders 10K+ candles smoothly, has a built-in `series.update()` method for real-time streaming that integrates perfectly with WebSocket feeds. Supports candlestick, line, area, and histogram series out of the box.

For the order book depth display, **AG Grid** (used by real trading platforms) or a custom React component showing price levels with volume bars provides the best UX. For the leaderboard and compliance dashboard, standard React components with Tailwind CSS suffice.

### Deployment: Docker Compose + Fly.io

Provide a **Docker Compose** configuration (Node.js + PostgreSQL) for self-hosting by institutions. For cloud deployment, **Fly.io** offers robust WebSocket support with sticky sessions and global edge routing — ideal for a WebSocket-heavy application. Railway.app is the simplest alternative for zero-config deployment from a GitHub repo.

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/carbonsim
      NODE_ENV: production
    depends_on: [db]
  db:
    image: postgres:16-alpine
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_DB: carbonsim
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
volumes:
  pgdata:
```

---

## Conclusion: from specification to working system

This specification covers the complete architecture needed to replicate CarbonSim's functionality. Three architectural decisions deserve emphasis above all others. **First**, the single-threaded command queue pattern for the matching engine eliminates race conditions entirely and is sufficient for this scale — do not over-engineer with distributed systems. **Second**, the event sourcing pattern (persisting all state changes as an append-only event log) enables crash recovery, post-game replay analysis, and debugging with minimal additional complexity. **Third**, AI bots are not optional — they are structural to the simulation. Without ~200+ bots providing market liquidity and heterogeneous MAC-curve-driven price discovery, a game with 20 human players would have insufficient depth for realistic market dynamics.

The most important parameters to get right for a pedagogically effective simulation are the **ratio between cap decline rate and emission growth rate** (which determines how much pressure builds each year), the **penalty-to-ceiling-price relationship** (penalty must exceed ceiling to prevent rational non-compliance), and the **diversity of MAC curves across sectors** (which creates natural long and short positions and drives trade volume). CarbonSim's defaults — 3% decline, 2–6% growth, $300 penalty vs $300 ceiling, 4 sectors with distinct cost curves — have been validated across 3,500+ participants in 30 countries.

The recommended implementation order: (1) game state machine with timer-driven year transitions, (2) auction engine (simplest market), (3) order book and matching engine, (4) OTC negotiation, (5) abatement menu and MAC curves, (6) AI bot agents, (7) compliance and scoring engine, (8) frontend with charts and dashboards. Each component can be developed and tested independently against the event sourcing backbone before integration.