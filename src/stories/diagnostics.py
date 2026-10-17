"""Selected diagnostics adapted from the two supplied exploratory notebooks."""
from pathlib import Path

import numpy as np
import pandas as pd

from .calendar import RAMADAN_START, RAMADAN_END, LENT_START, LENT_END, CHANGE_DATE


def calendar_exposure(start, end):
    dates = pd.date_range(start, end)
    return {'ramadan_days': int(((dates >= RAMADAN_START) & (dates <= RAMADAN_END)).sum()),
            'lent_days': int(((dates >= LENT_START) & (dates <= LENT_END)).sum())}


def category_windows(d, cutoff=CHANGE_DATE, widths=(14, 28, 42)):
    summaries, exposure = [], []
    for width in widths:
        start, end = cutoff-pd.Timedelta(days=width), cutoff+pd.Timedelta(days=width-1)
        if start < d.date.min() or end > d.date.max():
            continue
        for period, left, right in [('Before', start, cutoff-pd.Timedelta(days=1)),
                                    ('After', cutoff, end)]:
            exposure.append(dict(days_each_side=width, period=period, start=left, end=right,
                                 **calendar_exposure(left, right)))
            x = d[d.date.between(left, right)].copy()
            x['discounted_units'] = x.quantity * x.discount.gt(0)
            for branch in ['All branches', *sorted(d.branch.unique())]:
                items = x if branch == 'All branches' else x[x.branch == branch]
                s = items.groupby('category').agg(units=('quantity', 'sum'),
                    revenue=('revenue', 'sum'), gross_profit=('gross_profit', 'sum'),
                    discounted_units=('discounted_units', 'sum')).reset_index()
                s['units_per_day'] = s.units / width
                s['gross_profit_per_day'] = s.gross_profit / width
                s['gross_profit_per_unit'] = s.gross_profit / s.units
                s['unit_share'] = s.units / s.units.sum()
                s['discounted_unit_share'] = s.discounted_units / s.units
                s['branch'], s['period'], s['days_each_side'] = branch, period, width
                summaries.append(s)
    s = pd.concat(summaries, ignore_index=True)
    keys = ['branch', 'category', 'days_each_side']
    before = s[s.period == 'Before'].set_index(keys)
    after = s[s.period == 'After'].set_index(keys)
    change = pd.DataFrame(index=before.index.union(after.index))
    for metric in ['units_per_day', 'gross_profit_per_day', 'gross_profit_per_unit']:
        change[metric + '_change_pct'] = 100 * (after[metric] / before[metric].replace(0, np.nan)-1)
    for metric in ['unit_share', 'discounted_unit_share']:
        change[metric + '_change_pp'] = 100 * (after[metric] - before[metric])
    return s, change.reset_index(), pd.DataFrame(exposure)


def same_product_economics(d, reference='Harbour'):
    s = d.assign(list_value=d.price*d.quantity, cost_value=d.cost*d.quantity).groupby(
        ['branch', 'product', 'category']).agg(units=('quantity', 'sum'),
        list_value=('list_value', 'sum'), cost_value=('cost_value', 'sum'),
        price_values=('price', 'nunique'), cost_values=('cost', 'nunique')).reset_index()
    s['weighted_list_price'] = s.list_value / s.units
    s['weighted_unit_cost'] = s.cost_value / s.units
    ref = s[s.branch == reference][['product','category','weighted_list_price','weighted_unit_cost']]
    ref = ref.rename(columns={'weighted_list_price':'reference_price', 'weighted_unit_cost':'reference_cost'})
    s = s.merge(ref, on=['product','category'], how='left', validate='many_to_one')
    s['price_ratio_to_reference'] = s.weighted_list_price / s.reference_price.replace(0,np.nan)
    s['cost_ratio_to_reference'] = s.weighted_unit_cost / s.reference_cost.replace(0,np.nan)
    s['reference_branch'] = reference
    return s


def weekday_hour_rates(d, b):
    rows = []
    scopes = [('Full history', d.date.min(), d.date.max()),
              ('Before: 28 days', CHANGE_DATE-pd.Timedelta(days=28), CHANGE_DATE-pd.Timedelta(days=1)),
              ('After: 28 days', CHANGE_DATE, CHANGE_DATE+pd.Timedelta(days=27))]
    hours = range(int(b.hour.min()), int(b.hour.max())+1)
    for scope, start, end in scopes:
        dates = pd.date_range(start,end)
        days = pd.Series(dates.dayofweek).value_counts().reindex(range(7), fill_value=0)
        for branch, g in b[b.date.between(start,end)].groupby('branch'):
            counts = g.groupby([g.date.dt.dayofweek,g.hour]).size()
            for weekday in range(7):
                for hour in hours:
                    count = int(counts.get((weekday,hour),0))
                    rows.append(dict(branch=branch, scope=scope, weekday=weekday, hour=hour,
                        orders=count, weekday_occurrences=int(days[weekday]),
                        orders_per_weekday_occurrence=count/days[weekday] if days[weekday] else np.nan))
    return pd.DataFrame(rows)


