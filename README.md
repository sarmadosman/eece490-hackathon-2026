# Stories Coffee: a playbook for abrupt change

**EECE490 Stories Coffee Hackathon**

**Team:** _<add every team member's full name here>_ · Repository owner: `sarmadosman`

---

## The answer in one paragraph

From March 2, 2026, Stories traded through three overlapping shocks: the start of the war, Ramadan (Feb 17–Mar 18) and Lent (Feb 18–Apr 2). Over those weeks, **demand did not fall. It grew, and its shape stayed the same.** Orders per day rose from 158 to 186. Evening share, takeaway share and gross profit per order did not move, and the growth matches the trend Stories already had before the war. **The discount response at Harbour lost money.** Harbour ran the same 15%-off Cold Coffee and Desserts promotion twice, once during the war/Ramadan window and once in May with no calendar event. Neither time did promoted units rise. To break even, the promotion needed +29% more units, and a lift that size would have been easy to detect in this data. Each 8-day wave gave away about $210–260 of margin, cut the promoted categories' gross profit by about a quarter, and brought in almost no new customers. **Customers were not lost either.** The identified customer base grew 6.4%. 85.5% of pre-war customers came back within 56 days, and most customers who "disappeared" from one branch were buying at another. **The playbook for the next abrupt change:** keep the operating plan but scale it to recent demand at each branch; don't use blanket discounts (if you promote, keep a holdout); and only call a customer lost after 56 days with no purchase at any branch. These three habits protect profit without any new spending. Ramadan, Lent and the war cannot be separated in this data, and we don't claim to separate them.

---

## 1. Business problem

> **How can Stories apply changes to maximize profit in times of abrupt change?**

When conditions shift suddenly, management faces three pressing decisions. **(a)** Should we change capacity, menu or hours? **(b)** Should we discount to protect traffic? **(c)** Are we losing customers, and should we try to win them back? Each one can cost money if Stories reacts to a shock that is not actually happening in its sales. We use the war/Ramadan/Lent period as a test case: what really changed, what did not, and what Stories should do the next time.

The question is **not** "how much did the war cost?" That question cannot be answered from this data (see §5). The question is which decisions the observed changes support.

## 2. Strategy and context

### 2.1 Three events in one window

The three events overlap almost completely. That makes it impossible to cleanly separate their effects:

| Phase (2026, inclusive) | Days | Orders/day | Gross profit/day | GP/order | Evening share (18:00+) | Takeaway share | Discounted-unit share |
|---|---:|---:|---:|---:|---:|---:|---:|
| Before everything (Jan 1–Feb 16) | 47 | 152.4 | $809 | $5.31 | 50.0% | 41.0% | 5.9% |
| Ramadan + Lent, pre-war (Feb 18–Mar 1) | 12 | 158.3 | $835 | $5.28 | 50.2% | 40.2% | 5.2% |
| **Ramadan + Lent + war (Mar 2–18)** | 17 | **186.1** | **$983** | $5.28 | 50.4% | 41.3% | **9.1%** |
| Lent + war (Mar 19–Apr 2) | 15 | 180.3 | $960 | $5.32 | 51.0% | 39.7% | 6.3% |
| War only, both religious periods over (Apr 3–Jun 30) | 89 | 210.3 | $1,112 | $5.29 | 50.4% | 41.0% | 6.6% |

Feb 17, the only day that is Ramadan but not Lent, is excluded from the table. A single day cannot support conclusions. Source: [calendar_phase_summary.csv](reports/calendar_phase_summary.csv).

### 2.2 How we compared before and after

Since the events cannot be separated, we did not try to assign effects to each one. We asked what changed across the whole disruption, and then whether each change was unusual compared with normal weeks. The methods:

