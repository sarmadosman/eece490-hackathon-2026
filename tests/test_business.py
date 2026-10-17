import pandas as pd
import pytest

from stories.business import event_comparisons, branch_phase_economics


def example_items():
    dates=pd.date_range('2026-02-01','2026-04-30')
    d=pd.DataFrame({'date':dates,'branch':'Harbour','product':'Test Latte','category':'Cold Coffee'})
    post=d.date.ge('2026-03-02')
    d['quantity']=2+2*post.astype(int)
    d['price']=5.
    d['cost']=2.
    d['discount']=.25*post.astype(int)
    d['revenue']=d.quantity*d.price*(1-d.discount)
    d['gross_profit']=d.revenue-d.quantity*d.cost
    d['transaction']=d.date.astype(str)
    return d,d[['date','branch']].copy()


def test_item_price_contribution_and_volume_thresholds_have_distinct_denominators():
    d,b=example_items()
    _,changes,branches,_=event_comparisons(d,b,widths=(7,))
    row=changes[(changes.event=='March 2 / war context')&(changes.branch=='Harbour')].iloc[0]
    assert row.units_before == 14 and row.units_after == 28
    assert row.weighted_list_price_before == row.weighted_list_price_after == 5
    assert row.realized_price_per_unit_after == 3.75
    assert row.gross_profit_per_unit_after == 1.75
    assert row.gross_profit_per_day_change_pct == pytest.approx(100*(49/42-1))
    assert row.gross_profit_neutral_volume_change_pct == pytest.approx(100*(3/1.75-1))
    assert row.volume_loss_tolerable_at_full_list_price_pct == pytest.approx(100*(1-1.75/3))
    assert row.listed_price_values_in_history_after == 1
    assert row.small_base_either_period


def test_each_calendar_event_is_exported_with_overlap_exposure():
    d,b=example_items()
    _,_,_,exposure=event_comparisons(d,b,widths=(7,))
    assert set(exposure.event)=={'March 2 / war context','Ramadan start','Lent start','Ramadan end','Lent end'}
    x=exposure[exposure.event=='Lent start'].set_index('period')
    assert x.loc['Before','ramadan_days']==1
    assert x.loc['After','ramadan_days']==7
    assert x.loc['Before','lent_days']==0
    assert x.loc['After','lent_days']==7


def test_branch_margin_uses_aggregate_revenue_denominator():
    phases=pd.DataFrame([dict(branch='Test',phase='test',days=2,orders_per_day=3,
        revenue=100,gross_profit=40,gross_profit_per_order=40/6)])
    x=branch_phase_economics(phases).iloc[0]
    assert x.gross_margin==.4
    assert x.gross_profit_per_day==20
