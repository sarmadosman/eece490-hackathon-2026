# Customer-level methods and limitations

The primary business questions concern observed audience breadth, repeat behavior, cross-branch continuity, and the timing of observed return. The analysis is descriptive and operational; it does not fit a churn, lifetime-value, or causal response model.

## Population and grain

One transaction is one order. Item rows are grouped before customer analysis, and conflicting IDs within one transaction cause an error. A customer-day is one distinct Customer ID/date pair; multiple orders that day still count as one customer-day. Calling a customer-day a physical visit is an approximation: the file does not identify visits, shared accounts, or separate same-day outings.

There are 21,534 identified orders among 33,887 orders, with 3,494 distinct observed IDs. Missing IDs are excluded from distinct-customer and matched-account calculations, retained in coverage denominators, and never grouped as an anonymous customer. Coverage is computed by period and branch. Similar coverage does not establish random missingness or representativeness; inference to all customers is unsupported. IDs must be stable and globally consistent across branches; this is assumed from the schema, not verified against the source system.

## Event windows and calendar overlap

Use the user-supplied dates: March 2 war-context cutoff, Ramadan February 17–March 18, Lent February 18–April 2, inclusive. Compare equal 14-/28-day windows around March 2 and the starts/ends of Ramadan/Lent. Equal weekday exposure does not control all seasonality, promotions, or changes in ID capture. Alternative-cutoff checks are overlapping descriptive comparisons, not independent replications. Their recurrence weakens a uniquely disruption-specific interpretation.

The main comparison is February 2–March 1 versus March 2–29. Before/after identified-customer counts refer to distinct observed accounts in each complete window. They do not estimate the number of all actual customers or demonstrate true acquisition.

## Breadth and frequency

Let N be active identified accounts and F be identified orders per active account. Identified orders O = N × F. The symmetric accounting decomposition is:

`breadth component = (N_after − N_before) × (F_before + F_after) / 2`

`frequency component = (F_after − F_before) × (N_before + N_after) / 2`

The two components sum exactly to the identified-order difference. This is not attribution to marketing, war, or any intervention. Shares can be negative or exceed 100% when components offset and are undefined when total change is zero. Both order frequency and distinct customer-day frequency are reported.

Window-flow segments distinguish accounts seen in both windows, before only, or after only. For after-only IDs, a separate check asks whether they were observed earlier in the file, before the pre-window. This distinguishes reappearance from first observation in the available file; first observation remains left-censored and does not establish a first-ever purchase.

## Independently fixed repeat cohorts

For a width w and event date t, calibration uses [t−2w, t−w−1], the pre-window [t−w, t−1], and the post-window [t, t+w−1]. All are full calendar-day windows. Cases without complete calibration/pre/post coverage are skipped. Membership uses at least 1, 2, or 3 distinct recorded calibration customer-days; all qualifying IDs remain in both comparison denominators even if they make no later order.

The main repeat-account definition uses at least two distinct days in January 5–February 1: 584 IDs. Frequency and contribution are divided by all 584, not only returning accounts. Membership is not chosen from the outcome windows, avoiding the obvious regression-to-the-mean error of selecting frequent pre-period shoppers and describing their later fall as disruption-induced attrition. Threshold sensitivity is shown; none defines verified loyalty or causality. No formal significance or universal flat-cohort claim is made.

## Cross-branch continuity

For each branch, take IDs observed there in the pre-window. The post-window categories are disjoint: observed at the same branch (possibly also elsewhere), observed only at other branches, or not observed anywhere. The sum equals that branch's baseline cohort. Apparent branch absence is other-branch-only plus chain-unobserved; its elsewhere share quantifies how much local absence coexists with observed chain activity.

An ID can be in several baseline branch cohorts; their rows and gross-profit sums must not be added as unique people or unique chain opportunity. Cross-branch continuity does not establish relocation, travel, branch preference, or war-induced migration. This pattern may reflect routine multi-branch behavior.

## Follow-up and nonreturn

At each cutoff, freeze accounts observed during the prior 28 days. Count how many are observed again over the following 28 and 56 complete days. Skip a horizon if its end exceeds the data's calendar coverage. Zero observed returns are not silently imputed for incomplete horizons. The same fixed cohort and nested horizons make return rates mechanically nondecreasing; the policy-relevant result is how many short-window absent IDs later appear, not a claim that observing longer improves true retention.

These are cutoff-based cohort windows. They are not an individual last-visit-indexed churn risk set: baseline accounts can have different recency at the cutoff. An operational policy based on days since each account's last identified visit must be constructed and validated separately.

At March 2, the 56-day endpoint is April 26. Accounts absent during March 2–29 but appearing during March 30–April 26 are late observed returns relative to that rule. They may have purchased anonymously earlier, and historical promotions or service may already have affected their return. They are not proven organic returns or evidence that outreach is unnecessary.

Permanent attrition is not directly observed in a noncontractual transaction record. This distinction is discussed in the primary [Fader, Hardie, and Shang customer-base research](https://www.brucehardie.com/papers/020/). We use transparent cohort comparisons rather than treating a fixed inactivity threshold as verified churn. A formal customer model would require its own assumptions, temporal validation, and capture checks.

## Conditional economics and validation

One-extra-order scenarios assume an extra 1%, 2%, or 5% of the 1,978 baseline IDs generate one additional order at the observed post-window identified-order mean gross contribution. The response rates are unmeasured; substitution, intervention, labor, and other incremental costs must be assessed separately.

Avoided-contact scenarios assume an existing branch-loss policy with an avoidable $0.25/$0.50/$1 cost per account already observed elsewhere. These are hypothetical costs, not verified operations or savings. If there is no such policy the scenario is inapplicable. No messages were sent. Do not aggregate overlapping branch opportunities.

Evaluate any chosen continuity or inactivity policy with assignment fixed before treatment, a concurrent control, customer-level analysis including zero outcomes, and the same complete follow-up for both arms. The data alone do not establish an optimal outreach date, acquisition channel, treatment response, or full net-profit improvement.
