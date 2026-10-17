"""Retrospective calendar comparisons, never causal attribution or real-time forecasts."""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

RAMADAN_START = pd.Timestamp('2026-02-17')
RAMADAN_END = pd.Timestamp('2026-03-18')
LENT_START = pd.Timestamp('2026-02-18')
LENT_END = pd.Timestamp('2026-04-02')
CHANGE_DATE = pd.Timestamp('2026-03-02')
PHASES = ['Before both / before March 2', 'Ramadan only: one day',
          'Ramadan + Lent / before March 2', 'Ramadan + Lent / after March 2',
          'Lent only / after March 2', 'After both / after March 2']


def annotate(frame):
    x = frame.copy()
    x['ramadan'] = x.date.between(RAMADAN_START, RAMADAN_END).astype(int)
    x['lent'] = x.date.between(LENT_START, LENT_END).astype(int)
    x['post_march2'] = (x.date >= CHANGE_DATE).astype(int)
    conditions = [x.date < RAMADAN_START, x.date < LENT_START,
                  x.date < CHANGE_DATE, x.date <= RAMADAN_END, x.date <= LENT_END]
    x['phase'] = np.select(conditions, PHASES[:-1], default=PHASES[-1])
    return x


def daily_metrics(d, b):
    rows = []
    for branch in ['All branches', *sorted(d.branch.unique())]:
        items = d if branch == 'All branches' else d[d.branch == branch]
        orders = b if branch == 'All branches' else b[b.branch == branch]
        orders = orders.assign(evening=orders.hour >= 18,
            midday=orders.hour.between(11, 15),
            takeaway=orders.order_type.eq('Takeaway'),
            breakfast=orders.index.isin(items.loc[items.category == 'Breakfast', 'transaction']),
            drink_bakery=orders.drink & orders.bakery,
            drink_meal=orders.drink & orders.meal)
        s = orders.groupby('date').agg(orders=('branch', 'size'),
            gross_profit=('gross_profit', 'sum'), revenue=('revenue', 'sum'),
            evening_orders=('evening', 'sum'), midday_orders=('midday', 'sum'),
            takeaway_orders=('takeaway', 'sum'), breakfast_orders=('breakfast', 'sum'),
            drink_orders=('drink', 'sum'), bakery_drink_orders=('drink_bakery', 'sum'),
            meal_drink_orders=('drink_meal', 'sum'), eligible_orders=('eligible', 'sum'))
        dates = pd.date_range(d.date.min(), d.date.max())
        s = s.reindex(dates, fill_value=0)
        unit = items.assign(discounted_units=items.quantity * items.discount.gt(0)).groupby('date').agg(
            units=('quantity', 'sum'), discounted_units=('discounted_units', 'sum'))
        s = s.join(unit).fillna(0)
        s['branch'] = branch
        s.index.name = 'date'; s = s.reset_index()
        rows.append(s)
    daily = annotate(pd.concat(rows, ignore_index=True))
    return add_rates(daily)


def add_rates(s):
    s = s.copy()
    denominator = s.orders.replace(0, np.nan)
    for metric in ['evening', 'midday', 'takeaway', 'breakfast']:
        s[f'{metric}_share'] = s[f'{metric}_orders'] / denominator
    s['gross_profit_per_order'] = s.gross_profit / denominator
    s['bakery_attachment'] = s.bakery_drink_orders / s.drink_orders.replace(0, np.nan)
    s['meal_attachment'] = s.meal_drink_orders / s.drink_orders.replace(0, np.nan)
    s['discounted_unit_share'] = s.discounted_units / s.units.replace(0, np.nan)
    return s


def phase_summary(daily):
    counts = ['orders', 'gross_profit', 'revenue', 'evening_orders', 'midday_orders',
              'takeaway_orders', 'breakfast_orders', 'drink_orders', 'bakery_drink_orders',
              'meal_drink_orders', 'eligible_orders', 'units', 'discounted_units']
    s = daily.groupby(['branch', 'phase'])[counts].sum()
    s['days'] = daily.groupby(['branch', 'phase']).date.nunique()
    s = add_rates(s.reset_index())
    s['orders_per_day'] = s.orders / s.days
    s['eligible_orders_per_day'] = s.eligible_orders / s.days
    order = {p: i for i, p in enumerate(PHASES)}
    return s.assign(_sort=s.phase.map(order)).sort_values(['branch', '_sort']).drop(columns='_sort')


