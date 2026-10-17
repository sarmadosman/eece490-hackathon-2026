"""Conditional economics; conversion inputs are assumptions, never predictions."""
import argparse
import json


def evaluate(*, eligible_orders, additional_attachment, food_price, food_cost,
             discount=0.0, baseline_attachment=0.0, substitution_rate=0.0,
             displaced_contribution=0.0, waste_units=0.0, extra_cost_per_addition=0.0,
             fixed_cost=0.0):
    """Rates use eligible orders as denominator; baseline and additional are disjoint.

    baseline_attachment represents purchases that would occur without the offer but
    receive its discount. Substitution is a fraction of additional purchases.
    Waste is additional unsold units, charged at recorded unit cost.
    """
    values = locals().copy()
    if any(v < 0 for v in values.values()):
        raise ValueError('Inputs must be nonnegative.')
    if eligible_orders <= 0:
        raise ValueError('eligible_orders must be positive.')
    if any(r > 1 for r in (additional_attachment, baseline_attachment, substitution_rate)):
        raise ValueError('Rates must lie between zero and one.')
    if additional_attachment + baseline_attachment > 1:
        raise ValueError('Baseline plus additional attachment cannot exceed one.')
    if discount > food_price:
        raise ValueError('Discount cannot exceed food price.')
    contribution = (food_price - food_cost - discount - extra_cost_per_addition
                    - substitution_rate * displaced_contribution)
    leakage = eligible_orders * baseline_attachment * discount
    overhead = waste_units * food_cost + fixed_cost
    profit = eligible_orders * additional_attachment * contribution - leakage - overhead
    threshold = ((leakage + overhead) / (eligible_orders * contribution)
                 if contribution > 0 else None)
    return {
        'inputs': values,
        'net_contribution_per_addition_usd': contribution,
        'additional_purchases': eligible_orders * additional_attachment,
        'discount_leakage_usd': leakage,
        'incremental_gross_profit_after_assumed_costs_usd': profit,
        'incremental_profit_per_eligible_order_usd': profit / eligible_orders,
        'break_even_additional_attachment': threshold,
        'break_even_feasible': threshold is not None and threshold <= 1 - baseline_attachment,
        'interpretation': 'Conditional scenario, not measured uplift or net company profit.',
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name, default in [('eligible-orders', 1000), ('additional-attachment', .05),
                          ('food-price', None), ('food-cost', None), ('discount', 0.),
                          ('baseline-attachment', 0.), ('substitution-rate', 0.),
                          ('displaced-contribution', 0.), ('waste-units', 0.),
                          ('extra-cost-per-addition', 0.), ('fixed-cost', 0.)]:
        p.add_argument('--' + name, type=float, default=default, required=default is None)
    print(json.dumps(evaluate(**vars(p.parse_args())), indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