1. **Matched windows.** We compared the 28 days before March 2 (Feb 2–Mar 1) with the 28 days after (Mar 2–29). Both windows contain the same mix of weekdays. We repeated this with 7-, 14- and 42-day windows, and around the start and end of Ramadan and Lent.
2. **Alternative cutoffs (placebo dates).** We ran the same 28-day before/after comparison at 19 other dates. If March 2 looks the same as an ordinary date, the war is not the explanation.
3. **Forecasts trained only on pre-war data.** We used three simple models, each tested chronologically on data it had not seen. Their March projections give a "what if nothing had changed" reference.
4. **A natural experiment for discounts.** Harbour ran the same promotion twice; Garden and Uptown did not. We compared Harbour with the other two branches before, during and after each wave. We then repeated the comparison for every 8-day window without a promotion (60 placebo windows) to measure normal noise.
5. **Customer cohorts.** We froze the pre-war customer list, then tracked where (which branch) and when (28 versus 56 days) those customers showed up again.
6. **Calendar regressions** as a cross-check: weekday effects, a trend term, and separate Ramadan, Lent and post-March-2 indicators, with robust (HAC) errors and five model specifications.

## 3. Data and quality checks (observed facts)

| Check | Result |
|---|---|
| Rows / orders / products | 51,177 item lines · 33,887 orders · 45 products · 3 branches (Harbour, Garden, Uptown) |
| Period | Jan 1–Jun 30, 2026: about 60 days before the war and 120 after |
| Accounting consistency | Revenue = qty × price × (1 − discount) to within $0.005 on every line; gross profit = revenue − cost exactly |
| Exact duplicate lines | 132 (0.26%). Kept. Removing them leaves order counts and forecasts unchanged and moves GP/order by < $0.02 ([duplicate_sensitivity.csv](reports/duplicate_sensitivity.csv)) |
| Missing Customer ID | 36.5% of orders, similar before and after (64.3% vs 63.4% identified) |
| Prices | Each product has **one list price per branch for the whole half-year**, so price changes appear only as discounts (10% or 15%) |
| Discount rates | 93.4% of lines at 0%, 5.6% at 10%, 1.0% at 15% |
| Transaction IDs | Replacement IDs (`SYN-…`), as the brief states |

Full details: [data_quality.json](reports/data_quality.json), [data/README.md](data/README.md).

---

## 4. Three conclusions, and what to do next time

Each conclusion lists **what we measured**, the **alternative explanations we tested**, **what Stories should do when this happens again**, and the **estimated value**. The value is always built on stated assumptions and kept separate from the measured results.

### Conclusion 1: Demand rose during the disruption, and its shape did not change. Scale the plan; don't redesign it.

**Measured:**
- Orders in the 28 days after March 2 were **+9.1%** above the 28 days before (4,611 → 5,030). The week of March 2 was **+12.8%** over the previous week. That is the biggest week-over-week jump in the half-year, but normal weekly changes vary by about 5.6%, and +12.8% is only about 2 standard deviations.
- **The rise is not unique to March 2.** The same 28-day comparison at 19 other dates gives **+5.9% to +10.7%** ([alternative_cutoff_comparisons.csv](reports/alternative_cutoff_comparisons.csv)). Stories was growing steadily all half-year, from about 143 orders/day in early January to about 225 in late June.
- **What customers bought, and when, did not change.** Evening share stayed at 50.0–51.0% across every phase. Takeaway share stayed at 39.7–41.3%, GP/order at $5.28–$5.32, and meal attachment to beverage orders at 2.0–2.4%. We found no Ramadan shift to evenings and no Lent shift in food choice.
- **The size of the change differed by branch.** Against forecasts trained only on pre-war data, the 28 days after March 2 came in at **Harbour +10.4%**, **Uptown +7.7%** and **Garden −2.2%** ([projection_summary.csv](reports/projection_summary.csv)). Garden's figure changes sign depending on the model (−2.2% to +5.1%); Harbour's (+5.3% to +12.0%) and Uptown's (+7.7% to +13.0%) do not ([projection_model_sensitivity.csv](reports/projection_model_sensitivity.csv)).
- **The models were compared with simple baselines on data they never saw.** For daily order forecasts we tested three candidates chronologically: previous same weekday, mean of the last four same weekdays, and trend plus weekday. The simplest rule, "same as last week", lost at every branch. 14-day MAE was 10.52 vs 9.87 orders/day at Harbour, 8.05 vs 6.26 at Garden, and 6.81 vs 4.35 at Uptown ([forecast_backtest_scores.csv](reports/forecast_backtest_scores.csv)). For food preparation, "mean of the last four same weekdays" beat "last week" on four months of out-of-sample data (Mar 2–Jun 30): Harbour bakery MAE fell from 7.52 to 5.49 units/day and meal MAE from 2.90 to 2.20 ([preparation_backtest.csv](reports/preparation_backtest.csv)).

