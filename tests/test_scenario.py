import pytest
from stories.scenario import evaluate


def test_economics_include_leakage_waste_and_substitution():
    r = evaluate(eligible_orders=1000, additional_attachment=.1, food_price=10,
                 food_cost=4, discount=1, baseline_attachment=.2,
                 substitution_rate=.25, displaced_contribution=2,
                 waste_units=10, extra_cost_per_addition=.5, fixed_cost=30)
    # 100 additions * $4 net contribution - $200 leakage - $40 waste - $30 fixed.
    assert r['incremental_gross_profit_after_assumed_costs_usd'] == 130
    assert r['break_even_additional_attachment'] == pytest.approx(.0675)


def test_nonpositive_contribution_has_no_profitable_threshold():
    r = evaluate(eligible_orders=100, additional_attachment=.1, food_price=2, food_cost=3)
    assert r['break_even_additional_attachment'] is None
    assert not r['break_even_feasible']


def test_impossible_rates_are_rejected():
    with pytest.raises(ValueError):
        evaluate(eligible_orders=100, additional_attachment=.8,
                 baseline_attachment=.3, food_price=10, food_cost=4)
