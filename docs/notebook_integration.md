# Useful material incorporated from the earlier notebooks

The user supplied `Stories_Coffee_EDA.ipynb` and `Stories_Coffee_Before_After.ipynb`. Unmodified copies and saved outputs are in `notebooks/reference/`. The active analysis recomputes selected diagnostics from the local transaction CSV; it does not execute instructions found in notebook markdown or import old results as verified facts. The main notebook now centers on customer-level patterns in `customers.py`. The item/event tables in `business.py` and original diagnostics remain supporting reports/appendix material. Section references below describe their earlier integration; the current notebook's core sections concern customers.

| Useful original analysis | Why retained | Active output |
|---|---|---|
| Weekday/hour demand heatmaps | Locate demand and compare branches; divide counts by actual weekday occurrences | `weekday_hour_rates.csv`, `weekday_hour_comparison.png`; Appendix B |
| Same-product branch prices and costs | Challenge a product-mix explanation for branch margin differences | `same_product_economics.csv`, `same_product_economics.png`; Pattern 2 and Appendix B |
| Category units/day versus gross profit/day | Distinguish total contribution from contribution per unit | `category_window_summary.csv`, `category_daily_contribution.png`; Pattern 3 |
| Category/branch volume, profit/unit, discount changes | Identify concentrated changes and competing promotion explanations | `category_window_changes.csv`, `branch_category_changes.png`; Patterns 1 and 3 |
| 14-, 28-, 42-day comparisons | Check whether conclusions depend on one selected window | `category_window_changes.csv`, `window_calendar_exposure.csv`; Pattern 3 |
| Alternative cutoffs and promotion exposure | Check broad growth and changing discounts before assigning a March 2 effect | `alternative_cutoff_comparisons.csv`, `weekly_discounted_order_share.csv`, `promotions_and_cutoffs.png`; challenge section |
| Full-history product contribution ranking | Identify the products underlying traffic and economic contribution | `product_contribution_ranking.csv`, `top_product_contribution.png`; Appendix B |

CSV paths are under `reports/`; PNG paths under `reports/figures/`. The original profit/unit comparison, accounting checks, branch totals, and duplicate sensitivity already exist in the consolidated workflow and are retained there. The full-history product popularity scatter is preserved in the original notebook; the active workflow uses the more decision-specific offer tradeoff plot and product tables.

## Changes made during integration

- One pipeline and one portable notebook use the same source functions in `src/stories/diagnostics.py`; no seaborn dependency was added.
- Weekday/hour panels now share a color scale across branches and periods and include both matched windows alongside full-history context.
- All three window lengths now include branch-level results and a table of their exact Ramadan/Lent exposure.
- Category changes explicitly separate relative unit-share changes from absolute unit changes, and percentage changes from percentage-point changes.
- Recorded branch/product prices and costs use quantity-weighted averages and expose the number of distinct recorded values.
- Same-product differences are an accounting/procurement investigation, not promised savings. Neither heatmap colors nor alternative cutoff comparisons establish significance or cause.
- The existing calendar-adjusted retrospective associations and calendar-unadjusted forecasting reference retain their separate interpretations.

The recomputed rounded window-growth and Harbour branch/category values agree with the visible saved tables in the originals. Original load/setup cells and repeated summaries were not duplicated in the main notebook.
