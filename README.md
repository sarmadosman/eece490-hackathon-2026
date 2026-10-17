# Stories Coffee: customer continuity during abrupt changes

**Business problem: “How can Stories apply changes to maximize profit in times of abrupt change?”**

The primary investigation now looks for customer-level patterns in pre/post war-context, Ramadan, and Lent comparisons. It focuses on **audience breadth versus repeat frequency**, **cross-branch continuity**, and **delayed observed return**. The earlier branch-margin and discount analyses are supporting material, not the main story.

## Three current arguments

| Pattern | Measured result in the matched March 2 windows | Decision to investigate |
|---|---|---|
| More traffic does not necessarily mean stronger repeat habits | Active identified customers 1,978 → 2,104; orders/active customer 1.498 → 1.515; about 84.4% of the identified-order increase is the audience-breadth component | Separate audience/reactivation and repeat-frequency measures before choosing interventions |
| Local branch absence can be continued chain business | 216 of 426 previously active Uptown IDs absent from Uptown afterward appear at another branch | Use chain-wide activity and branch-independent customer continuity before loss-recovery targeting |
| A short absence is not permanent loss | Of 774 baseline IDs not observed during the first 28 days, 488 appear in days 29–56 | Test staged inactivity/service timing with fixed follow-up instead of treating 28-day absence as churn |

The main periods are February 2–March 1 and March 2–29, 2026. A complete 56-day follow-up ends April 26. Active identified customers increase; there is **no overall identified-customer decline in this comparison**. The analysis does not invent one.

About 36.5% of all orders have no Customer ID. Findings describe observed identified accounts, not the full population. ID consistency across branches is assumed and must be verified before operational use. First observed does not mean newly acquired; not observed does not mean permanently lost.

## Start with the business argument

- [Decision memo](reports/decision_memo.md): three customer patterns, limits, decisions, conditional economics, and validation.
- [Main executed notebook](notebooks/stories_decision_analysis.ipynb): coverage checks, comparisons, fixed cohorts, branch continuity, and complete follow-up.
- [Problem statement](docs/problem_statement.md) and [validation plans](docs/pilot.md).
- [Customer methods](docs/customer_methodology.md): denominators, zero-visit cohorts, overlap, missingness, censoring, and decomposition.

## Reproduce

Use Python 3.10+; this workspace was verified with Python 3.13. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
PYTHONPATH=src python3 -m stories.analysis
python3 -m pytest -q
```

The supplied CSV is already at `data/raw/stories_transactions.csv` locally and is ignored by Git. On another machine, place the supplied file there or use `--data /path/to/stories_transactions.csv`. The pipeline recomputes outputs in `reports/` and `reports/figures/`.

For Colab, upload the main notebook, Run All, and upload the CSV when prompted. It embeds the canonical source files. Local notebook execution is verified; the hosted Colab service was not used. Existing uploaded copies do not update automatically when this repository changes.

## Evidence files

| File | Purpose |
|---|---|
| `reports/customer_window_summary.csv` | Orders, ID coverage, active IDs, order/visit-day frequency around all five event boundaries |
| `reports/customer_growth_decomposition.csv` | Exact observed breadth/frequency decomposition; no causal attribution |
| `reports/customer_window_flows.csv` | Both-window, before-only, and after-only accounts; prior observed history |
| `reports/customer_fixed_cohorts.csv` | Independent calibration cohorts, including members with zero comparison-window visits |
| `reports/customer_branch_continuity.csv` | Same-branch, other-branch-only, and unobserved-chain partitions |
| `reports/customer_followup.csv` | Complete 28-/56-day follow-up at event and alternative cutoffs |
| `reports/business_pattern_cards.csv` | Current customer evidence/decision/alternative/validation arguments |
| `reports/business_value_scenarios.csv` | Explicitly hypothetical additional-order and avoided-contact scenarios |
| `src/stories/customers.py` | Reproducible customer analysis |
| `reports/item_branch_memo.md`, `docs/item_branch_validation.md` | Earlier item/branch arguments, retained as supporting work |
| `reports/food_offer_memo.md`, `docs/food_offer_pilot.md` | Earlier optional food-offer investigation |
| `notebooks/reference/` | Original supplied EDA/before-after notebooks and saved outputs |
| `docs/methodology.md`, `data/README.md` | General methods and data provenance |
| `scripts/build_notebook.py` | Rebuild the portable notebook; rerun it afterward to restore outputs |
| `TEAM.md` | Add team names and the eventual submission URL |

Dates supplied by the user: March 2 war-context cutoff; Ramadan February 17–March 18; Lent February 18–April 2, inclusive. Calendar periods overlap and alternative dates show similar customer-continuity patterns. These are decision-relevant observations during changing conditions, not uniquely identified war effects. No campaign, messages, pilot, or GitHub publication was performed. The [hackathon brief](docs/hackathon_brief.pdf) remains reference material, with [source boundaries](docs/project_context.md) documented.
