# Business decisions during abrupt changes: three evidence-led patterns

**Supporting prior analysis:** this item/branch memo is preserved for reference. The user's current direction centers on customer-level patterns in [the main decision memo](decision_memo.md), rather than Garden underperformance or discount economics.

**Problem:** How can Stories apply changes to maximize profit in times of abrupt change?

Compare the supplied war-context, Ramadan, and Lent periods, then identify patterns that support operating decisions. The current evidence supports investigating product-specific promotions, branch-specific contribution constraints, and small preparation/product changes. Bakery-versus-meal suggestions are one optional action, not the primary problem statement.

## Comparison design and limits

Use the supplied dates: Ramadan February 17–March 18, Lent February 18–April 2, and March 2 as the war-context cutoff. [Equal-window item comparisons](item_event_changes.csv) cover 7, 14, and 28 days on each side of all five start/end boundaries. [Calendar exposure](event_window_calendar_exposure.csv) discloses overlap. [Branch economics by phase](branch_phase_economics.csv) separate six phases, including the one-day Ramadan-only phase that cannot support generalization.

The specific examples below use February 2–March 1 versus March 2–29. These equal 28-day windows balance weekdays but have different religious-calendar exposure. Alternative cutoffs also show growth, so neither growth alone nor the selected examples identify a causal war effect. Full tables expose other items and windows; these are exploratory business arguments, not confirmed effects selected through independent hypothesis testing.

## Pattern 1: item sales and discounts must be judged through contribution

| Harbour item | Units, before → after | Realized revenue/unit | Recorded gross profit/unit | Total gross profit |
|---|---:|---:|---:|---:|
| Iced Latte | 159 → 189 | $5.59 → $5.32 | $3.93 → $3.66 | $625.16 → $691.53 |
| Frozen Yoghurt Cup | 70 → 70 | $6.43 → $6.20 | $3.74 → $3.51 | $261.95 → $245.47 |

List prices stay $5.62 and $6.46 respectively; recorded unit costs also remain unchanged. Discounted-unit exposure rises for both. The Frozen Yoghurt Cup example loses recorded contribution without a volume increase. Iced Latte gains recorded total contribution despite weaker contribution per unit. Thus the correct response is product-specific investigation, not automatically retaining or cancelling every discount.

**Decision:** audit promotion eligibility/depth and test a narrower or normal-price alternative. Measure total incremental contribution after operating effects, rather than treating extra units as success.

**Economic argument:** at the observed post-window cost and product mix, normal list price would permit at most approximately 7.6% fewer Iced Latte units, or 7.0% fewer Frozen Yoghurt Cup units, while preserving each item's observed post-window gross contribution. This is an accounting break-even calculation before extra operating costs, not a forecast of demand under different pricing.

**Competing explanations and test:** calendar mix, broad growth, availability, and selection into discounts could explain the observations. Listed prices are constant within branch/product, so price elasticity cannot be estimated from this comparison. Randomize promotion depth/eligibility within contemporaneous branch/daypart blocks, tracking basket contribution, substitution, waste, and costs.

Evidence: [all item comparisons](item_event_changes.csv), [underlying item summaries](item_event_summary.csv), [promotion/context checks](exploratory_findings.md).

## Pattern 2: traffic growth does not remove unequal branch economics

Garden's recorded gross margin stays approximately 46.8–47.2% across the multi-day phases, while Harbour remains approximately 64.9–65.6%. Garden's median same-product listed-price ratio is 0.953 relative to Harbour and its median recorded-cost ratio is 1.430. The gap persists across periods rather than emerging at March 2.

**Decision:** use branch-specific contribution floors and investigate Garden's recorded costs before applying chain-wide discounts, prices, or volume targets. A persistent baseline constraint can change which response is profitable during disruption; it should not be presented as a new shock-caused deterioration.

**Economic argument:** during March 2–29, Garden's quantities multiplied by the same-product cost difference from Harbour sum to $2,356.14. If costs were comparable and closing 10%, 25%, or 50% of that gap were attainable, conditional gross contribution would improve by $235.61, $589.04, or $1,178.07 before implementation costs. These are hypothetical benchmark scenarios, not verified savings.

**Competing explanations and test:** suppliers, recipes, quality, deliveries, cost allocations, or configuration may justify or explain the gap. Validate definitions against purchase and recipe records, rank the material differences, and test an achievable change before claiming savings.

Evidence: [branch event comparisons](branch_event_comparison.csv), [branch phase economics](branch_phase_economics.csv), [same-product economics](same_product_economics.csv), [conditional scenarios](supporting_item_value_scenarios.csv).

## Pattern 3: product demand and category share can require different actions

Chain-wide Bakery rises from 1,648 to 1,677 recorded units (+1.8%) while losing about 1.5 percentage points of unit share. A lower share is not necessarily lower absolute demand.

Meals units increase 46.2%, 25.6%, and 23.6% across 14-, 28-, and 42-day windows; the direction persists but the magnitude and calendar composition change. At Harbour, Quinoa Bowl rises from 18 to 32 units, with recorded gross profit/unit about $7.24 → $7.31. This is a small-base candidate for investigation, not evidence of a validated chain-wide preference or dietary suitability.

**Decision:** test small product-specific preparation changes, tracking unsold units and unavailable items. Do not cut Bakery preparation solely because its share falls. A normal-price suggestion or bundle can be tested if customer demand creation is the question; it is not a required solution.

**Economic argument:** assuming 10 genuinely additional Quinoa Bowl purchases at $12.23, recorded cost $4.92, $0.25 incremental operating cost per addition, three extra wasted units at recorded cost, a $20 setup cost, and no substitution, conditional incremental contribution is $35.84. None of the extra purchases or operating assumptions has been observed. The scenario identifies what must be measured.

**Competing explanations and test:** growth may reflect small numbers, availability, substitution, promotions, or calendar mix. Compare preparation rules chronologically and collect waste/stockout records before optimizing stock. A randomized suggestion test is optional when measuring incremental purchases.

Evidence: [item comparisons](item_event_changes.csv), [window/category changes](category_window_changes.csv), [calendar exposure](window_calendar_exposure.csv), [conditional scenarios](supporting_item_value_scenarios.csv).

## Role of the calendar analysis

Broad evening share stays near 50%, and there is no robust separate Ramadan/Lent meal-attachment effect in the current analysis. Do not invent a religious-calendar menu or timing effect. Those periods remain necessary comparisons and alternative explanations. [Detailed calendar analysis](calendar_decision_memo.md).

The original pre–March 2 projection is a calendar-unadjusted supporting reference. It neither defines the problem nor estimates verified no-war demand. The [earlier food-offer memo](food_offer_memo.md) is retained as supporting work.

## Practical recommendation

Prioritize a focused promotion audit/test and a branch costing audit. Evaluate a small preparation/product trial where availability and waste can be recorded. Choose the final two or three patterns according to evidence strength, materiality, and operational feasibility. Use the [three validation plans](../docs/pilot.md) before wider changes. The available data support measured recorded-contribution comparisons and conditional economics; realized profit maximization also requires labor, waste, capacity, implementation, and substitution data.
