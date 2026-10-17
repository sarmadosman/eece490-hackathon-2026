# Methods and assumptions

**Current final argument:** demand and preparation, observational promotion comparison with uncertainty, and customer continuity with testable timing. The latest changes refine the interpretation rather than replacing this playbook. [Customer methods](customer_methodology.md) document fixed cohorts, coverage, and complete follow-up. `scripts/promotion_test.py` preserves its calculations; its overlapping non-promotion comparisons describe variation, not a confidence interval or power analysis. The roughly 29% same-mix benchmark is supporting accounting, while the pilot criterion is total branch contribution after incremental costs. Garden cost/margin and food-offer material below remain supporting work.

## Calendar extension and revised objective

The accepted business problem is “How can Stories apply changes to maximize profit in times of abrupt change?” Compare pre/post observations, then identify two or three meaningful patterns supporting decisions. Offers, pricing/promotion tests, cost audits, and preparation changes are possible actions. Treat the user's inclusive dates as supplied assumptions: Ramadan February 17–March 18; Lent February 18–April 2. `calendar.py` exports daily and phase-level metrics, category economics, seven/fourteen-day boundary comparisons, and retrospective adjusted associations.

Phase rates pool the relevant numerator and denominator; phase totals are divided by actual calendar days when reporting orders/day. The isolated Ramadan-only phase is one day and cannot justify a general Ramadan-versus-Lent comparison. Evening means 18:00–23:59 in the recorded clock; it is not a sunset, fasting, or observance measure. Product categories do not establish dietary suitability.

OLS models use log daily order counts or daily rates as outcomes, weekday fixed effects, elapsed-week trend, and separate Ramadan/Lent/post–March 2 indicators. Rates are fit with equal weight per observed day; descriptive phase rates are weighted by orders. Specifications vary April/June follow-up, linear/quadratic trend, and a post-cutoff slope. Models are fit separately to chain-wide daily outcomes and each branch; branch rows are not treated as independent replicates of one shared calendar shock. HAC covariance uses seven lags, small-sample correction, and t-based 95% intervals. No multiple-comparison correction or causal identification is claimed; do not select a favorable model from the many results. Full-rank designs do not solve confounding.

These explanatory models consume post-event outcomes. Their retrospective associations are not out-of-sample forecast results. The original pre–March 2 forecasts are retained as explicitly calendar-unadjusted references; they already include calendar-active training days. Religious effects cannot be learned reliably from starts only one day apart and a single observed season. Promotions, changing observance intensity, holidays, opening hours, and latent demand remain unresolved. Longer historical data and credible controls are needed for stronger attribution. See the [calendar decision memo](../reports/calendar_decision_memo.md) for results and operating implications.

