"""Harbour's two 15% Cold Coffee/Desserts waves: observational promotion comparison.

Harbour recorded the same 15%-off pattern on March 12-19 (overlapping the
supplied Ramadan/Lent periods) and May 12-19 (outside those periods and away
from the March 2 onset). Garden and Uptown had no comparable recorded pattern. For each
promotion, compare Harbour with the other branches during the promotion and in
the 14 days on either side, then repeat the comparison for every non-promotion
8-day window to describe background relative variation. These overlapping
comparisons are not independent experiments, a confidence interval, or a power
test. Interpretation assumes comparable relative trends between branches; it
does not identify the promotion-period counterfactual.

Usage: python3 scripts/promotion_test.py [--data path/to/stories_transactions.csv]
Writes reports/promotion_natural_experiment.csv and reports/promotion_placebo.csv.
"""
import argparse
import os
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


def make_figure(result, placebo, output):
    """Plot observed comparisons without treating the background as a null test."""
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    starts = [start for start, _ in PROMOS]
    positions = np.arange(len(starts))
    for ax, metric, title in zip(
        axes[:2], ["promo_cat_units", "promo_cat_gross_profit"],
        ["Promoted-category units/day", "Promoted-category gross profit/day (USD)"],
    ):
        rows = result[result.metric == metric].set_index("promo_start").loc[starts]
        for offset, period, color in [(-.25, "pre", "#64748b"), (0, "during", "#16877a"), (.25, "post", "#c58b47")]:
            values = rows[f"harbour_{period}_per_day"]
            bars = ax.bar(positions + offset, values, width=.24, color=color,
                          label={"pre": "Before: 14 days", "during": "During: 8 days", "post": "After: 14 days"}[period])
            ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=7)
        ax.set_xticks(positions, ["March 12–19", "May 12–19"])
        ax.set_title(title, fontsize=10)
        ax.margins(y=.18)
    axes[0].legend(fontsize=7, loc="upper left")
    axes[2].hist(placebo.harbour_vs_others_change_pct, bins=12, color="#94a3b8", edgecolor="white")
    observed = result[result.metric == "promo_cat_units"]
    for (_, row), color, label in zip(observed.iterrows(), ["#16877a", "#c58b47"], ["Observed March", "Observed May"]):
        axes[2].axvline(row.harbour_vs_others_change_pct, color=color, lw=2,
                        label=f"{label}: {row.harbour_vs_others_change_pct:+.1f}%")
    axes[2].set(title="Overlapping background comparisons",
                xlabel="Harbour/other branches relative change (%)", ylabel="Windows")
    axes[2].legend(fontsize=7)
    fig.suptitle("Observational promotion comparison: volume, contribution, and background variation", fontsize=12)
    fig.text(.5, .015,
        "Bars show recorded means, not causal effects. The 60 overlapping windows are descriptive variation, not a confidence interval or power test.",
        ha="center", fontsize=8)
    fig.tight_layout(rect=[0, .07, 1, .93])
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "promotion_comparison.png", dpi=150)
    plt.close(fig)


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
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "promotion_natural_experiment.csv", index=False)
    placebo.to_csv(out / "promotion_placebo.csv", index=False)
    make_figure(result, placebo, out / "figures")

    units_rows = result[result["metric"] == "promo_cat_units"]
    q = placebo["harbour_vs_others_change_pct"].quantile([0.025, 0.975])
    print(f"Break-even unit lift for {DISCOUNT:.0%} off: {break_even_lift:+.1f}%")
    for _, r in units_rows.iterrows():
        print(f"{r.promo_start}: Harbour promoted units/day {r.harbour_pre_per_day:.1f} -> "
              f"{r.harbour_during_per_day:.1f}; relative to other branches {r.harbour_vs_others_change_pct:+.1f}%")
    print(
        f"Overlapping non-promotion comparisons: n={len(placebo)}, "
        f"empirical central 95% range "
        f"{q.iloc[0]:+.1f}% to {q.iloc[1]:+.1f}%. "
        "Descriptive variation only; not a confidence interval or power test."
    )


if __name__ == "__main__":
    main()
