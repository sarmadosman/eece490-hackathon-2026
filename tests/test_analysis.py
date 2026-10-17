import numpy as np
import pandas as pd

from stories.analysis import CUTOFF, baskets, demand, predict


def test_projection_cannot_see_post_cutoff_outcomes():
    dates = pd.date_range('2026-01-01', '2026-03-29')
    rows = [dict(date=t, branch='Test', transaction=f'{t.date()}-{j}')
            for i, t in enumerate(dates) for j in range(10 + i // 7)]
    original = pd.DataFrame(rows)
    extra = original[original.date >= CUTOFF].copy()
    extra['transaction'] += '-additional'
    _, validation, _, a = demand(original)
    _, _, _, b = demand(pd.concat([original, extra]))
    np.testing.assert_allclose(a.prediction, b.prediction)
    assert (b.actual > a.actual).all()
    assert (validation.date < CUTOFF).all()
    assert (pd.to_datetime(validation.origin) < validation.date).all()


def test_previous_weekday_is_frozen_at_forecast_origin():
    index = pd.date_range('2026-01-01', periods=28)
    train = pd.Series(np.arange(28), index=index)
    p = predict(train, pd.date_range('2026-01-29', periods=14), 'previous_weekday')
    np.testing.assert_array_equal(p[:7], np.arange(21, 28))
    np.testing.assert_array_equal(p[7:], p[:7])


def test_basket_eligibility_excludes_food_already_present():
    d = pd.DataFrame({'transaction': ['a', 'a', 'b'], 'category': ['Hot Coffee', 'Bakery', 'Cold Coffee']})
    for key, value in {'date': CUTOFF, 'branch': 'Harbour', 'time': '12:00:00',
                       'order_type': 'Takeaway', 'revenue': 3., 'gross_profit': 2.}.items():
        d[key] = value
    b = baskets(d)
    assert b.loc['a', 'drink'] and not b.loc['a', 'eligible']
    assert b.loc['b', 'eligible']