**Alternative explanations tested:** We tested whether the increase was a war effect, a Ramadan effect or a Lent effect. In five regression specifications, the Ramadan estimate is +1.7% to +2.4% and the Lent estimate −3.7% to −1.6%, with every 95% interval including zero. The post-March-2 estimate is +3.4% to +6.6%, and four of the five intervals include zero ([calendar_adjusted_associations.csv](reports/calendar_adjusted_associations.csv)). Ramadan and Lent overlap so much that their indicators have a correlation of 0.72. Our reading is that the rise is mostly ongoing growth, with a possible extra step around March 2 that we cannot reliably separate from the trend.

**What to do next time:**
1. **Don't cut capacity or stock because of the headline.** Plan each branch from the last four same weekdays, which was the better rule in our test. Re-forecast weekly.
2. **Don't reshape hours or menu for Ramadan or Lent on assumption.** This data shows no evening or meal shift. Change hours only if daily monitoring shows the evening share moving.
3. **React at branch level.** Harbour and Uptown ran clearly above the pre-war forecast, while Garden's result depends on the model used. Changes to staffing and stock should be decided branch by branch, not chain-wide.

**Estimated value (conditional):** Say Stories had planned March from the pre-war forecast and every order above it had been lost to stock-outs or slow service. That would put at risk about 227 Harbour orders and 69 Uptown orders, roughly **$1,700 of recorded gross profit in 28 days** (orders × each branch's GP/order). This is an upper bound. We cannot see stock-outs or wait times, so we don't know how many of those orders a tighter plan would actually have lost.

### Conclusion 2: Discounting during the disruption did not buy traffic. It gave away margin.

**Measured:** Harbour ran **the same promotion twice**: 15% off every Cold Coffee and Desserts item (Iced Latte, Cold Brew, Iced Americano, Cheesecake, Brownie and others) on **Mar 12–19**, inside the war/Ramadan window, and again on **May 12–19**, with no calendar event. Garden and Uptown ran nothing comparable. The weekly discount spikes are visible in [promotions_and_cutoffs.png](reports/figures/promotions_and_cutoffs.png).

| Harbour, promoted categories | Mar 12–19 wave | May 12–19 wave |
|---|---:|---:|
| Promoted units/day: 14 days before → during | **30.1 → 30.1** | **37.6 → 37.6** |
| Same, relative to Garden + Uptown | +10.7% | −4.4% |
| Promoted-category gross profit/day, during vs average of before and after | $120 → $90 (**−25%**) | $147 → $111 (**−24%**) |
| Discount given away on promoted items | **$209.87** | **$261.68** |
| First-seen customer IDs among promoted-item buyers | 19 of 133 | 2 of 160 |

- **Break-even test.** At Harbour's prices and costs, 15% off cuts the gross profit on each promoted unit from $3.86 to $2.99. The promotion pays for itself only if units rise by **+29.3%** (+24% to +36% depending on the product).
- **Could a lift that large be hidden by noise?** No. We ran the same Harbour-versus-other-branches comparison on 60 eight-day windows with no promotion. 95% of them fall between **−21% and +16%**, and the largest is +22%. **None reaches +29%**, so a break-even lift would have shown up clearly. The observed results (+10.7% and −4.4%, about +3% on average) sit inside ordinary noise.
- Harbour's total orders relative to the other branches also showed no gain (+4.5% in March, −4.1% in May). The discount did not pull extra people through the door.

**Alternative explanations tested:** (a) *Calendar.* The May wave had no war onset, Ramadan or Lent overlap and gave the same result, so the outcome is not a calendar artefact. The March relative figure is somewhat flattered because Garden and Uptown dipped at the end of Ramadan; the raw Harbour units did not move. (b) *Chain-wide shocks.* Comparing Harbour against the two other branches removes shocks that hit all three. (c) *Customer acquisition.* Almost no first-seen customers bought the promoted items. (d) *Slower effects such as loyalty or later visits.* Not measured. This is the remaining reason Stories might still choose to run promotions.

**What to do next time:**
1. **Don't use blanket discounts as the reflex response to a shock.** In this data, customers kept coming without them.
2. **If a promotion is needed for other reasons (brand, competition), build in a test.** Run it at some branches or on some days and keep the others at full price. Agree beforehand that it must show at least the break-even lift (about +29% for 15% off).
3. **Prefer smaller or targeted offers.** At 10% off, break-even is about +18%; one product instead of two whole categories also limits what is given away.

**Value:** **Measured:** the two waves gave away **$471.55** of discount on promoted items, with no detectable gain in units or orders. **Estimated:** each 8-day wave Stories skips (or targets better) should keep roughly $210–260 of gross profit at Harbour at current volumes. This assumes volume would have been the same at full price, which the before/during comparison supports. If Stories runs such waves regularly, the saving grows proportionally. The dollar amounts are small because the dataset is small. The underlying finding, a 25% fall in profit on the promoted categories for no extra volume, carries over at any scale.

Evidence: [promotion_natural_experiment.csv](reports/promotion_natural_experiment.csv), [promotion_placebo.csv](reports/promotion_placebo.csv). Reproduce: `python3 scripts/promotion_test.py`.

### Conclusion 3: Customers weren't lost. Judge loss at chain level, over 56 days.

**Measured** (identified customers only; see weak areas):
- **More customers, not more visits each.** Active identified customers rose from **1,978 to 2,104 (+6.4%)**, while orders per customer rose only from 1.498 to 1.515 (+1.2%). About **84%** of the extra identified orders came from more customers rather than more frequent visits ([customer_growth_decomposition.csv](reports/customer_growth_decomposition.csv)).
- **Many "new" customers were returning ones.** Of 900 IDs seen after March 2 but not in the previous 28 days, **508 had bought earlier in the year**. They are returning customers, not new ones.
- **A short absence is not churn.** Of the 1,978 customers active before the war, 60.9% were seen again within 28 days and **85.5% within 56 days**. Of the 774 who were not seen in the first 28 days, **488 (63%) came back in days 29–56** ([customer_followup.csv](reports/customer_followup.csv)). The pattern is the same at other cutoff dates (for example, Jan 29: 56.7% within 28 days, 82.4% within 56), so it is how Stories customers normally behave, not something the war caused.
- **Customers use the whole chain.** Over the half-year, **93.8% of identified customers bought at two or more branches**. Of 426 pre-war Uptown customers who did not come back to Uptown, **216 (51%) bought at another Stories branch** (Garden 49%, Harbour 39%). The share is the same around the Ramadan start (51%) and the Lent start (49%), so it is routine, not war-driven relocation ([customer_branch_continuity.csv](reports/customer_branch_continuity.csv)).
- A fixed group of 584 repeat customers, chosen from data before both comparison windows, made 504 orders before and 513 after, with gross profit at $2,662 before and $2,657 after. Their habits stayed the same through the disruption ([customer_fixed_cohorts.csv](reports/customer_fixed_cohorts.csv)).

**Alternative explanations tested:** (a) *Regression to the mean.* The 584-customer group was chosen from earlier data, before both comparison windows, and members with zero later visits stay in the count. (b) *Longer windows mechanically show more returns.* True. The finding is not that "56 days is better". It is that a 28-day rule would label 774 customers as lost when 488 of them were seen again weeks later. (c) *Missing IDs.* A customer may have bought without their ID being recorded. That would only make the real return rates higher.

**What to do next time:**
1. **Measure customer loss across the whole chain.** A customer who is missing from Uptown but buying at Harbour has not been lost. Branch-only "lost customer" lists would wrongly include about half of Uptown's names.
2. **Wait 56 days before treating someone as lost.** Any win-back offer sent at 28 days would mostly go to customers who were about to come back anyway.
3. **Put retention effort into turning the new wave of visitors into regulars.** Growth came from more people, not more visits each. This is a better use of the money than discounts to existing customers, who kept coming anyway (Conclusion 2).

**Estimated value (conditional):** Say Stories sent a win-back offer worth $1 at the 28-day mark. About **488** of the offers would go to customers who were seen again within 56 days anyway, up to **$488 per cycle** of incentive with no clear gain (plus 216 Uptown contacts to customers active at another branch). If a retention effort got just 1% of the 1,978 baseline customers to make one extra order, it would add about **$103 of gross profit** (at the observed $5.22 per identified order), before costs. These response rates are assumptions, not measurements.

---

## 5. Weak areas, uncertainty and possible failures

| Weakness | Why it matters | Effect on our conclusions |
|---|---|---|
| **Ramadan, Lent and the war overlap; there is one season and no comparison year** | We cannot say how much of any change belongs to which event | We claim only what changed during the combined period, not causes. All three conclusions concern decisions, not attribution |
| **Strong underlying growth** | Any before/after comparison partly reflects the trend | Conclusion 1 explicitly says the rise is mostly trend. Every alternative cutoff shows similar growth |
| **No control branch** | All three branches were exposed to the same events | For promotions, Garden and Uptown act as the comparison only because they ran no promotion. A shock that hit only Harbour during the promo weeks would bias the result |
| **Only two promotion waves, both at one branch, both the same design** | Two consistent results are not proof for other branches, depths or products | The recommendation is a holdout test, not a ban. Garden and Uptown customers might respond differently |
| **36.5% of orders have no Customer ID** | Customer findings cover identified accounts only; missing IDs may not be random | Return rates are probably understated. If the share of IDs captured changed over time, cohort comparisons could be biased |
| **Customer IDs assumed stable and shared across branches** | Cross-branch findings depend on it | If IDs differ between branches, the 94% multi-branch figure is an artefact. Verify with the loyalty system |
| **Signs the data may be synthetic or sampled** | "SYN-" IDs, one fixed price per product, 94% of customers using several branches, very stable shares | Patterns may be cleaner than in real operations. Dollar amounts reflect the dataset's size and should not be read as company totals |
| **Gross profit excludes labour, rent, waste and stock-outs** | Profit here is recorded revenue minus recorded product cost | Value estimates are gross-profit estimates. Missed demand from stock-outs (Conclusion 1) is invisible |
| **No opening hours, stock-outs, wait times or marketing calendar** | Low sales could mean closed, sold out or low demand | Forecasts predict recorded sales, not true demand |
| **Short forecasting history** | Only about 60 pre-war days: three overlapping 14-day test folds and one 28-day fold | Forecast errors are rough development estimates, not guaranteed accuracy. The bands in [demand_projection.png](reports/figures/demand_projection.png) are not calibrated intervals |
| **Many comparisons** | Windows, branches and models multiply the chance of finding something | We report full tables and model ranges, not the most favourable result, and we built conclusions only on patterns that repeat across windows or cutoffs |

**Where the recommendations could be wrong.** Conclusion 2 fails if the promotions were meant to build long-term loyalty. That effect would appear in later visits, which we did not measure. Conclusion 1 fails if a future shock does reduce demand: the "scale to recent demand" rule handles both directions, but only if Stories forecasts weekly. Conclusion 3 fails if the IDs are not consistent across branches.

## 6. Practical tests Stories can run before wider use

| Test | Design | Success criterion agreed in advance |
|---|---|---|
| **Promotion holdout** (Conclusion 2) | Next planned promotion: randomise days (or branches) into promo and full price over 4+ weeks, so both groups face the same calendar | Gross profit per day in promoted categories, including any extra items bought. Expand only if units rise by at least the break-even amount (+29% at 15% off) |
| **Win-back timing** (Conclusion 3) | Customers absent from the whole chain for 28 days: randomise into "contact at day 28" or "contact at day 56 only if still absent". Follow everyone for 56 days | Chain-wide gross profit per assigned customer minus offer costs. Count every assigned customer, including those who never return |
| **Recent-demand preparation** (Conclusion 1) | At one branch for 4 weeks: prepare from the 4-week same-weekday average, and log waste and stock-out times | Waste units, stock-out hours and sales compared with the previous rule at a similar branch |
| **Data fixes (no cost)** | Log opening hours, stock-outs and promotion dates; confirm IDs are the same across branches; push for more orders with an ID | Makes all three conclusions measurable next time |

## 7. Assumptions (kept separate from facts)

| Assumption | Source | If wrong |
|---|---|---|
| War-context cutoff = **March 2, 2026** | Team context (not detected from the data) | The alternative cutoffs show the conclusions don't depend on this exact date |
| Ramadan **Feb 17–Mar 18**, Lent **Feb 18–Apr 2**, inclusive | Team-supplied calendar | Small shifts of a day or two change the phase table slightly but not the conclusions |
| Calendar periods describe the calendar, not customers | Nobody's religion or fasting is known | We make no claims about who observes what |
| Recorded unit cost is the right cost for gross profit | Data dictionary | Break-even lift and dollar values scale with true margins |
| Harbour's discounts on Mar 12–19 and May 12–19 were planned promotions | 15% applied to every promoted-category unit, at Harbour only | If they were system errors, the recommendation becomes "fix the discount configuration", which is still a profit gain |
| Promoted volume would have been the same without the discount | Before = during in both waves | If the discount prevented a fall, savings are overstated. The 60 placebo windows make a hidden fall of more than about 20% unlikely |
| A missing Customer ID is unknown, not one anonymous customer | Our method choice | Customer counts cover identified accounts only |
| Exact duplicate lines are real sales | Meaning unknown | Removing them changes nothing material |

## 8. Approaches we considered and rejected

- **Estimating "the cost of the war".** Without a comparison year or an unaffected branch, any such number would be invented. We quantified decisions instead.
- **Complex ML forecasting.** About 60 days of history cannot support it. Simple weekday-based models were tested chronologically against even simpler rules, and the four-week weekday average is enough to make the decision.
- **Making Garden's low margin the headline.** Garden's recorded margin (about 47% vs Harbour's 65%) is real but **stable in every phase** (46.8–47.2%), so it is not a response to the disruption. It is a separate cost-recording or procurement question ([same_product_economics.csv](reports/same_product_economics.csv): Garden's costs for the same products are about 43% higher).
- **A Ramadan/Lent menu or hours redesign.** No evening or meal shift appears in the data, and the menu categories do not tell us what is suitable for fasting.
- **Basket-pairing offers ("croissant with latte").** Past co-purchases cannot show whether a suggestion creates extra sales. That needs a randomised test, sketched in [docs/food_offer_pilot.md](docs/food_offer_pilot.md).
- **A churn or lifetime-value model.** Coffee customers never cancel, so "churn" is never directly observed. Transparent cohort tracking answers the 28- versus 56-day question directly.
- **A "chat with your sales data" dashboard.** The brief rules this out, and it would not support a decision.

---

## 9. Repository guide

| Path | What it contains |
|---|---|
| `README.md` | This document: the final submission |
| `scripts/promotion_test.py` | Harbour promotion natural experiment, break-even and placebo windows (Conclusion 2) |
| `src/stories/analysis.py` | Main pipeline: data quality, matched windows, forecasting backtests, preparation backtest, figures |
| `src/stories/calendar.py` | Phase table, boundary comparisons, calendar regressions (Conclusion 1) |
| `src/stories/customers.py` | Customer growth breakdown, fixed groups, cross-branch tracking, 28/56-day follow-up (Conclusion 3) |
| `src/stories/business.py`, `diagnostics.py`, `scenario.py` | Item/branch economics, alternative cutoffs, same-product costs, scenario arithmetic |
| `reports/*.csv`, `reports/figures/*.png` | Every number cited above |
| `notebooks/stories_decision_analysis.ipynb` | Executed notebook covering the pipeline outputs |
| `notebooks/reference/` | Original exploratory notebooks (EDA and before/after) |
| `reports/*_memo.md`, `docs/*.md` | Earlier working memos and detailed method notes (supporting material) |
| `tests/` | 18 unit tests for the analysis code |

**Key figures:** [calendar_timeline.png](reports/figures/calendar_timeline.png) (orders, evening share and GP/order across the calendar) · [promotions_and_cutoffs.png](reports/figures/promotions_and_cutoffs.png) (Harbour discount waves and alternative cutoffs) · [demand_projection.png](reports/figures/demand_projection.png) (pre-war forecast vs actual).

### Reproduce

Python 3.10+ (verified on 3.13). The transaction CSV is not committed; place the supplied file at `data/raw/stories_transactions.csv` (SHA-256 `f1672e72…7a1`) or pass `--data`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python3 -m stories.analysis     # regenerates reports/ and reports/figures/
python3 scripts/promotion_test.py              # Conclusion 2 evidence
python3 -m pytest -q                           # 18 tests
```