def alternative_cutoffs(d, b, width=28):
    dates = pd.date_range(d.date.min()+pd.Timedelta(days=width),
                         d.date.max()-pd.Timedelta(days=width-1),freq='7D')
    dates = dates.union(pd.DatetimeIndex([CHANGE_DATE])).sort_values()
    rows = []
    for branch in ['All branches', *sorted(d.branch.unique())]:
        orders = b if branch == 'All branches' else b[b.branch == branch]
        for cutoff in dates:
            before = orders[orders.date.between(cutoff-pd.Timedelta(days=width),cutoff-pd.Timedelta(days=1))]
            after = orders[orders.date.between(cutoff,cutoff+pd.Timedelta(days=width-1))]
            rows.append(dict(branch=branch,cutoff=cutoff,days_each_side=width,
                before_orders=len(before),after_orders=len(after),
                order_change_pct=100*(len(after)/len(before)-1) if len(before) else np.nan))
    return pd.DataFrame(rows)


def figures(s, change, rates, cost, cutoff, weekly, products, output):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    categories = sorted(s.category.unique())
    branches = sorted(rates.branch.unique())
    colors = {c: plt.get_cmap('tab10')(i) for i,c in enumerate(categories)}
    handles = [Line2D([0],[0],marker='o',color=colors[c],ls='',label=f'{i+1}  {c}')
               for i,c in enumerate(categories)]
    pair = s[(s.branch == 'All branches') & (s.days_each_side == 28)]
    fig,axes = plt.subplots(1,2,figsize=(12,6),sharex=True,sharey=True)
    for ax,period in zip(axes,['Before','After']):
        g = pair[pair.period == period].set_index('category')
        for i,cat in enumerate(categories):
            r = g.loc[cat]
            ax.scatter(r.units_per_day,r.gross_profit_per_day,color=colors[cat],s=70)
            ax.annotate(str(i+1),(r.units_per_day,r.gross_profit_per_day),xytext=(6,5),textcoords='offset points')
        ax.set(title=period,xlabel='Units per calendar day',xlim=(0,pair.units_per_day.max()*1.2),
               ylim=(0,pair.gross_profit_per_day.max()*1.2))
    axes[0].set_ylabel('Recorded gross profit per calendar day (USD)')
    fig.legend(handles=handles,loc='lower center',ncol=3,frameon=False)
    fig.suptitle('Category contribution around March 2: equal 28-day windows\nCalendar-unadjusted descriptive comparison',fontsize=12)
    fig.tight_layout(rect=[0,.16,1,.93]);fig.savefig(output/'category_daily_contribution.png',dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,3,figsize=(13,6),sharey=True)
    x=change[(change.days_each_side==28)&(change.branch!='All branches')]
    for ax,(metric,title,unit) in zip(axes,[
        ('units_per_day_change_pct','Units/day change','%'),
        ('gross_profit_per_unit_change_pct','Gross profit/unit change','%'),
        ('discounted_unit_share_change_pp','Discounted-unit share change','percentage points')]):
        values=x.pivot(index='category',columns='branch',values=metric).reindex(index=categories,columns=branches)
        limit=max(float(np.nanmax(abs(values.to_numpy()))),.01)
        im=ax.imshow(values,aspect='auto',cmap='RdBu_r',vmin=-limit,vmax=limit)
        for i in range(len(categories)):
            for j in range(len(branches)):
                v=values.iloc[i,j]
                if pd.notna(v):ax.text(j,i,f'{v:.1f}',ha='center',va='center',fontsize=8,
                    color='white' if abs(v)>.65*limit else 'black')
        ax.set_xticks(range(len(branches)),branches);ax.set_yticks(range(len(categories)),categories)
        ax.set_title(title,fontsize=10);fig.colorbar(im,ax=ax,shrink=.7,label=unit)
    fig.suptitle('Branch/category changes: February 2–March 1 vs March 2–29\nSeparate volume, contribution, and discounts; colors do not imply significance',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.90]);fig.savefig(output/'branch_category_changes.png',dpi=150);plt.close(fig)

    scopes=rates.scope.unique()
    fig,axes=plt.subplots(len(branches),len(scopes),figsize=(15,8),squeeze=False)
    limit=float(rates.orders_per_weekday_occurrence.max())
    for i,branch in enumerate(branches):
        for j,scope in enumerate(scopes):
            ax=axes[i,j]
            values=rates[(rates.branch==branch)&(rates.scope==scope)].pivot(index='weekday',columns='hour',values='orders_per_weekday_occurrence')
            im=ax.imshow(values,aspect='auto',cmap='YlGnBu',vmin=0,vmax=limit)
            ax.set_xticks(range(0,len(values.columns),2),values.columns[::2]);ax.set_yticks(range(7),['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
            ax.set_title(f'{branch} — {scope}',fontsize=9)
    fig.suptitle('Orders per weekday occurrence by hour\nShared scale; recorded sales do not measure capacity, opening hours, or unmet demand',fontsize=12)
    fig.tight_layout(rect=[0,0,.91,.91]);fig.colorbar(im,ax=axes.ravel().tolist(),fraction=.025,pad=.02,label='Orders / weekday occurrence')
    fig.savefig(output/'weekday_hour_comparison.png',dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for branch,g in weekly.groupby('branch'):
        axes[0].plot(g.week,100*g.discounted_order_share,label=branch)
    axes[0].axvline(CHANGE_DATE,color='#c25a28',ls='--')
    axes[0].set(title='Discounted-order exposure by week',ylabel='Orders with any discounted line (%)');axes[0].legend(fontsize=8)
    c=cutoff[cutoff.branch=='All branches']
    axes[1].plot(c.cutoff,c.order_change_pct,marker='.',color='#334155')
    p=c[c.cutoff==CHANGE_DATE];axes[1].scatter(p.cutoff,p.order_change_pct,c='#c25a28',s=65,label='March 2')
    axes[1].axhline(0,color='#64748b',lw=1);axes[1].legend()
    axes[1].set(title='28-day order change at alternative cutoffs',ylabel='After versus before (%)')
    for ax in axes:ax.tick_params(axis='x',rotation=30)
    fig.suptitle('Alternative explanations: promotions and broad growth\nOverlapping cutoff windows are descriptive checks, not independent placebo experiments',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.89]);fig.savefig(output/'promotions_and_cutoffs.png',dpi=150);plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for ax,metric,title in zip(axes,['price_ratio_to_reference','cost_ratio_to_reference'],['Same-product list-price ratio','Same-product recorded-cost ratio']):
        data=[cost.loc[cost.branch==branch,metric].dropna() for branch in branches]
        ax.boxplot(data,tick_labels=branches,showfliers=True)
        ax.axhline(1,color='#64748b',ls='--');ax.set(title=title,ylabel='Ratio to Harbour (1 = equal)')
    fig.suptitle('Full-history same-product comparisons\nSystematic recorded differences do not establish attainable procurement savings',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.89]);fig.savefig(output/'same_product_economics.png',dpi=150);plt.close(fig)

    top=products.nlargest(12,'gross_profit').sort_values('gross_profit')
    fig,ax=plt.subplots(figsize=(9,6));ax.barh(top['product'],top.gross_profit,color='#16877a')
    ax.set(title='Full-history product contribution: context for beverage traffic',xlabel='Recorded gross profit (USD)')
    fig.tight_layout();fig.savefig(output/'top_product_contribution.png',dpi=150);plt.close(fig)


def run_diagnostics(d,b,output):
    output=Path(output)
    summary,change,exposure=category_windows(d)
    cost=same_product_economics(d)
    rates=weekday_hour_rates(d,b)
    cutoff=alternative_cutoffs(d,b)
    weekly=b.assign(discounted=b.index.isin(d.loc[d.discount.gt(0),'transaction']),
                    week=b.date.dt.to_period('W-SUN').dt.start_time).groupby(['week','branch']).agg(
                        orders=('branch','size'),days_observed=('date','nunique'),
                        discounted_order_share=('discounted','mean')).reset_index()
    products=d.groupby(['product','category']).agg(units=('quantity','sum'),revenue=('revenue','sum'),
                                                  gross_profit=('gross_profit','sum')).reset_index()
    products['gross_profit_per_unit']=products.gross_profit/products.units
    products=products.sort_values('gross_profit',ascending=False)
    for name,table in [('category_window_summary',summary),('category_window_changes',change),
                       ('window_calendar_exposure',exposure),('same_product_economics',cost),
                       ('weekday_hour_rates',rates),('alternative_cutoff_comparisons',cutoff),
                       ('weekly_discounted_order_share',weekly),('product_contribution_ranking',products)]:
        table.to_csv(output/f'{name}.csv',index=False)
    figures(summary,change,rates,cost,cutoff,weekly,products,output/'figures')
    return {'summary':summary,'changes':change,'calendar_exposure':exposure,'cost':cost,
            'rates':rates,'cutoffs':cutoff,'weekly':weekly,'products':products}