def category_phases(d, daily):
    rows = []
    exposure = daily.set_index(['branch', 'phase']).groupby(level=[0, 1]).size()
    for branch in ['All branches', *sorted(d.branch.unique())]:
        x = annotate(d if branch == 'All branches' else d[d.branch == branch])
        s = x.assign(discounted_units=x.quantity * x.discount.gt(0)).groupby(['phase', 'category']).agg(
            units=('quantity', 'sum'), gross_profit=('gross_profit', 'sum'),
            discounted_units=('discounted_units', 'sum')).reset_index()
        s['branch'] = branch
        s['phase_days'] = s.phase.map(exposure.loc[branch])
        s['units_per_day'] = s.units / s.phase_days
        s['unit_share'] = s.units / s.groupby('phase').units.transform('sum')
        s['gross_profit_per_unit'] = s.gross_profit / s.units
        s['discounted_unit_share'] = s.discounted_units / s.units
        rows.append(s)
    return pd.concat(rows, ignore_index=True)


def boundary_comparisons(daily):
    events = [('Joint calendar start', RAMADAN_START), ('March 2', CHANGE_DATE),
              ('Ramadan ended', RAMADAN_END + pd.Timedelta(days=1)),
              ('Lent ended', LENT_END + pd.Timedelta(days=1))]
    rows = []
    for branch, g in daily.groupby('branch'):
        for event, date in events:
            for width in [7, 14]:
                pre = g[(g.date >= date - pd.Timedelta(days=width)) & (g.date < date)]
                post = g[(g.date >= date) & (g.date < date + pd.Timedelta(days=width))]
                if len(pre) != width or len(post) != width:
                    continue
                total = add_rates(pd.DataFrame([pre.sum(numeric_only=True), post.sum(numeric_only=True)]))
                for metric in ['orders', 'evening_share', 'midday_share', 'gross_profit_per_order',
                               'bakery_attachment', 'meal_attachment', 'discounted_unit_share']:
                    before, after = total[metric].tolist()
                    change = ((after / before - 1) * 100 if metric == 'orders'
                              else (after - before) * (1 if metric == 'gross_profit_per_order' else 100))
                    rows.append(dict(branch=branch, event=event, boundary_date=date,
                        window_days_each_side=width, metric=metric, before=before, after=after,
                        change=change, change_unit='percent' if metric == 'orders' else
                        ('USD/order' if metric == 'gross_profit_per_order' else 'percentage points'),
                        pre_ramadan_days=int(pre.ramadan.sum()), post_ramadan_days=int(post.ramadan.sum()),
                        pre_lent_days=int(pre.lent.sum()), post_lent_days=int(post.lent.sum()),
                        pre_postmarch2_days=int(pre.post_march2.sum()), post_postmarch2_days=int(post.post_march2.sum())))
    return pd.DataFrame(rows)


def model_associations(daily):
    """OLS with weekday/trend adjustment and HAC errors; full-sample associations only."""
    records, diagnostics = [], []
    specs = [('through_April_linear', '2026-04-30', False, False),
             ('through_April_quadratic', '2026-04-30', True, False),
             ('through_June_linear', '2026-06-30', False, False),
             ('through_June_quadratic', '2026-06-30', True, False),
             ('through_June_post_slope', '2026-06-30', False, True)]
    metrics = ['orders', 'evening_share', 'midday_share', 'gross_profit_per_order',
               'bakery_attachment', 'meal_attachment', 'breakfast_share', 'discounted_unit_share']
    for branch, g in daily.groupby('branch'):
        for spec, end, quadratic, post_slope in specs:
            z = g[g.date <= end].sort_values('date').copy()
            t = (z.date - daily.date.min()).dt.days / 7
            X = pd.DataFrame({'intercept': 1., 'trend_weeks': t,
                              'ramadan': z.ramadan, 'lent': z.lent,
                              'post_march2': z.post_march2}, index=z.index)
            if quadratic:
                X['trend_squared'] = t ** 2
            if post_slope:
                X['post_trend_weeks'] = ((z.date - CHANGE_DATE).dt.days / 7).clip(lower=0)
            for day in range(1, 7):
                X[f'weekday_{day}'] = z.date.dt.dayofweek.eq(day).astype(float)
            for metric in metrics:
                mask = z[metric].notna() & (z[metric].gt(0) if metric == 'orders' else True)
                target = np.log(z.loc[mask, metric]) if metric == 'orders' else z.loc[mask, metric]
                fit = sm.OLS(target, X.loc[mask].astype(float)).fit(cov_type='HAC',
                    cov_kwds={'maxlags': 7, 'use_correction': True}, use_t=True)
                intervals = fit.conf_int()
                for term in ['ramadan', 'lent', 'post_march2']:
                    scale = (lambda v: 100 * np.expm1(v)) if metric == 'orders' else (
                        (lambda v: v) if metric == 'gross_profit_per_order' else (lambda v: 100 * v))
                    records.append(dict(branch=branch, specification=spec, metric=metric,
                        term=term, association=scale(fit.params[term]),
                        ci_lower=scale(intervals.loc[term, 0]), ci_upper=scale(intervals.loc[term, 1]),
                        unit='percent' if metric == 'orders' else ('USD/order' if metric == 'gross_profit_per_order' else 'percentage points'),
                        n_days=int(fit.nobs), causal=False))
            diagnostics.append(dict(branch=branch, specification=spec, n_days=len(z),
                design_rank=int(np.linalg.matrix_rank(X)), design_columns=len(X.columns),
                condition_number=float(np.linalg.cond(X)),
                ramadan_lent_correlation=float(z.ramadan.corr(z.lent))))
    return pd.DataFrame(records), pd.DataFrame(diagnostics)


