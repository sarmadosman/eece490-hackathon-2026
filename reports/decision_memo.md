# Three conclusions for the abrupt-change playbook

**Business problem:** How can Stories apply changes to maximize profit in times of abrupt change?

The existing argument is retained: use observed demand to guide preparation, assess promotions through their total contribution, and evaluate customer continuity and intervention timing. These refinements separate observation from causal effect and conditional economics. Garden's margin/cost investigation remains supporting material.

## Conclusion 1: Recorded orders increased, while selected aggregate trading measures remained broadly similar.

**Measured:** the 28 days after March 2 recorded 5,030 orders versus 4,611 in the preceding 28 days (+9.1%). Across the multi-day phases, evening share ranged from 50.0% to 51.0%, takeaway share from 39.7% to 41.3%, recorded gross profit per order from $5.28 to $5.32, and meal attachment from approximately 2.0% to 2.4%. These aggregates do not establish equivalence, exclude branch/product changes, or rule out calendar effects.

Similar increases at other cutoffs weaken the interpretation that the observed growth uniquely marks March 2; they do not rule out conflict-related effects. Ramadan and Lent overlap the cutoff, and model-dependent calendar associations do not provide a reliable causal decomposition.

**Decision and validation:** test a recent matching-weekday preparation rule at each branch while logging waste, stockouts, availability, service, and incremental operating costs. At Harbour, the prior-four-matching-weekdays rule reduces historical bakery-unit MAE from 7.52 to 5.49 and meal-unit MAE from 2.90 to 2.20 relative to the previous-weekday rule. Forecast accuracy is not measured waste savings or proof of an optimal stock level. The pre-cutoff projection is calendar-unadjusted, with uncalibrated historical-error bands. Define a material operating threshold and show uncertainty excludes it before concluding no material change.

Evidence: [phase metrics](calendar_phase_summary.csv), [alternative cutoffs](alternative_cutoff_comparisons.csv), [forecast backtests](forecast_backtest_scores.csv), [preparation backtest](preparation_backtest.csv).

**Figure — demand and overlap:** [calendar_timeline.png](figures/calendar_timeline.png) shows increasing recorded orders alongside selected aggregate measures. Compare their trajectories without treating broad similarity as equivalence.

## Conclusion 2: The observed promotion results do not establish that the discounts paid for themselves.

Harbour has two recorded 15%-off Cold Coffee/Desserts windows, March 12–19 and May 12–19. The observational promotion comparison reports promoted units/day of 30.1 before and during the March window, and 37.6 before and during the May window. Relative branch comparisons are +10.7% and −4.4%. The comparison adjusts for common movements if the branches would otherwise have followed comparable relative trends. It does not identify the no-promotion counterfactual. First-observed IDs among promoted-item buyers do not establish incremental customer acquisition.

**Uncertainty:** the 60 overlapping non-promotion windows produced relative changes with a central 95% range of approximately −21% to +16%. The observed promotion comparisons, +10.7% and −4.4%, lie within this background variation. This does not establish zero effect or rule out a break-even effect: negative background variation can mask positive promotion effects. These overlapping windows are descriptive sensitivity checks, not independent experiments or a calibrated power analysis.

**Measured:** the two promotion windows recorded $471.55 in discounts relative to listed prices. This is not a measured causal profit loss: the quantities customers would have purchased without the promotion are unknown. **Conditional scenario:** holding quantities and product mix unchanged, charging full listed prices would have increased recorded gross profit by $471.55. Ordinary discounts, changes in demand, substitution, and later purchases could reduce or reverse that difference. We recommend a randomized holdout before repeating the promotion.

**Success criterion:** expand only if the randomized comparison shows a pre-agreed worthwhile improvement in total branch gross contribution after discounts and incremental operating costs. Report promoted-category units and the approximately 29% same-mix break-even benchmark as supporting measures. Include gains or losses elsewhere in the basket. The background comparisons do not establish the unobserved promotion-period counterfactual.

Evidence: [promotion comparison](promotion_natural_experiment.csv), [overlapping background comparisons](promotion_placebo.csv). The historical CSV filename is retained for compatibility and does not imply causal identification. Reproduce with `python3 scripts/promotion_test.py --data /path/to/stories_transactions.csv`.

**Figure — observational promotion comparison:**

![Recorded promotion volumes, contribution, and overlapping background variation](figures/promotion_comparison.png)

The first two panels show raw before/during/after means; the third shows descriptive background relative changes. The graphic does not identify the unobserved counterfactual or provide a calibrated power test.

## Conclusion 3: Check chain-wide activity and test inactivity thresholds before targeting customers.

Among the 1,978 identified accounts active in the baseline window, 1,692 were observed again within 56 days and 286 were not observed. These are observed-account return measures, not estimates of permanent customer loss.

Among baseline accounts not observed again at their original branch during the next 28 days, the share observed elsewhere was 49.2% for Garden, 38.9% for Harbour, and 50.7% for Uptown. Branch cohorts overlap and must not be summed as unique customers. Customer findings cover identified accounts only; 36.5% of orders lack IDs. Cross-branch results assume globally consistent IDs.

Of 774 baseline accounts unobserved during the first 28-day follow-up, 488 appeared during days 29–56. Their returns may already have been influenced by existing activity or interventions. This count does not measure avoidable incentives or prove that earlier contact would be ineffective.

Active identified accounts increase from 1,978 to 2,104, with identified orders per active account 1.498 → 1.515. Of 900 IDs observed in the second window but absent in the preceding one, 508 were previously observed earlier in the file; the others are first observed in the available history, not verified acquisitions. Fixed-cohort totals are descriptive and do not establish unchanged individual habits.

**Test intervention timing.** Compare contacting accounts after 28 days without an identified chain-wide purchase with contacting them after 56 days if they remain inactive. Historical returns do not establish which timing produces higher incremental contribution.

**Trial clock:** eligibility begins 28 days after each account’s last recorded chain-wide purchase. Randomize eligible accounts to contact immediately or wait another 28 days and contact only if still inactive. Evaluate both groups for 56 days from randomization, retaining every assigned account in the denominator. The historical fixed-window cohort is useful evidence; it is not itself an exact “days since last purchase” eligibility calculation.

**Conditional economics:** one genuinely additional order from 1% of baseline identified accounts would contribute about $103 before intervention and other incremental costs, using the observed identified-order mean contribution. This is an assumed response, not a measured improvement. Do not price the 488 historical later returns as avoided incentives.

Evidence: [coverage and account metrics](customer_window_summary.csv), [window flows](customer_window_flows.csv), [cross-branch activity](customer_branch_continuity.csv), [observed return](customer_followup.csv), [customer methods](../docs/customer_methodology.md).

**Figures — customer continuity:** [branch activity partitions](figures/customer_branch_continuity.png) distinguish local absence from chain-wide non-observation; [complete follow-up](figures/customer_followup.png) contrasts observed return horizons and alternative cutoffs. Neither figure selects a profitable contact threshold.

## Practical tests and supporting work

Use the [pilot plans](../docs/pilot.md) for preparation, promotion holdout, and precisely timed customer contact. Measure total contribution after relevant incremental costs and retain assigned units/accounts in the analysis. No pilot or campaign has been run.

Earlier [food-offer](food_offer_memo.md) and [item/branch](item_branch_memo.md) investigations are supporting material, not a change to the main three-part idea. The [executed notebook](../notebooks/stories_decision_analysis.ipynb) reproduces all three conclusions and embeds the promotion script for standalone use.
