"""Harbour's two 15% Cold Coffee/Desserts promotions as a natural experiment.

Harbour ran the same promotion on March 12-19 (inside the war/Ramadan/Lent
window) and May 12-19 (no calendar event). Garden and Uptown did not. For each
promotion, compare Harbour with the other branches during the promotion and in
the 14 days on either side, then repeat the comparison for every non-promotion
8-day window (placebo) to see how large a "lift" ordinary noise produces.

Usage: python3 scripts/promotion_test.py [--data path/to/stories_transactions.csv]
Writes reports/promotion_natural_experiment.csv and reports/promotion_placebo.csv.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROMOS = [("2026-03-12", "2026-03-19"), ("2026-05-12", "2026-05-19")]
PROMO_CATEGORIES = ["Cold Coffee", "Desserts"]
DISCOUNT = 0.15
SIDE_DAYS = 14
PROMO_DAYS = 8


def daily_by_group(df):
    df = df.assign(
        group=np.where(df["Branch"] == "Harbour", "Harbour", "Garden+Uptown"),
        promo_cat=df["Category"].isin(PROMO_CATEGORIES),
        discount_usd=df["Quantity"] * df["Unit Price (USD)"] - df["Line Revenue (USD)"],
    )
    pc = df[df["promo_cat"]]
    out = pd.concat(
        {
            "promo_cat_units": pc.groupby(["Date", "group"])["Quantity"].sum(),
            "promo_cat_gross_profit": pc.groupby(["Date", "group"])["Line Gross Profit (USD)"].sum(),
            "promo_cat_discount_usd": pc.groupby(["Date", "group"])["discount_usd"].sum(),
            "other_units": df[~df["promo_cat"]].groupby(["Date", "group"])["Quantity"].sum(),
            "orders": df.groupby(["Date", "group"])["Transaction ID"].nunique(),
            "gross_profit": df.groupby(["Date", "group"])["Line Gross Profit (USD)"].sum(),
        },
        axis=1,
    )
    return out.unstack("group").fillna(0)


def relative_change(daily, start, metric):
    """Harbour/other ratio during the window vs the mean ratio in the 14 days either side."""
    end = start + pd.Timedelta(days=PROMO_DAYS - 1)
    pre = daily.loc[start - pd.Timedelta(days=SIDE_DAYS): start - pd.Timedelta(days=1)]
    during = daily.loc[start:end]
    post = daily.loc[end + pd.Timedelta(days=1): end + pd.Timedelta(days=SIDE_DAYS)]
    if len(pre) < SIDE_DAYS or len(post) < SIDE_DAYS or len(during) < PROMO_DAYS:
        return None
    ratio = lambda b: b[(metric, "Harbour")].sum() / b[(metric, "Garden+Uptown")].sum()
    base = (ratio(pre) + ratio(post)) / 2
    return {
        "harbour_pre_per_day": pre[(metric, "Harbour")].mean(),
        "harbour_during_per_day": during[(metric, "Harbour")].mean(),
        "harbour_post_per_day": post[(metric, "Harbour")].mean(),
        "others_pre_per_day": pre[(metric, "Garden+Uptown")].mean(),
        "others_during_per_day": during[(metric, "Garden+Uptown")].mean(),
        "others_post_per_day": post[(metric, "Garden+Uptown")].mean(),
        "harbour_vs_others_change_pct": 100 * (ratio(during) / base - 1),
        "harbour_during_total": during[(metric, "Harbour")].sum(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=ROOT / "data/raw/stories_transactions.csv")
    args = parser.parse_args()
    df = pd.read_csv(args.data, parse_dates=["Date"])
    daily = daily_by_group(df)

    rows = []
    for start, end in PROMOS:
        for metric in ["promo_cat_units", "other_units", "orders", "promo_cat_gross_profit",
                       "gross_profit", "promo_cat_discount_usd"]:
            rows.append({"promo_start": start, "promo_end": end, "metric": metric,
                         **relative_change(daily, pd.Timestamp(start), metric)})
    result = pd.DataFrame(rows)

    # Volume lift needed for the discounted price to earn the same gross profit as full price.
    harbour = df[(df["Branch"] == "Harbour") & df["Category"].isin(PROMO_CATEGORIES)]
    units = harbour["Quantity"].sum()
    price = (harbour["Unit Price (USD)"] * harbour["Quantity"]).sum() / units
    cost = (harbour["Unit Cost (USD)"] * harbour["Quantity"]).sum() / units
    break_even_lift = 100 * ((price - cost) / ((1 - DISCOUNT) * price - cost) - 1)
    result["break_even_unit_lift_pct"] = break_even_lift

    promo_days = set()
    for start, end in PROMOS:
        promo_days |= set(pd.date_range(start, end))
    placebo = []
    for start in daily.index:
        span = pd.date_range(start - pd.Timedelta(days=SIDE_DAYS),
                             start + pd.Timedelta(days=PROMO_DAYS - 1 + SIDE_DAYS))
        if promo_days & set(span):
            continue
        r = relative_change(daily, start, "promo_cat_units")
        if r is not None:
            placebo.append({"window_start": start.date(),
                            "harbour_vs_others_change_pct": r["harbour_vs_others_change_pct"]})
    placebo = pd.DataFrame(placebo)

    out = ROOT / "reports"
    result.to_csv(out / "promotion_natural_experiment.csv", index=False)
    placebo.to_csv(out / "promotion_placebo.csv", index=False)

    units_rows = result[result["metric"] == "promo_cat_units"]
    q = placebo["harbour_vs_others_change_pct"].quantile([0.025, 0.975])
    print(f"Break-even unit lift for {DISCOUNT:.0%} off: {break_even_lift:+.1f}%")
    for _, r in units_rows.iterrows():
        print(f"{r.promo_start}: Harbour promoted units/day {r.harbour_pre_per_day:.1f} -> "
              f"{r.harbour_during_per_day:.1f}; relative to other branches {r.harbour_vs_others_change_pct:+.1f}%")
    print(f"Placebo windows: n={len(placebo)}, 95% range {q.iloc[0]:+.1f}% to {q.iloc[1]:+.1f}%, "
          f"max {placebo['harbour_vs_others_change_pct'].max():+.1f}%")


if __name__ == "__main__":
    main()
