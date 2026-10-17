import numpy as np
import pandas as pd
import pytest

from stories.calendar import PHASES, annotate, boundary_comparisons, model_associations


def test_calendar_boundaries_are_inclusive_and_exhaustive():
    dates = pd.to_datetime(['2026-02-16','2026-02-17','2026-02-18','2026-03-01',
                            '2026-03-02','2026-03-18','2026-03-19','2026-04-02','2026-04-03'])
    x = annotate(pd.DataFrame({'date': dates}))
    assert x.ramadan.tolist() == [0,1,1,1,1,1,0,0,0]
    assert x.lent.tolist() == [0,0,1,1,1,1,1,1,0]
    assert x.phase.tolist() == [PHASES[i] for i in [0,1,2,2,3,3,4,4,5]]


def synthetic_daily():
    dates = pd.date_range('2026-01-01', '2026-06-30')
    x = annotate(pd.DataFrame({'date': dates, 'branch': 'All branches'}))
    t = (x.date - dates.min()).dt.days
    x['orders'] = np.exp(4 + .001 * t + .08*x.ramadan - .04*x.lent + .12*x.post_march2
                          + .05*x.date.dt.dayofweek.eq(1))
    for col in ['evening_share','midday_share','gross_profit_per_order','bakery_attachment',
                'meal_attachment','breakfast_share','discounted_unit_share']:
        x[col] = .5
    for col in ['gross_profit','revenue','evening_orders','midday_orders','takeaway_orders',
                'breakfast_orders','drink_orders','bakery_drink_orders','meal_drink_orders',
                'eligible_orders','units','discounted_units']:
        x[col] = x.orders * .5
    return x


def test_march2_seven_day_comparison_holds_calendar_flags_constant():
    x = boundary_comparisons(synthetic_daily())
    row = x[(x.event == 'March 2') & (x.window_days_each_side == 7) & (x.metric == 'orders')].iloc[0]
    assert row.pre_ramadan_days == row.post_ramadan_days == 7
    assert row.pre_lent_days == row.post_lent_days == 7
    assert row.pre_postmarch2_days == 0 and row.post_postmarch2_days == 7


def test_adjusted_model_recovers_known_associations_without_conflating_events():
    a, diagnostics = model_associations(synthetic_daily())
    x = a[(a.metric == 'orders') & (a.specification == 'through_June_linear')].set_index('term')
    for term, beta in [('ramadan', .08), ('lent', -.04), ('post_march2', .12)]:
        assert x.loc[term, 'association'] == pytest.approx(100*np.expm1(beta), abs=1e-9)
    assert (diagnostics.design_rank == diagnostics.design_columns).all()
    assert not a.causal.any()