def calendar_figures(daily, associations, output):
    import matplotlib.pyplot as plt
    x = daily[daily.branch == 'All branches'].set_index('date')
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    for ax, metric, title, multiplier in zip(axes,
        ['orders', 'evening_share', 'gross_profit_per_order'],
        ['Orders/day (7-day mean)', 'Evening orders, 18:00–23:59 (%)', 'Gross profit/order (USD)'],
        [1, 100, 1]):
        ax.plot(x.index, x[metric].rolling(7, min_periods=7).mean() * multiplier, color='#334155')
        ax.axvspan(RAMADAN_START, RAMADAN_END + pd.Timedelta(days=1), color='#0d9488', alpha=.15, label='Ramadan (supplied dates)')
        ax.axvspan(LENT_START, LENT_END + pd.Timedelta(days=1), color='#b283df', alpha=.13, label='Lent (supplied dates)')
        ax.axvline(CHANGE_DATE, color='#c25a28', ls='--', label='March 2 cutoff')
        ax.set_ylabel(title)
    axes[0].legend(loc='upper left', fontsize=8)
    fig.suptitle('Calendar overlap and observed trading patterns — no causal attribution')
    fig.tight_layout(); fig.savefig(output / 'calendar_timeline.png', dpi=150); plt.close(fig)
    a = associations[(associations.branch == 'All branches') &
                     (associations.metric == 'orders')]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    specs = a.specification.unique()
    for ax, term in zip(axes, ['ramadan', 'lent', 'post_march2']):
        s = a[a.term == term].set_index('specification').loc[specs]
        y = np.arange(len(s))
        ax.errorbar(s.association, y,
            xerr=np.vstack([s.association - s.ci_lower, s.ci_upper - s.association]),
            fmt='o', capsize=3, color='#0d7e77')
        ax.axvline(0, color='#64748b', ls='--'); ax.set_title(term)
        ax.set_xlabel('Adjusted association with daily orders (%)')
        ax.set_yticks(y, specs)
    fig.suptitle('Retrospective model sensitivity; 95% HAC intervals are conditional on each model')
    fig.tight_layout(); fig.savefig(output / 'calendar_model_sensitivity.png', dpi=150); plt.close(fig)


def run_calendar(d, b, output):
    output = Path(output)
    daily = daily_metrics(d, b)
    phases = phase_summary(daily)
    categories = category_phases(d, daily)
    boundaries = boundary_comparisons(daily)
    associations, diagnostics = model_associations(daily)
    for name, table in [('calendar_daily_metrics', daily), ('calendar_phase_summary', phases),
                        ('calendar_category_phases', categories), ('calendar_boundary_comparisons', boundaries),
                        ('calendar_adjusted_associations', associations),
                        ('calendar_model_diagnostics', diagnostics)]:
        table.to_csv(output / f'{name}.csv', index=False)
    calendar_figures(daily, associations, output / 'figures')
    return {'daily': daily, 'phases': phases, 'categories': categories, 'boundaries': boundaries,
            'associations': associations, 'diagnostics': diagnostics}
