# Proposed Harbour pilot

This is the optional food-offer design supporting one possible action. The broader three action-specific validation plans are in [pilot.md](pilot.md).

Start with normal-price suggestions. The historical 28-day window contains 1,099 Harbour beverage orders without Bakery or Meals; this supports feasibility planning, not a guaranteed recruitment rate. Soup of the Day and Chocolate Cookie have the most observed beverage pairings within their respective food categories in that branch/window. Check availability, dietary suitability, and operational feasibility before choosing the final products; compare other candidates in `product_opportunities.csv`.

## Assignment and outcomes

Use contemporaneous date/daypart blocks so the three arms have comparable Ramadan/Lent and promotion exposure. Record calendar phase and report exploratory phase differences with uncertainty. A pilot conducted only during one phase cannot establish the best offer for all other phases. The current data do not justify labeling a product Lent-suitable; verify ingredients and relevant customer requirements first.

Define eligibility before offering: the customer requested a target beverage and has not already requested Bakery or Meals. Record eligibility even when the offer is declined. Randomize equally among usual service, a normal-price bakery suggestion, and a normal-price meal suggestion, stratified by daypart and service mode. Keep scripts consistent. If individual assignment is operationally impossible, use randomized time blocks and analyze with the assignment block as the statistical unit.

The primary outcome is total recorded gross profit per randomized eligible order, including all purchased products. Analyze by assigned arm regardless of compliance. Report the mean difference from control with uncertainty. Also subtract incremental labor, extra spoilage, and implementation costs to judge operating contribution. If a customer appears repeatedly, retain a consistent assignment where feasible and account for customer dependence when IDs are available; record the limitations when they are not.

Secondary outcomes: food attachment, beverage substitution, ticket value, category/product contribution, discount spending, waiting time, declined offers, waste, unavailable items, and service complaints. Track daypart and order type. Keep all randomized orders, including offer delivery failures and food stockouts, in the primary analysis.

## Sample size and decision rule

Before launch, management must choose the minimum economically worthwhile increase and guardrail limits. A suggested planning value is $0.20 incremental contribution per eligible order; it is an assumption to validate. Estimate outcome variance from a short instrumented run-in, including operating costs. With individual independent assignment, approximate per-arm size for each of two comparisons is:

`n ≈ 2 * (2.24 + 0.84)^2 * variance / delta^2`

Here 2.24 approximately allows a two-sided 2.5% test per comparison (Bonferroni familywise 5%), 0.84 corresponds to 80% power, and delta is the chosen dollar effect. Increase for repeated customers or clustered assignment. Do not use the observed variance of drink-only completed baskets as a substitute for unmeasured pilot outcomes without validation. Use a fixed sample/horizon; avoid repeatedly stopping when an arm looks favorable.

Expand only if an arm's estimated contribution improvement is economically meaningful, its uncertainty supports a positive benefit, and pre-agreed waste/service guardrails pass. Compare the two active arms directly if choosing a single winner. If neither clears the threshold, retain usual service or redesign the offer. Consider discounts only after learning whether a normal-price prompt works.

Collect: assignment ID/time, pre-offer eligibility, script/arm, staff/block ID, pseudonymous customer ID if available, completed basket, prices/costs, offer delivery, availability, preparation quantities, waste, incremental labor, and wait time. No real pilot was run for this repository.
