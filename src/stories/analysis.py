"""Run all analyses without network calls. Outputs are recomputed from the supplied CSV."""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .scenario import evaluate
from .calendar import run_calendar
from .diagnostics import run_diagnostics
from .business import run_business
from .customers import run_customers

ROOT = Path(__file__).resolve().parents[2]
CUTOFF = pd.Timestamp('2026-03-02')  # User-supplied context, not inferred causality.
DRINKS = ['Hot Coffee', 'Cold Coffee', 'Matcha & Tea']
FOODS = ['Bakery', 'Meals']
COLUMNS = {
    'Transaction ID': 'transaction', 'Date': 'date', 'Time': 'time',
    'Branch': 'branch', 'Customer ID': 'customer', 'Order Type': 'order_type',
    'Product': 'product', 'Category': 'category', 'Quantity': 'quantity',
    'Unit Price (USD)': 'price', 'Discount Rate': 'discount',
    'Unit Cost (USD)': 'cost', 'Line Revenue (USD)': 'revenue',
    'Line Gross Profit (USD)': 'gross_profit',
}


def load_data(path):
    d = pd.read_csv(path)
    missing = set(COLUMNS) - set(d.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    d = d.rename(columns=COLUMNS)
    d['date'] = pd.to_datetime(d['date'], errors='raise')
    pd.to_datetime(d['time'], format='%H:%M:%S', errors='raise')
    if d.drop(columns='customer').isna().any().any():
        raise ValueError('Unexpected missing values outside Customer ID.')
    if (d.quantity <= 0).any() or (d.price < 0).any() or (d.cost < 0).any():
        raise ValueError('Nonpositive quantity or negative price/cost requires investigation.')
    if not d.discount.between(0, 1).all():
        raise ValueError('Discount must be a fraction between zero and one.')
    consistency = d.groupby('transaction')[['branch', 'date', 'order_type', 'time']].nunique()
    if (consistency > 1).any().any():
        raise ValueError('Transaction metadata is inconsistent; review basket keys.')
    return d


def quality(d, path):
    orders = d.groupby('transaction').customer.first()
    revenue_error = (d.revenue - d.quantity * d.price * (1 - d.discount)).abs()
    profit_error = (d.gross_profit - (d.revenue - d.quantity * d.cost)).abs()
    return {
        'source_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        'rows': len(d), 'transactions': int(d.transaction.nunique()),
        'products': int(d['product'].nunique()),
        'date_min': str(d.date.min().date()), 'date_max': str(d.date.max().date()),
        'exact_duplicate_rows_beyond_first': int(d.duplicated().sum()),
        'missing_customer_fraction_orders': float(orders.isna().mean()),
        'max_revenue_formula_error_usd': float(revenue_error.max()),
        'max_gross_profit_formula_error_usd': float(profit_error.max()),
        'revenue_formula_errors_over_one_cent': int((revenue_error > .010001).sum()),
        'gross_profit_formula_errors_over_one_cent': int((profit_error > .010001).sum()),
        'duplicate_policy': 'Retain all rows; export errors versus valid repeated lines are unknown. Repeat key results after exact deduplication.',
    }


def branch_summary(d):
    s = d.groupby('branch').agg(orders=('transaction', 'nunique'), units=('quantity', 'sum'),
                               revenue=('revenue', 'sum'), gross_profit=('gross_profit', 'sum'))
    s['gross_margin'] = s.gross_profit / s.revenue
    s['gross_profit_per_order'] = s.gross_profit / s.orders
    return s.reset_index()


def baskets(d):
    b = d.groupby('transaction').agg(date=('date', 'first'), branch=('branch', 'first'),
        time=('time', 'first'), order_type=('order_type', 'first'),
        revenue=('revenue', 'sum'), gross_profit=('gross_profit', 'sum'))
    for name, cats in [('drink', DRINKS), ('bakery', ['Bakery']), ('meal', ['Meals'])]:
        b[name] = b.index.isin(d.loc[d.category.isin(cats), 'transaction'])
    b['eligible'] = b.drink & ~b.bakery & ~b.meal
    b['hour'] = b.time.str[:2].astype(int)
    return b


def matched_comparison(d):
    # Two adjacent 28-day windows: identical weekday counts and no unequal exposure.
    a = d[(d.date >= CUTOFF - pd.Timedelta(days=28)) &
          (d.date < CUTOFF + pd.Timedelta(days=28))].copy()
    a['period'] = np.where(a.date < CUTOFF, 'pre_28_days', 'post_28_days')
    s = a.groupby(['branch', 'category', 'period']).agg(units=('quantity', 'sum'),
        revenue=('revenue', 'sum'), gross_profit=('gross_profit', 'sum'),
        category_orders=('transaction', 'nunique'))
    s['gross_profit_per_unit'] = s.gross_profit / s.units
    s['discounted_unit_share'] = a.assign(discounted_units=a.quantity * (a.discount > 0)).groupby(
        ['branch', 'category', 'period']).discounted_units.sum() / s.units
    return s.reset_index()


def product_opportunities(d, b):
    post = d[(d.date >= CUTOFF) & (d.date < CUTOFF + pd.Timedelta(days=28))]
    bp = b[(b.date >= CUTOFF) & (b.date < CUTOFF + pd.Timedelta(days=28))]
    rows = []
    for branch, g in post[post.category.isin(FOODS)].groupby('branch'):
        bb = bp[bp.branch == branch]
        drinks = bb[bb.drink]
        eligible = bb[bb.eligible]
        for (cat, product), x in g.groupby(['category', 'product']):
            units = x.quantity.sum()
            price = float((x.price * x.quantity).sum() / units)
            cost = float((x.cost * x.quantity).sum() / units)
            pair_count = int(drinks.index.isin(x.transaction).sum())
            rows.append(dict(branch=branch, category=cat, product=product,
                food_units=int(units), weighted_list_price=price, weighted_unit_cost=cost,
                observed_gross_profit_per_unit=float(x.gross_profit.sum() / units),
                normal_price_contribution=price-cost,
                max_discount_for_2_usd_contribution=max(0, price-cost-2),
                two_usd_contribution_feasible=bool(price-cost >= 2),
                drink_orders=len(drinks), historical_eligible_orders=len(eligible),
                existing_pair_orders=pair_count,
                existing_pair_rate=pair_count / len(drinks) if len(drinks) else 0))
    return pd.DataFrame(rows).sort_values(['branch', 'category', 'normal_price_contribution'],
                                         ascending=[True, True, False])


def features(index, start):
    t = (index - start).days.to_numpy() / 7
    weekdays = np.column_stack([(index.dayofweek == i).astype(float) for i in range(1, 7)])
    return np.column_stack([t, weekdays])


def product_pairs(d):
    """Observed distinct-product basket pairs; association is not incremental demand."""
    x = d[(d.date >= CUTOFF) & (d.date < CUTOFF + pd.Timedelta(days=28))]
    drink = x[x.category.isin(DRINKS)][['branch', 'transaction', 'product']].drop_duplicates()
    food = x[x.category.isin(FOODS)][['branch', 'transaction', 'product', 'category']].drop_duplicates()
    pairs = drink.merge(food, on=['branch', 'transaction'], suffixes=('_drink', '_food'))
    counts = pairs.groupby(['branch', 'product_drink', 'category', 'product_food']).size().rename('pair_orders').reset_index()
    dn = drink.groupby(['branch', 'product']).size().rename('drink_product_orders').reset_index()
    fn = food.groupby(['branch', 'product']).size().rename('food_product_orders').reset_index()
    counts = counts.merge(dn, left_on=['branch', 'product_drink'], right_on=['branch', 'product']).drop(columns='product')
    counts = counts.merge(fn, left_on=['branch', 'product_food'], right_on=['branch', 'product']).drop(columns='product')
    totals = x.groupby('branch').transaction.nunique()
    counts['pair_rate_given_drink'] = counts.pair_orders / counts.drink_product_orders
    counts['lift'] = counts.pair_orders * counts.branch.map(totals) / (counts.drink_product_orders * counts.food_product_orders)
    return counts.sort_values('pair_orders', ascending=False)


def predict(train, dates, model):
    if model == 'previous_weekday':
        p = [train[train.index.dayofweek == t.dayofweek].iloc[-1] for t in dates]
    elif model == 'recent_weekday_average':
        p = [train[train.index.dayofweek == t.dayofweek].tail(4).mean() for t in dates]
    elif model == 'trend_weekday':
        fit = LinearRegression().fit(features(train.index, train.index.min()), train.values)
        p = fit.predict(features(dates, train.index.min()))
    else:
        raise ValueError(model)
    return np.maximum(0, np.asarray(p, dtype=float))


def demand(d):
    daily = d.groupby(['date', 'branch']).transaction.nunique().unstack('branch').fillna(0)
    daily = daily.reindex(pd.date_range(d.date.min(), d.date.max()), fill_value=0)
    daily.index.name = 'date'
    pre = daily[daily.index < CUTOFF]
    if len(pre) < 56:
        raise ValueError('At least 56 pre-cutoff days are required for the planned backtests.')
    records = []
    models = ['previous_weekday', 'recent_weekday_average', 'trend_weekday']
    for branch in daily:
        for horizon in [14, 28]:
            # Overlapping origins are diagnostic, not independent experiments.
            for origin in range(28, len(pre) - horizon + 1, 7):
                train = pre[branch].iloc[:origin]
                test = pre[branch].iloc[origin:origin + horizon]
                for model in models:
                    predictions = predict(train, test.index, model)
                    for step, (date, actual, predicted) in enumerate(zip(test.index, test, predictions), 1):
                        records.append(dict(branch=branch, model=model, horizon=horizon,
                            origin=str(train.index.max().date()), step=step, date=date,
                            actual=float(actual), prediction=float(predicted),
                            absolute_error=float(abs(actual-predicted))))
    validation = pd.DataFrame(records)
    scores = validation.groupby(['branch', 'model', 'horizon']).agg(
        mae=('absolute_error', 'mean'), absolute_error=('absolute_error', 'sum'),
        actual_total=('actual', 'sum'), folds=('origin', 'nunique')).reset_index()
    scores['wape'] = scores.absolute_error / scores.actual_total
    selected = scores[scores.horizon == 14].sort_values('mae').groupby('branch').first()
    forecast_rows = []
    dates = pd.date_range(CUTOFF, periods=28)
    for branch in daily:
        model = selected.loc[branch, 'model']
        errors = validation[(validation.branch == branch) & (validation.model == model) &
                            (validation.horizon == 14)].absolute_error
        radius = float(errors.quantile(.90))
        pred = predict(pre[branch], dates, model)
        for date, value in zip(dates, pred):
            forecast_rows.append(dict(branch=branch, date=date, model=model,
                actual=int(daily.loc[date, branch]), prediction=float(value),
                lower_sensitivity_band=max(0, float(value-radius)),
                upper_sensitivity_band=float(value+radius)))
    return daily, validation, scores, pd.DataFrame(forecast_rows)


def preparation(d):
    records = []
    dates = pd.date_range(d.date.min(), d.date.max())
    for (branch, category), g in d[d.category.isin(FOODS)].groupby(['branch', 'category']):
        y = g.groupby('date').quantity.sum().reindex(dates, fill_value=0)
        for date in dates[dates >= CUTOFF]:
            history = y[y.index < date]
            peers = history[history.index.dayofweek == date.dayofweek]
            for policy, prediction in [('previous_weekday', peers.iloc[-1]),
                                       ('recent_4_weekdays', peers.tail(4).mean())]:
                records.append(dict(branch=branch, category=category, date=date,
                    policy=policy, actual=int(y[date]), prediction=float(prediction),
                    absolute_error=float(abs(y[date] - prediction))))
    return pd.DataFrame(records)


def scenarios(opportunities):
    rows = []
    # Select candidates by observed pair count, with economics as a secondary key.
    candidates = opportunities.sort_values(['existing_pair_orders', 'normal_price_contribution'],
        ascending=False).groupby(['branch', 'category']).head(1)
    for _, x in candidates.iterrows():
        for name, attachment, waste, fixed in [('conservative', .02, 20, 100),
                                               ('central', .05, 10, 50),
                                               ('optimistic', .10, 5, 25)]:
            for discount in [0., 1.]:
                # Baseline spontaneous attachment is unobserved: stress assumption.
                result = evaluate(eligible_orders=1000, additional_attachment=attachment,
                    food_price=x.weighted_list_price, food_cost=x.weighted_unit_cost,
                    discount=discount, baseline_attachment=.05,
                    substitution_rate=.10, displaced_contribution=2.,
                    waste_units=waste, extra_cost_per_addition=.25, fixed_cost=fixed)
                rows.append(dict(branch=x.branch, category=x.category, product=x['product'],
                    scenario=name, discount=discount,
                    **{k: v for k, v in result.items() if k not in ['inputs', 'interpretation']}))
    return pd.DataFrame(rows)


def make_figures(daily, forecast, comparison, opportunities, output):
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'figure.dpi': 140, 'axes.spines.top': False,
                         'axes.spines.right': False, 'font.size': 10})
    branches = list(daily.columns)
    fig, axes = plt.subplots(len(branches), 1, figsize=(10, 8), sharex=True)
    for ax, branch in zip(np.atleast_1d(axes), branches):
        f = forecast[forecast.branch == branch]
        ax.plot(daily.loc[:f.date.max()].index, daily.loc[:f.date.max(), branch],
                color='#334155', lw=1, label='Actual daily orders')
        ax.plot(f.date, f.prediction, color='#c25a28', label='Pre-cutoff pattern projection')
        ax.fill_between(f.date, f.lower_sensitivity_band, f.upper_sensitivity_band,
                        color='#c25a28', alpha=.16, label='Historical-error sensitivity band')
        ax.axvline(CUTOFF, color='#64748b', ls='--')
        ax.set_ylabel(f'{branch}\nOrders')
    axes[0].legend(loc='upper left', fontsize=8)
    fig.suptitle('Demand relative to earlier patterns — no causal war estimate')
    fig.tight_layout(); fig.savefig(output / 'demand_projection.png'); plt.close(fig)
    s = comparison.groupby(['category', 'period']).agg(units=('units', 'sum'),
                                                       gross_profit=('gross_profit', 'sum')).reset_index()
    s['profit_per_unit'] = s.gross_profit / s.units
    fig, ax = plt.subplots(figsize=(10, 6))
    for period, marker in [('pre_28_days', 'o'), ('post_28_days', '^')]:
        g = s[s.period == period]
        ax.scatter(g.units, g.profit_per_unit, marker=marker, s=70, label=period)
        for _, r in g.iterrows():
            ax.annotate(r.category, (r.units, r.profit_per_unit), xytext=(4, 4),
                        textcoords='offset points', fontsize=7)
    ax.set(xlabel='Units in matched 28-day window', ylabel='Recorded gross profit per unit (USD)',
           title='Category volume and contribution before and after March 2')
    ax.legend(); fig.tight_layout(); fig.savefig(output / 'category_economics.png'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    for cat, color in [('Bakery', '#c25a28'), ('Meals', '#16877a')]:
        g = opportunities[opportunities.category == cat]
        ax.scatter(g.existing_pair_rate * 100, g.normal_price_contribution,
                   c=color, label=cat, alpha=.7, s=55)
    ax.set(xlabel='Existing product attachment to beverage orders (%)',
           ylabel='Normal-price food contribution (USD/unit)',
           title='Candidate products: historical pairing is not an offer response estimate')
    ax.legend(); fig.tight_layout(); fig.savefig(output / 'offer_tradeoff.png'); plt.close(fig)


def run(data_path=ROOT / 'data/raw/stories_transactions.csv', output=ROOT / 'reports'):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    (output / 'figures').mkdir(exist_ok=True)
    d = load_data(data_path); b = baskets(d)
    q = quality(d, data_path)
    (output / 'data_quality.json').write_text(json.dumps(q, indent=2) + '\n')
    branch_summary(d).to_csv(output / 'branch_economics.csv', index=False)
    comparison = matched_comparison(d)
    comparison.to_csv(output / 'matched_category_comparison.csv', index=False)
    opportunities = product_opportunities(d, b)
    opportunities.to_csv(output / 'product_opportunities.csv', index=False)
    product_pairs(d).to_csv(output / 'observed_product_pairs.csv', index=False)
    bp = b[(b.date >= CUTOFF) & (b.date < CUTOFF + pd.Timedelta(days=28)) & b.drink]
    bp.groupby('branch').agg(drink_orders=('drink', 'size'),
        bakery_attachment=('bakery', 'mean'), meal_attachment=('meal', 'mean'),
        historical_eligible_orders=('eligible', 'sum')).to_csv(output / 'basket_summary.csv')
    bp[bp.eligible].groupby(['branch', 'hour', 'order_type']).size().rename(
        'historical_eligible_orders').to_csv(output / 'eligible_order_segments.csv')
    daily, validation, scores, forecast = demand(d)
    daily.to_csv(output / 'daily_orders.csv')
    validation.to_csv(output / 'forecast_backtest_predictions.csv', index=False)
    scores.to_csv(output / 'forecast_backtest_scores.csv', index=False)
    forecast.to_csv(output / 'demand_projection.csv', index=False)
    fs = forecast.groupby(['branch', 'model']).agg(actual_orders=('actual', 'sum'),
        projected_orders=('prediction', 'sum')).reset_index()
    fs['deviation_fraction'] = fs.actual_orders / fs.projected_orders - 1
    fs.to_csv(output / 'projection_summary.csv', index=False)
    sensitivity = []
    for branch in daily:
        train = daily.loc[daily.index < CUTOFF, branch]
        for model in ['previous_weekday', 'recent_weekday_average', 'trend_weekday']:
            total = float(predict(train, pd.date_range(CUTOFF, periods=28), model).sum())
            actual = int(daily.loc[CUTOFF:CUTOFF + pd.Timedelta(days=27), branch].sum())
            sensitivity.append(dict(branch=branch, model=model, projected_orders=total,
                actual_orders=actual, deviation_fraction=actual / total - 1))
    pd.DataFrame(sensitivity).to_csv(output / 'projection_model_sensitivity.csv', index=False)
    prep = preparation(d)
    prep.groupby(['branch', 'category', 'policy']).agg(mae=('absolute_error', 'mean'),
        absolute_error=('absolute_error', 'sum'), actual_units=('actual', 'sum')).assign(
        wape=lambda x: x.absolute_error / x.actual_units).to_csv(output / 'preparation_backtest.csv')
    scenarios(opportunities).to_csv(output / 'offer_scenarios.csv', index=False)
    sens = []
    for policy, x in [('retain', d), ('exact_deduplicate', d.drop_duplicates())]:
        bs = branch_summary(x); bs['duplicate_policy'] = policy; sens.append(bs)
    pd.concat(sens).to_csv(output / 'duplicate_sensitivity.csv', index=False)
    od = product_opportunities(d.drop_duplicates(), baskets(d.drop_duplicates()))
    od.to_csv(output / 'product_opportunities_deduplicated.csv', index=False)
    _, _, _, fd = demand(d.drop_duplicates())
    fd.groupby(['branch', 'model']).agg(actual_orders=('actual', 'sum'),
        projected_orders=('prediction', 'sum')).to_csv(output / 'projection_deduplicated.csv')
    make_figures(daily, forecast, comparison, opportunities, output / 'figures')
    calendar_results = run_calendar(d, b, output)
    diagnostics = run_diagnostics(d, b, output)
    business = run_business(d, b, calendar_results, diagnostics, output)
    customers = run_customers(d, b, output)
    print(json.dumps(q, indent=2))
    print('\nProjection summary (descriptive, not causal):\n' + fs.to_string(index=False))
    return {'data': d, 'baskets': b, 'opportunities': opportunities,
            'scores': scores, 'forecast': forecast, 'comparison': comparison,
            'calendar': calendar_results, 'diagnostics': diagnostics, 'business': business,
            'customers': customers}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=ROOT / 'data/raw/stories_transactions.csv')
    p.add_argument('--output', type=Path, default=ROOT / 'reports')
    args = p.parse_args(); run(args.data, args.output)


if __name__ == '__main__':
    main()
