import pandas as pd
import pytest

from stories.diagnostics import category_windows, weekday_hour_rates


def test_window_metrics_keep_volume_unit_profit_and_discount_denominators_distinct():
    dates = pd.date_range('2026-02-23', '2026-03-08')
    d = pd.DataFrame({'date':dates,'branch':'Harbour','category':'Meals'})
    post = d.date >= pd.Timestamp('2026-03-02')
    d['quantity'] = 1 + post.astype(int)
    d['revenue'] = d.quantity * 10
    d['gross_profit'] = d.quantity * 5
    d['discount'] = post.astype(float) * .1
    summary,changes,exposure = category_windows(d,widths=(7,))
    c = changes[changes.branch == 'All branches'].iloc[0]
    assert c.units_per_day_change_pct == pytest.approx(100)
    assert c.gross_profit_per_day_change_pct == pytest.approx(100)
    assert c.gross_profit_per_unit_change_pct == pytest.approx(0)
    assert c.discounted_unit_share_change_pp == pytest.approx(100)
    assert c.unit_share_change_pp == pytest.approx(0)
    assert exposure.ramadan_days.tolist() == [7,7]
    assert exposure.lent_days.tolist() == [7,7]


def test_hour_rates_include_zero_cells_and_divide_by_weekday_occurrences():
    b = pd.DataFrame({'date':pd.to_datetime(['2026-02-02','2026-02-09']),
                      'branch':['Harbour','Harbour'],'hour':[9,10]})
    d = pd.DataFrame({'date':pd.date_range('2026-02-02','2026-03-29')})
    rates = weekday_hour_rates(d,b)
    x = rates[(rates.scope=='Before: 28 days') & (rates.weekday==0)].set_index('hour')
    assert x.loc[9,'orders_per_weekday_occurrence'] == pytest.approx(.25)
    assert x.loc[10,'orders_per_weekday_occurrence'] == pytest.approx(.25)
    zero = rates[(rates.scope=='Before: 28 days') & (rates.weekday==1)]
    assert zero.orders.eq(0).all()
    assert zero.orders_per_weekday_occurrence.eq(0).all()
