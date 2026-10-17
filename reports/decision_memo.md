# Customer continuity: three less obvious business arguments

**Problem:** How can Stories apply changes to maximize profit in times of abrupt change?

Investigate customer behavior rather than centering the submission on branch margins or discounts. The evidence supports separating observed audience growth from repeat frequency, checking chain-wide continuity before calling a branch customer lost, and testing the timing of inactivity decisions. These patterns concern operational interpretation and customer-service policy; no causal war effect or customer-response uplift has been established.

## Population and comparisons

The supplied data contain 33,887 orders, 21,534 with Customer ID, and 3,494 distinct observed IDs over January–June. Approximately 36.5% of orders have no ID. We do not infer the number of unique anonymous customers. IDs are assumed to represent persistent accounts across branches; this must be verified with the source system.

The main windows are February 2–March 1 and March 2–29: equal 28-day periods with matching weekday exposure. Ramadan and Lent overlap them differently. Customer tables also compare 14-day windows and Ramadan/Lent starts and ends. Customer-ID coverage is 64.3% before and 63.4% after. Similar coverage does not establish unbiased or representative capture.

[Window metrics](customer_window_summary.csv), [calendar exposure](event_window_calendar_exposure.csv), [customer methods](../docs/customer_methodology.md).

## Pattern 1: growing traffic can conceal modest repeat-cohort change

| Measure | Before | After |
|---|---:|---:|
| All orders | 4,611 | 5,030 |
| Identified orders | 2,963 | 3,188 |
| Distinct active identified accounts | 1,978 | 2,104 |
| Orders per active identified account | 1.498 | 1.515 |
| Distinct customer-days per active account | 1.465 | 1.484 |

The audience increases 6.4%, while order frequency per active account increases about 1.2%. The exact symmetric accounting decomposition assigns approximately 189.8 of the 225 extra identified orders (84.4%) to the audience-breadth component and 35.2 (15.6%) to the frequency component. This does not identify causes or attribute marketing success.

A second distinction matters: 900 IDs appear after but not in the preceding 28-day window. **508 already appeared earlier in the file**. The remaining 392 are first observed in this limited history, not proven new customers. Reporting all 900 as acquisition would conflate reappearance with first observation.

For an independent repeat-cohort check, freeze 584 accounts with at least two distinct recorded visit-days during January 5–February 1, before the comparison windows. Include all 584 in both windows, including zero-visit members. They record 504 → 513 orders, 488 → 504 customer-days, and $2,662.27 → $2,656.57 recorded gross profit. This is modest order change and essentially flat observed contribution under that definition, not a proven loyalty deterioration. Other calibration thresholds are exported and differ; no threshold was optimized for significance.

**Business argument:** traffic growth alone is insufficient evidence that existing customers are buying more habitually or that customer acquisition is succeeding. Separate audience breadth, reactivation, and fixed-cohort frequency before allocating customer-service or marketing effort. Measure the actual bottleneck instead of treating every newly active ID as a new customer.

**Test and conditional value:** if 1% of the 1,978 baseline identified accounts made one genuinely additional order at the observed post-window mean identified-order contribution, the conditional gross contribution would be about $103.15 before intervention and other incremental costs. That uplift is an assumption, not a forecast. Randomize any repeat-visit/service intervention and evaluate all assigned customers, including zero visits, over a fixed period.

Evidence: [decomposition](customer_growth_decomposition.csv), [window flows](customer_window_flows.csv), [independently fixed cohorts](customer_fixed_cohorts.csv), [conditional scenarios](business_value_scenarios.csv).

## Pattern 2: branch absence can be continued business elsewhere

| Baseline branch cohort | Accounts before | Seen at same branch afterward | Seen only at other branches afterward | Not observed anywhere afterward |
|---|---:|---:|---:|---:|
| Garden | 864 | 242 | 306 | 316 |
| Harbour | 1,166 | 405 | 296 | 465 |
| Uptown | 507 | 81 | 216 | 210 |

For Uptown, 426 previously active accounts do not appear there in the post-window. Of those, 216—**50.7%**—are observed elsewhere in the chain. This is a customer-continuity pattern, not a branch-margin diagnosis. It does not prove relocation, a new preferred branch, or a war-driven switch; routine multi-branch use and other cutoffs must be considered.

**Business argument:** a branch-only loss-recovery list would include accounts still doing business with Stories. Evaluate customer continuity across the chain before treating a local absence as loss. Test branch-independent recognition, account continuity, availability information, or service routing where operationally appropriate.

**Economics and test:** under a hypothetical existing branch-loss contact policy costing $0.50 per contact, suppressing one loss-recovery contact for each of the 216 Uptown accounts already observed elsewhere would avoid $108 of assumed cost. No current policy, contact cost, or realized saving is known. Randomize the service/routing process against current practice, and measure chain-wide incremental contribution after costs; do not count branch transfer as new chain revenue.

A customer can belong to more than one baseline branch cohort. Do not sum rows as unique people or sum their gross-profit amounts as a chain-wide opportunity. Confirm globally consistent customer IDs before using cross-branch matches.

Evidence: [branch-continuity partitions and alternative boundaries](customer_branch_continuity.csv).

## Pattern 3: a short absence is not permanent customer loss

Follow the **same 1,978 accounts** active in the pre-window:

| Complete follow-up after March 2 | Observed again | Not observed | Observed return rate |
|---|---:|---:|---:|
| 28 days, through March 29 | 1,204 | 774 | 60.9% |
| 56 days, through April 26 | 1,692 | 286 | 85.5% |

Of the 774 initially unobserved accounts, **488 (63.0%)** are observed during days 29–56. A longer horizon mechanically allows more returns; the practical finding is that a large group labelled absent by a short rule subsequently appears. Missing IDs can also hide actual visits. We have not established whether late returns happened without existing marketing or service interventions.

**Business argument:** compare staged inactivity/service policies instead of interpreting a 28-day absence as permanent churn. A coffee business has no directly observed cancellation event, so observed nonreturn and actual customer loss are distinct. This distinction is standard in [noncontractual customer-base research](https://www.brucehardie.com/papers/020/).

**Test:** compare an existing short-horizon policy with an alternative staged policy using randomized timing and the same full 56-day outcome horizon. Track chain-wide contribution per assigned account, actual contact/service costs, and earlier/later return. Do not assume waiting 56 days is optimal; some high-value customers might benefit from earlier service. Complete follow-up and a control are required before claiming avoided cost or recovered revenue.

The same broad short-/long-horizon difference appears at alternative dates; it is not uniquely associated with war. [Follow-up evidence](customer_followup.csv).

## What these results do not establish

- No overall identified-customer decline is observed in the main comparison; the active count increases.
- No exact war/Ramadan/Lent effect or event-specific relocation is identified.
- Missing IDs are not known to be random, and observed late return is not proof of an unprompted return.
- The fixed cohort is an observed repeat-account definition, not a verified loyalty segment. Zero-visit members remain in its denominator.
- Conditional economics do not establish actual uplift, contact savings, or full net profit.

## Recommendation

Build the submission around customer continuity during changing conditions: distinguish which accounts are active, where they are active, and over what time horizon before choosing a profit-oriented response. Present the breadth/frequency and cross-branch findings as the primary operational arguments, with delayed return strengthening the case for a better inactivity policy. Validate with the [customer-service plans](../docs/pilot.md). Earlier item/branch analyses are preserved in [supporting material](item_branch_memo.md), not used as the main story.