Method references: [interrupted-time-series tutorial](https://pmc.ncbi.nlm.nih.gov/articles/PMC5407170/), [statsmodels HAC covariance documentation](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html).

## Decision and scope

The primary workflow compares item-level sales, listed/realized prices, recorded costs, contribution, discounts, branch performance, and menu mix before choosing actions. Three exploratory arguments are presented with alternatives, value thresholds/scenarios, and validation plans. No causal treatment response or global profit optimum is established. Recorded gross profit is the available accounting measure; missing operating costs must be included before claiming realized profit improvements.

The earlier bakery-versus-meal investigation is an optional supporting action. Its basket, contribution, and scenario definitions below remain applicable when that action is selected. Historical co-purchases are not offer-treatment labels.

## Item/event comparisons and price interpretation

`business.py` exports equal 7-, 14-, and 28-day comparisons around March 2, Ramadan start, Lent start, and the first day after each supplied end date. All observed products and branches are included, with chain totals as separate aggregates. Exposure tables give exact Ramadan/Lent/post–March 2 days; unequal exposure and concurrent events remain confounders. Each period uses units and recorded money sums; quantity-weighted list price/cost and revenue/unit are distinct measures. Missing before/after observations remain missing rather than implying a valid growth estimate. Item windows with fewer than 20 units in either period receive a small-base flag; this is a display aid, not a statistical power threshold.

The data have one listed price within each branch/product across the history. Realized revenue/unit varies through discounts, while between-branch price comparisons also differ in costs, demand, and customers. Neither identifies price elasticity. The illustrative promotion threshold is `1 − observed post-window gross profit/unit ÷ normal-list-price contribution/unit`: the proportion of post-window units that could be lost at normal list price while preserving that item's recorded gross contribution, under unchanged costs/mix and before other operating effects. It is not a demand forecast. The gross-profit-neutral volume increase under a lower unit contribution is `old contribution/unit ÷ new contribution/unit − 1`.

The primary branch comparison shows whether a gap persists across phases; a persistent gap is a baseline constraint, not a new disruption effect. Conditional cost-gap closure holds observed quantities, prices, and discounts fixed and assumes the reference cost is comparable and partially attainable. The scenarios explicitly subtract no implementation cost, so that cost must be assessed separately. Additional-product scenarios separately disclose assumed incremental purchases, waste, operating cost, setup, and substitution assumptions. All scenario values remain hypothetical.

## Windows, baskets, and data quality

Cutoff: March 2, 2026, from the user's context. The matched comparison uses February 2–March 1 and March 2–29: two adjacent 28-day windows containing equal weekday counts. This controls weekday exposure, not promotions, seasonal changes, holidays, or changing customer composition. Full-history summaries are labeled separately.

Count distinct transaction IDs for orders. Beverage categories are Hot Coffee, Cold Coffee, and Matcha & Tea. Cold Drinks are excluded to match the chat's proposed target; expanding the category definition would require a separate sensitivity check. Foods are the exact Bakery and Meals categories; Breakfast, Sandwiches, and Desserts are distinct categories.

Historical eligible orders contain a target beverage and neither Bakery nor Meals. This is an opportunity-sizing proxy from completed baskets. For a live pilot, eligibility must be recorded before the offer when the customer has requested a beverage and has not yet requested either food category. Do not define eligibility using the customer's response to the offer.

Missing customer IDs are retained. No customer-level propensity or retention claim is made. Exact duplicates are retained and key economics repeated after deduplication. The accounting formulas reconcile within one cent. The report includes source hash, row counts, and missingness. Recorded product cost is not known to include all variable operating costs.

## Forecasting without lookahead

Daily branch order counts are fit only on January 1–March 1. Candidates: last observed matching weekday; mean of the last four matching weekdays; ordinary linear regression on elapsed weeks and weekday indicators. Forecasts are clipped at zero. Fixed-origin multi-week baselines never consume future actual values.

Expanding-window backtests start with 28 days and advance seven days. There are three overlapping 14-day folds and only one 28-day fold in the available 60-day pre-cutoff history. Select each branch's model on mean 14-day absolute error; report every candidate at both horizons. These are development backtests with few, partly overlapping folds; selected-model errors are not an independent final performance estimate. The held-out post-cutoff actuals do not influence selection.

The final model is refit on all 60 pre-cutoff days and projected for March 2–29. Actual minus projected is a deviation from continuation of earlier patterns. No branch has been established as unaffected by conflict; promotions and calendar effects remain competing explanations. A credible causal no-war estimate is beyond this dataset alone.

Shaded bands use the selected model's 90th percentile absolute 14-day backtest error. They are **historical-error sensitivity bands**, not calibrated 90% prediction intervals. Selection reuse, overlapping folds, sparse 28-day validation, and a possible regime change prevent a reliable coverage claim. No confidence interval for cumulative impact is implied. A longer pre-period and independent calibration sample are needed for formal predictive intervals.

For preparation, compare yesterday's available same-weekday sales with the mean of the prior four matching weekdays, updated daily using only prior outcomes. Backtest March 2–June 30. These predict observed food units, not latent demand or optimal stock. Evaluate MAE and WAPE; do not translate forecast errors into claimed waste savings without availability and waste records.

## Product selection and economics

Export every branch/product candidate with quantity-weighted price and cost. For the illustrative scenario table, choose the food product with the most existing beverage-pair orders within each branch/category; break ties by normal-price contribution. This gives candidates with some observed pairing support, not proven best offers. The tradeoff chart preserves alternatives with higher contribution but less pairing evidence.

The illustrative $2 minimum contribution used in discount ceilings is a configurable business assumption, not a measured requirement. A zero ceiling with an infeasible flag means the target contribution is already unattainable, even at full price.

For N eligible orders, additional attachment a, counterfactual spontaneous attachment b, discount d, list price p, recorded cost c, per-addition operating cost o, substitution fraction s, displaced contribution m, extra waste w, and fixed cost F:

`incremental contribution = N*a*(p-c-d-o-s*m) - N*b*d - w*c - F`

`break-even a = (N*b*d + w*c + F) / (N*(p-c-d-o-s*m))`

The threshold is undefined if per-addition contribution is nonpositive, and infeasible if it exceeds 1−b. Baseline and additional food purchases are disjoint. This assumes a single offered food unit per eligible order and allocates the entire bundle discount against food contribution. Model changes in beverage choice separately if they occur.

Exported scenarios normalize to 1,000 eligible orders. Additional attachment is 2%, 5%, or 10%; extra waste is 20, 10, or 5 units; fixed costs are $100, $50, or $25. All use 5% counterfactual spontaneous attachment, $0.25 operating cost per addition, and 10% substitution of an item with $2 contribution. Compare discounts of $0 and $1. These are stress assumptions, not estimated conversion, costs, or probabilities. Food prices/costs alone are measured. The calculator allows each assumption to change independently; scenario labels do not imply likelihood.

## Rejected shortcuts

- A before/after increase cannot isolate war's effect because demand already trends and promotions change.
- Complex ML cannot repair two months of baseline history or provide offer treatment labels.
- Basket lift or attachment does not estimate incremental response to a suggestion.
- A universal bundle price ignores branch cost differences.
- Higher meal contribution alone cannot beat bakery if bakery generates sufficiently more additional purchases.
- A sales summary or chatbot does not answer which operating action deserves a pilot.
