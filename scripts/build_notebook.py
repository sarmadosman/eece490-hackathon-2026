"""Regenerate the portable notebook from the canonical analysis sources."""
import json
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sources = {name: (ROOT / 'src/stories' / name).read_text()
           for name in ['__init__.py', 'scenario.py', 'calendar.py', 'diagnostics.py', 'business.py', 'customers.py', 'analysis.py']}
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
'''.replace('__SOURCES__', repr(sources))
nb.cells = [
    md('# Stories Coffee: customer continuity during abrupt changes\n\n**Business problem:** How can Stories apply changes to maximize profit in times of abrupt change?\n\nInvestigate uncommon customer-level patterns: whether sales growth reflects more identified customers or more frequent visits, whether branch absence is activity elsewhere in the chain, and whether a short absence is followed by later return. Branch margin and discount investigations remain supporting material.\n\nDates supplied by the user: March 2 war-context cutoff; Ramadan February 17–March 18; Lent February 18–April 2, inclusive. Comparisons account for overlap but do not isolate a causal effect of war or religious observance.\n\n**Identification limit:** about 36.5% of orders lack Customer ID. Results about people concern identified accounts only; IDs must be stable across branches and must be validated as identifying the same customer. First appearance in this file is not proof of acquisition.\n\nRun all locally after installing requirements, or upload this notebook to Colab and upload the supplied CSV when prompted. It embeds its source files.'),
    code(setup),
    md('## 1. Check the population and customer-ID coverage\n\nOne order can have several item lines. Orders are grouped by transaction ID and customer-ID consistency is checked. Count distinct customer-days separately from orders so multiple orders on one day are not automatically multiple visit-days. Missing customer IDs remain missing; they are not one anonymous person or estimated unique people.'),
    code("import contextlib, io\nwith contextlib.redirect_stdout(io.StringIO()):\n    result = run(DATA, OUTPUT)\nd = result['data']\nb = result['baskets']\ncust = result['customers']\ncal = result['calendar']\nbiz = result['business']\ndiag = result['diagnostics']\nchain = 'All branches'\nevent_name = 'March 2 / war context'\ncutoff = pd.Timestamp('2026-03-02')\nwidth = 28\ndisplay(pd.read_json(OUTPUT / 'data_quality.json',typ='series'))\nmain_summary = cust['summary'].query('event == @event_name and days_each_side == @width and branch == @chain')\ndisplay(main_summary)"),
    md('## 2. Compare like periods and disclose overlap\n\nThe main comparison is February 2–March 1 versus March 2–29, 28 days each. Exports also cover Ramadan/Lent starts and ends, with 14/28-day windows and branch-specific customer summaries. Religious-calendar overlap prevents clean attribution. Short-term ID coverage is 64.3% before and 63.4% after: similar, but neither complete nor known to be representative.\n\nThe unique identified audience increases in the main windows; the analysis does not invent a customer decline because it would make a more dramatic story.'),
    code("display(biz['exposure'].query('days_each_side == @width'))\ndisplay(cust['summary'].query('branch == @chain')[['event','days_each_side','period','total_orders','identified_orders','id_coverage','active_identified_customers','orders_per_active_customer']])\ndisplay(Image(filename=str(OUTPUT / 'figures/customer_growth_sources.png')))"),
    md('## 3. Pattern 1: more traffic is not the same as stronger habitual use\n\nActive identified customers rise 1,978 → 2,104, while orders per active identified customer barely move, 1.498 → 1.515. The exact symmetric decomposition assigns about 84.4% of the +225 identified orders to audience breadth and 15.6% to order frequency. This is accounting, not causal attribution.\n\nOf 900 IDs appearing after but not in the preceding 28 days, 508 already appeared earlier in the file. Do not report all 900 as acquired customers. The remaining 392 are first observed in this limited history, not verified first-time customers.\n\n**Fixed-cohort check:** define 584 accounts with at least two distinct visit-days in January 5–February 1, before either comparison window. Keep all 584, including members with zero later orders. They record 504 → 513 orders and $2,662.27 → $2,656.57 gross profit. This supports modest repeat-cohort change in this definition, not a universal or statistically proven loyalty decline. Change the calibration threshold to inspect sensitivity.\n\n**Decision:** separate audience/reactivation performance from repeat-frequency performance before choosing a customer-service or retention intervention. The data do not establish acquisition, satisfaction, or intervention response.'),
    code("display(cust['decomposition'].query('event == @event_name and days_each_side == @width and branch == @chain'))\ndisplay(cust['flows'].query('event == @event_name and days_each_side == @width and branch == @chain'))\ndisplay(cust['cohorts'].query('event == @event_name and days_each_side == @width'))"),
    md('## 4. Pattern 2: a customer missing at one branch may still buy elsewhere\n\nFor Uptown, 507 identified accounts were active before March 2. In the next 28 days, 81 appear at Uptown, 216 appear only at other branches, and 210 are not observed anywhere. Thus 216 of the 426 absent from Uptown, 50.7%, are still observed in the chain.\n\n**Decision:** use chain-wide customer continuity and activity checks before classifying a branch customer as lost. Consider branch-independent loyalty recognition, availability information, or service routing. This is not proof of relocation or a war-driven branch switch; compare other dates.\n\nBranch cohorts overlap if a customer used multiple branches before. Do not sum branch rows as unique people or sum the monetary values as chain-wide opportunity. Validate that the ID is globally consistent across the branches.'),
    code("display(cust['continuity'].query('cutoff == @cutoff and days_each_side == @width'))\ndisplay(Image(filename=str(OUTPUT / 'figures/customer_branch_continuity.png')))\n# Other boundaries/windows remain available to challenge a disruption-specific story.\ndisplay(cust['continuity'].query('days_each_side == @width')[['event','branch','before_customers','apparent_branch_absent','observed_other_branches_only_after','share_of_apparent_branch_absence_seen_elsewhere']])"),
    md('## 5. Pattern 3: a 28-day absence is not permanent loss\n\nFollow the same 1,978 pre-window accounts. 1,204 are observed within 28 days after March 2; 774 are not. With a complete 56-day follow-up through April 26, 1,692 are observed and 286 are not. Of the 774 initially absent, 488, or 63.0%, appear during days 29–56.\n\n**Decision:** test staged inactivity/service policies against a short branch-only rule. A longer reporting horizon mechanically permits more returns; the informative fact is that many accounts labelled absent by a short rule subsequently appear. This does not establish a universally optimal 56-day wait or that late returns were unprompted.\n\nUse only complete follow-up. The same pattern appears at other cutoffs, so it should not be attributed uniquely to war. Missing IDs can conceal visits. A noncontractual coffee business has no directly observed cancellation event; this notebook measures observed return, not true churn.'),
    code("display(cust['followup'].query('cutoff == @cutoff'))\ndisplay(Image(filename=str(OUTPUT / 'figures/customer_followup.png')))\ndisplay(cust['followup'][['cutoff','followup_days','baseline_customers','observed_return_rate','later_return_share_of_initial_absence']])"),
    md('## 6. Challenge the interpretation\n\nCheck all event boundaries, both window lengths, identification coverage, cohort thresholds, and other dates. Ramadan and Lent start nearly together. No unaffected branch or full customer population is available. First observed, newly active, returning, inactive, and permanently lost customers are different concepts. Observed patterns may be normal background behavior rather than effects of disruption.\n\nThe paired repeat-cohort comparison uses membership fixed in an earlier independent period, with zero visits included. This avoids defining a loyal cohort from the same period whose decline is then reported. No customer response model or causal estimate is fitted. More formal attrition modeling requires additional assumptions and validation.\n\nThe practical argument is that sales totals, branch-only activity, and short absence rules can lead to different—and potentially misleading—customer decisions.'),
    code("display(Image(filename=str(OUTPUT / 'figures/calendar_timeline.png')))\ndisplay(pd.read_csv(OUTPUT / 'alternative_cutoff_comparisons.csv').query('branch == @chain'))\ndisplay(cust['summary'].query('branch != @chain and days_each_side == @width')[['event','branch','period','id_coverage','active_identified_customers']])"),
    md('## 7. Customer decisions, conditional value, and validation\n\nThe three current arguments are customer breadth versus repeat behavior, cross-branch continuity, and the timing of observed return. Validate any customer-service or outreach policy with a preassigned control, customer-level randomization, chain-wide outcomes, fixed follow-up, and recorded intervention costs. No messages were sent or campaign run.\n\nValue scenarios are conditional, not measured uplift. The one-extra-order scenarios use observed identified-order contribution before intervention and other incremental costs. The avoided-contact scenarios assume an otherwise existing branch-loss process and hypothetical costs; they establish no realized savings. Do not aggregate overlapping branch cohorts.\n\nSee reports/decision_memo.md for the business argument and docs/pilot.md for validation plans.'),
    code("display(cust['patterns'])\ndisplay(cust['value_scenarios'])"),
    md('## Appendix A. Supporting calendar and demand checks\n\nCalendar regression is retrospective and not a causal no-war forecast. The original demand projection is calendar-unadjusted, and its shaded historical-error band is not a calibrated prediction interval. Preparation backtests predict recorded sales, not optimal stock or realized waste savings.'),
    code("display(Image(filename=str(OUTPUT / 'figures/calendar_model_sensitivity.png')))\ndisplay(result['scores'])\ndisplay(pd.read_csv(OUTPUT / 'preparation_backtest.csv'))"),
    md('## Appendix B. Earlier item/branch analysis retained for context\n\nThe earlier promotion, branch-margin, product-preparation, and food-offer investigations remain in the reports and source code as supporting work. They are not the main business argument. Original supplied notebooks and saved plots remain in notebooks/reference. Full item comparisons can still be used to challenge customer-basket explanations.'),
    code("display(biz['changes'].query('event == @event_name and branch == @chain and days_each_side == @width')[['product','units_before','units_after','gross_profit_before','gross_profit_after']])\ndisplay(pd.read_csv(OUTPUT / 'duplicate_sensitivity.csv'))"),
]
nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
               'language_info': {'name': 'python', 'version': '3.13'}}
path = ROOT / 'notebooks/stories_decision_analysis.ipynb'
nbf.write(nb, path)
print(path)
