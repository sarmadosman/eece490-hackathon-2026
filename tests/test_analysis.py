import numpy as np
import pandas as pd
import pytest

from stories.analysis import CUTOFF, baskets, demand, forecast_holdout, predict


def test_projection_cannot_see_post_cutoff_outcomes():
    dates = pd.date_range('2026-01-01', '2026-03-29')
    rows = [dict(date=t, branch='Test', transaction=f'{t.date()}-{j}')
            for i, t in enumerate(dates) for j in range(10 + i // 7)]
    original = pd.DataFrame(rows)
    extra = original[original.date >= CUTOFF].copy()
    extra['transaction'] += '-additional'
    daily_a, validation, scores_a, a = demand(original)
    daily_b, _, scores_b, b = demand(pd.concat([original, extra]))
    np.testing.assert_allclose(a.prediction, b.prediction)
    assert (b.actual > a.actual).all()
    assert (validation.date < CUTOFF).all()
    assert (pd.to_datetime(validation.origin) < validation.date).all()
    test_a, _ = forecast_holdout(daily_a, scores_a)
    test_b, _ = forecast_holdout(daily_b, scores_b)
    # Alter every held-out outcome: neither selection nor any candidate forecast
    # may change. Earlier test days must not leak into later test predictions.
    pd.testing.assert_frame_equal(scores_a, scores_b)
    np.testing.assert_allclose(test_a.prediction, test_b.prediction)
    pd.testing.assert_series_equal(test_a.selected_on_validation, test_b.selected_on_validation)
    assert (test_b.actual > test_a.actual).all()
    selected_test = test_a[test_a.selected_on_validation]
    np.testing.assert_allclose(selected_test.prediction, a.prediction)


def test_holdout_metrics_match_manual_same_weekday_baseline():
    dates = pd.date_range('2026-01-01', '2026-03-29')
    # A repeating weekday pattern then a ten-order step, unseen in training.
    daily = pd.DataFrame({'Test': dates.dayofweek + 1.}, index=dates)
    daily.loc[daily.index >= CUTOFF, 'Test'] += 10
    validation = pd.DataFrame([
        dict(branch='Test', model=model, horizon=14, mae=mae)
        for model, mae in [('previous_weekday', 2), ('recent_weekday_average', 1), ('trend_weekday', 3)]
    ])
    predictions, scores = forecast_holdout(daily, validation)
    baseline = scores[scores.model == 'previous_weekday'].iloc[0]
    assert baseline.mae == pytest.approx(10)
    assert baseline.absolute_error == pytest.approx(280)
    assert baseline.wape == pytest.approx(280 / 392)
    assert baseline.bias == pytest.approx(-10)
    assert baseline.mae_reduction_vs_baseline_pct == pytest.approx(0)
    assert scores.loc[scores.selected_on_validation, 'model'].tolist() == ['recent_weekday_average']
    assert len(predictions) == 3 * 28
    assert (predictions.train_end < predictions.date).all()
    assert predictions.train_end.eq(pd.Timestamp('2026-03-01')).all()
    assert predictions.date.min() == CUTOFF
    assert predictions.date.max() == pd.Timestamp('2026-03-29')
    with pytest.raises(ValueError, match='full March 2–29 holdout'):
        forecast_holdout(daily.iloc[:-1], validation)


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
