"""Regenerate the portable notebook from the canonical analysis sources."""
import json
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sources = {name: (ROOT / 'src/stories' / name).read_text()
           for name in ['__init__.py', 'scenario.py', 'calendar.py', 'diagnostics.py', 'business.py', 'customers.py', 'analysis.py']}
promotion_source = (ROOT / "scripts/promotion_test.py").read_text()
nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
setup = '''from pathlib import Path
import sys, os, tempfile
import pandas as pd
from IPython.display import display, Image

# Colab may not ship the calendar model dependency. Install only if absent.
import importlib.util
if importlib.util.find_spec('statsmodels') is None:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'statsmodels>=0.14,<0.15'])

# Use repository sources locally; embedded copies make this file portable to Colab.
PROJECT = next((p for p in [Path.cwd(), Path.cwd().parent] if (p / 'src/stories/analysis.py').exists()), None)
if PROJECT is None:
    PROJECT = Path(tempfile.mkdtemp(prefix='stories-coffee-'))
    package = PROJECT / 'src/stories'
    package.mkdir(parents=True)
    embedded_sources = __SOURCES__
    for name, source in embedded_sources.items():
        (package / name).write_text(source)
promotion_path = PROJECT / "scripts/promotion_test.py"
if not promotion_path.exists():
    promotion_path.parent.mkdir(parents=True, exist_ok=True)
    promotion_path.write_text(__PROMOTION_SOURCE__)
sys.path.insert(0, str(PROJECT / 'src'))
os.environ.setdefault('MPLCONFIGDIR', str(PROJECT / '.cache/matplotlib'))
DATA = PROJECT / 'data/raw/stories_transactions.csv'
if not DATA.exists():
    try:
        from google.colab import files
    except ImportError:
        raise FileNotFoundError('Place stories_transactions.csv in data/raw, or set DATA to its location.')
    print('Upload the supplied stories_transactions.csv.')
    uploads = files.upload()
    if 'stories_transactions.csv' not in uploads:
        raise ValueError('Expected stories_transactions.csv in the uploaded files.')
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_bytes(uploads['stories_transactions.csv'])
from stories.analysis import run, CUTOFF
from stories.scenario import evaluate
OUTPUT = PROJECT / 'reports'
'''.replace(
    '__SOURCES__', repr(sources)
).replace(
    '__PROMOTION_SOURCE__', repr(promotion_source)
)
nb.cells = [
    md('# Stories Coffee: a playbook for abrupt change\n\n**Business problem:** How can Stories apply changes to maximize profit in times of abrupt change?\n\nThe final three-part argument is about **demand and preparation**, **observational promotion results**, and **customer continuity with testable intervention timing**. Supporting food-offer and branch-cost investigations remain in section 6.\n\nDates supplied by the team: March 2 war-context cutoff; Ramadan February 17–March 18; Lent February 18–April 2, inclusive. Overlap and concurrent changes prevent clean causal attribution. Recorded gross profit excludes unrecorded operating costs.\n\nRun all locally after installing requirements, or upload this notebook to Colab and upload the supplied CSV. The package sources and promotion script are embedded for standalone execution.'),
    code(setup),
    md('## 1. Data quality and calendar overlap\n\nOne order can contain multiple item lines. Count distinct transaction IDs, reconcile accounting, retain ambiguous exact repeats with a separate sensitivity check, and show calendar overlap. Customer findings cover identified accounts only; 36.5% of orders lack IDs. Cross-branch results assume globally consistent IDs. First observed, previously observed, and observed return describe the recorded data, not verified acquisition or permanent customer loss.'),
    code("import contextlib, io\nwith contextlib.redirect_stdout(io.StringIO()):\n    result = run(DATA, OUTPUT)\nd = result['data']\nb = result['baskets']\ncal = result['calendar']\ncust = result['customers']\nbiz = result['business']\ndiag = result['diagnostics']\nchain = 'All branches'\nevent_name = 'March 2 / war context'\ncutoff = pd.Timestamp('2026-03-02')\nwidth = 28\ndisplay(pd.read_json(OUTPUT / 'data_quality.json',typ='series'))\nphases = cal['phases'].query('branch == @chain and days > 1')\ndisplay(phases[['phase','days','orders_per_day','gross_profit_per_order','evening_share','takeaway_share','meal_attachment']])\ndisplay(biz['exposure'].query('days_each_side == @width'))"),
    md('## 2. Demand and preparation\n\n**Conclusion 1: Recorded orders increased, while selected aggregate trading measures remained broadly similar.**\n\nOrders rise from 4,611 to 5,030 in the matched March 2 windows (+9.1%). Across the multi-day phases, evening share is 50.0–51.0%, takeaway share 39.7–41.3%, recorded gross profit/order $5.28–$5.32, and meal attachment approximately 2.0–2.4%. These aggregates do not establish equivalence, exclude branch/product changes, or rule out calendar effects.\n\nSimilar increases at other cutoffs weaken the interpretation that the observed growth uniquely marks March 2; they do not rule out conflict-related effects. The original pre-cutoff forecast is a calendar-unadjusted reference, not verified no-war demand. Its historical-error bands are not calibrated prediction intervals. Preparation errors concern recorded sales, not unmet demand or measured waste savings.\n\n**Decision:** test recent same-weekday preparation with waste, availability, and service logs; use branch-specific observed demand. Define an operationally meaningful threshold and uncertainty criterion before concluding there is no material change.'),
    code("display(Image(filename=str(OUTPUT / 'figures/calendar_timeline.png')))\ndisplay(pd.read_csv(OUTPUT / 'alternative_cutoff_comparisons.csv').query('branch == @chain'))\ndisplay(result['scores'])\ndisplay(pd.read_csv(OUTPUT / 'projection_summary.csv'))\ndisplay(pd.read_csv(OUTPUT / 'projection_model_sensitivity.csv'))\ndisplay(pd.read_csv(OUTPUT / 'preparation_backtest.csv'))"),
    md('### Model evaluation: simple baselines and a separate later test\n\n**Target:** recorded daily orders per branch. **Simple baseline:** repeat the last matching weekday available at the forecast origin. Also compare the prior-four-matching-weekdays average with linear trend plus weekday regression.\n\n**Selection and training:** choose using three earlier 14-day validation folds (Jan 29–Feb 11, Feb 5–18, Feb 12–25), then refit on Jan 1–Mar 1. Those overlapping development folds, shown above, are not the final test. **Separate test:** Mar 2–29, 28 days per branch. Issue all predictions using history ending Mar 1; do not update with test sales or change choices after looking at errors. All three candidates face the same test dates.\n\n**Read the scores:** MAE is average absolute error in orders per branch per day; WAPE is total absolute error divided by total actual orders. Lower is better. A positive MAE reduction means improvement over last matching weekday. The earlier-selected candidates reduce test MAE by 12.7% at Harbour, 17.9% at Garden, and 19.4% at Uptown. Complexity does not consistently help: Garden’s selected regression loses to the four-week average, and Harbour’s selected average loses to regression. Keep both losses visible.\n\nThese dates were already explored retrospectively, but are excluded from fitting and the coded selection rule. This is not a prospective trial, a causal no-war forecast, or proof of profit gains. Food preparation above forecasts units one day ahead using prior sales, so its errors answer a different operating question. The generated reports/forecast_evaluation.md records the split and full comparison.'),
    code("test_scores = result['holdout_scores'].copy()\ntest_scores['candidate'] = test_scores.model.map({\n    'previous_weekday': 'Last matching weekday (baseline)',\n    'recent_weekday_average': 'Prior four matching weekdays',\n    'trend_weekday': 'Linear trend + weekday',\n})\ndisplay(test_scores[['branch','candidate','selected_on_validation','train_start','train_end','test_start','test_end','test_days','mae','wape','bias','mae_reduction_vs_baseline_pct']])\nprint('Dark outlines in the figure mark choices made using earlier validation, not choices made from test results.')\ndisplay(Image(filename=str(OUTPUT / 'figures/forecast_holdout.png')))"),
    md('## 3. Promotion comparison and uncertainty\n\n**Conclusion 2: The observed promotion results do not establish that the discounts paid for themselves.**\n\nHarbour has two recorded 15%-off Cold Coffee/Desserts windows, March 12–19 and May 12–19. The observational promotion comparison adjusts for common movements if the branches would otherwise have followed comparable relative trends. It does not establish the counterfactual without promotion. First-observed buyer counts cannot identify incremental customer acquisition.\n\nThe script below is included in this notebook for standalone Colab use. Its historical CSV filename, promotion_natural_experiment.csv, is retained for compatibility; the interpretation is observational. The approximately 29% same-mix break-even benchmark is an accounting comparison, not a unit-only expansion rule.'),
    code('import subprocess\n\nsubprocess.run(\n    [\n        sys.executable,\n        str(PROJECT / "scripts/promotion_test.py"),\n        "--data", str(DATA),\n    ],\n    check=True,\n)\n\ndisplay(pd.read_csv(OUTPUT / "promotion_natural_experiment.csv"))\ndisplay(pd.read_csv(OUTPUT / "promotion_placebo.csv"))\ndisplay(Image(filename=str(OUTPUT / "figures/promotion_comparison.png")))'),
    md('**Uncertainty:** the 60 overlapping non-promotion windows produced relative changes with a central 95% range of approximately −21% to +16%. The observed promotion comparisons, +10.7% and −4.4%, lie within this background variation. This does not establish zero effect or rule out a break-even effect: negative background variation can mask positive promotion effects. These overlapping windows are descriptive sensitivity checks, not independent experiments or a calibrated power analysis.\n\n**Measured:** the two promotion windows recorded $471.55 in discounts relative to listed prices. This is not a measured causal profit loss: the quantities customers would have purchased without the promotion are unknown. **Conditional scenario:** holding quantities and product mix unchanged, charging full listed prices would have increased recorded gross profit by $471.55. Ordinary discounts, changes in demand, substitution, and later purchases could reduce or reverse that difference. We recommend a randomized holdout before repeating the promotion.'),
    code('promotion = pd.read_csv(OUTPUT / \'promotion_natural_experiment.csv\')\nbackground = pd.read_csv(OUTPUT / \'promotion_placebo.csv\')\ndiscounts = promotion.query("metric == \'promo_cat_discount_usd\'")\ndisplay(discounts[[\'promo_start\',\'promo_end\',\'harbour_during_total\']].rename(columns={\'harbour_during_total\':\'discount_relative_to_listed_prices_usd\'}))\nprint(f"Observed discount relative to listed prices: ${discounts.harbour_during_total.sum():,.2f}")\nprint(f"Same-mix unit break-even benchmark: {promotion.break_even_unit_lift_pct.iloc[0]:.1f}%")\ndisplay(background.harbour_vs_others_change_pct.quantile([.025,.975]).rename(\'empirical_relative_change_pct\'))'),
    md('## 4. Customer continuity and timing\n\n**Conclusion 3: Check chain-wide activity and test inactivity thresholds before targeting customers.**\n\nAmong the 1,978 identified accounts active in the baseline window, 1,692 were observed again within 56 days and 286 were not observed. These are observed-account return measures, not estimates of permanent customer loss.\n\nAmong baseline accounts not observed again at their original branch during the next 28 days, the share observed elsewhere was 49.2% for Garden, 38.9% for Harbour, and 50.7% for Uptown. Branch cohorts overlap and must not be summed as unique customers. Customer findings cover identified accounts only; 36.5% of orders lack IDs. Cross-branch results assume globally consistent IDs.\n\nOf 774 baseline accounts unobserved during the first 28-day follow-up, 488 appeared during days 29–56. Their returns may already have been influenced by existing activity or interventions. This count does not measure avoidable incentives or prove that earlier contact would be ineffective.\n\nThe historical cohort is based on calendar windows, not an exact individual last-purchase-indexed eligibility rule. First-observed IDs are not verified new customers; previously observed and observed return are the appropriate terms.'),
    code("display(cust['summary'].query('event == @event_name and days_each_side == @width and branch == @chain'))\ndisplay(cust['decomposition'].query('event == @event_name and days_each_side == @width and branch == @chain'))\ndisplay(cust['flows'].query('event == @event_name and days_each_side == @width and branch == @chain'))\ndisplay(cust['cohorts'].query('event == @event_name and days_each_side == @width'))\ndisplay(cust['continuity'].query('cutoff == @cutoff and days_each_side == @width'))\ndisplay(cust['followup'].query('cutoff == @cutoff'))\ndisplay(Image(filename=str(OUTPUT / 'figures/customer_branch_continuity.png')))\ndisplay(Image(filename=str(OUTPUT / 'figures/customer_followup.png')))"),
    md('## 5. Conditional economics and pilot decisions\n\n**Preparation:** evaluate a recent-demand rule using waste, availability, wait-time, and operating-cost records before translating forecast improvements into profit.\n\n**Promotion:** expand only if the randomized comparison shows a pre-agreed worthwhile improvement in total branch gross contribution after discounts and incremental operating costs. Report promoted-category units and the approximately 29% same-mix break-even benchmark as supporting measures. Include gains/losses elsewhere in the basket.\n\n**Test intervention timing:** compare contacting accounts after 28 days without an identified chain-wide purchase with contacting them after 56 days if they remain inactive. Historical returns do not establish which timing produces higher incremental contribution. Eligibility begins 28 days after each account’s last recorded chain-wide purchase. Randomize eligible accounts to contact immediately or wait another 28 days and contact only if still inactive. Evaluate both groups for 56 days from randomization, retaining every assigned account in the denominator.\n\nThe 488 later observed accounts are not an avoided-incentive estimate. A scenario in which 1% of baseline identified accounts make one genuinely additional order is hypothetical, before intervention and other incremental costs. No campaign or pilot has been run.'),
    code("# Keep only the additional-order scenarios; no historical-return count is priced as avoided incentives.\ndisplay(cust['value_scenarios'].query('pattern == 1'))\ndisplay(pd.read_csv(OUTPUT / 'duplicate_sensitivity.csv'))"),
    md('## 6. Supporting food-offer and branch-cost analyses\n\nEarlier food offers, product comparisons, and branch-cost investigations remain supporting material. They do not replace the three conclusions above. Same-product cost gaps are accounting/procurement hypotheses, not attainable savings; historical co-purchases do not estimate incremental response to a suggestion. Calendar regressions are retrospective and model-dependent. See the original supplied notebooks in notebooks/reference and the supporting reports for details.'),
    code("display(result['opportunities'])\ndisplay(pd.read_csv(OUTPUT / 'basket_summary.csv'))\ndisplay(diag['cost'].groupby('branch')[['price_ratio_to_reference','cost_ratio_to_reference']].agg(['min','median','max']))\ndisplay(Image(filename=str(OUTPUT / 'figures/offer_tradeoff.png')))\ndisplay(Image(filename=str(OUTPUT / 'figures/calendar_model_sensitivity.png')))"),
]
nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
               'language_info': {'name': 'python', 'version': '3.13'}}
path = ROOT / 'notebooks/stories_decision_analysis.ipynb'
nbf.write(nb, path)
print(path)
