"""Comparison-led business evidence: items, realized prices, and branch economics."""
from pathlib import Path

import numpy as np
import pandas as pd

from .calendar import CHANGE_DATE, RAMADAN_START, RAMADAN_END, LENT_START, LENT_END
from .diagnostics import calendar_exposure

EVENTS = [('March 2 / war context', CHANGE_DATE), ('Ramadan start', RAMADAN_START),
          ('Lent start', LENT_START), ('Ramadan end', RAMADAN_END+pd.Timedelta(days=1)),
          ('Lent end', LENT_END+pd.Timedelta(days=1))]


def event_comparisons(d, b, widths=(7, 14, 28)):
    """Equal-window comparisons; flags disclose overlapping calendar exposure."""
    items, branches, exposure = [], [], []
    variation = d.groupby(['branch','product']).price.nunique()
    for event, cutoff in EVENTS:
        for width in widths:
            start, end = cutoff-pd.Timedelta(days=width), cutoff+pd.Timedelta(days=width-1)
            if start < d.date.min() or end > d.date.max():
                continue
            for period,left,right in [('Before',start,cutoff-pd.Timedelta(days=1)),('After',cutoff,end)]:
                meta = dict(event=event, cutoff=cutoff, days_each_side=width, period=period)
                exposure.append(dict(**meta,start=left,end=right,**calendar_exposure(left,right),
                    post_march2_days=int((pd.date_range(left,right)>=CHANGE_DATE).sum())))
                x = d[d.date.between(left,right)]
                tickets = b[b.date.between(left,right)]
                for branch in ['All branches',*sorted(d.branch.unique())]:
                    g = x if branch == 'All branches' else x[x.branch==branch]
                    orders = tickets if branch == 'All branches' else tickets[tickets.branch==branch]
                    s = g.assign(list_revenue=g.quantity*g.price,cost_value=g.quantity*g.cost,
                        discounted_units=g.quantity*g.discount.gt(0)).groupby(['product','category']).agg(
                        units=('quantity','sum'), revenue=('revenue','sum'), gross_profit=('gross_profit','sum'),
                        list_revenue=('list_revenue','sum'), cost_value=('cost_value','sum'),
                        discounted_units=('discounted_units','sum'), product_orders=('transaction','nunique')).reset_index()
                    for metric in ['units','revenue','gross_profit']:
                        s[metric+'_per_day'] = s[metric]/width
                    s['weighted_list_price'] = s.list_revenue/s.units
                    s['realized_price_per_unit'] = s.revenue/s.units
                    s['recorded_cost_per_unit'] = s.cost_value/s.units
                    s['gross_profit_per_unit'] = s.gross_profit/s.units
                    s['discounted_unit_share'] = s.discounted_units/s.units
                    s['effective_discount_rate'] = 1-s.revenue/s.list_revenue
                    s['unit_share'] = s.units/s.units.sum()
                    s['branch'] = branch
                    s['listed_price_values_in_history'] = (s['product'].map(variation.loc[branch])
                        if branch != 'All branches' else np.nan)
                    for key,value in meta.items():s[key]=value
                    items.append(s)
                    revenue, gp = float(g.revenue.sum()), float(g.gross_profit.sum())
                    branches.append(dict(**meta,branch=branch,orders=len(orders),orders_per_day=len(orders)/width,
                        revenue=revenue,gross_profit=gp,gross_profit_per_day=gp/width,
                        gross_profit_per_order=gp/len(orders) if len(orders) else np.nan,
                        gross_margin=gp/revenue if revenue else np.nan))
    summary = pd.concat(items,ignore_index=True)
    keys = ['event','cutoff','days_each_side','branch','product','category']
    before = summary[summary.period=='Before'].set_index(keys)
    after = summary[summary.period=='After'].set_index(keys)
    change = before.add_suffix('_before').join(after.add_suffix('_after'),how='outer')
    for metric in ['units_per_day','gross_profit_per_day','gross_profit_per_unit','realized_price_per_unit']:
        change[metric+'_change_pct'] = 100*(change[metric+'_after']/change[metric+'_before'].replace(0,np.nan)-1)
    change['discounted_unit_share_change_pp'] = 100*(change.discounted_unit_share_after-change.discounted_unit_share_before)
    change['unit_share_change_pp'] = 100*(change.unit_share_after-change.unit_share_before)
    change['small_base_either_period'] = change.units_before.fillna(0).lt(20)|change.units_after.fillna(0).lt(20)
    change['gross_profit_neutral_volume_change_pct'] = 100*(
        change.gross_profit_per_unit_before/change.gross_profit_per_unit_after.where(change.gross_profit_per_unit_after>0)-1)
    # An accounting threshold: it is not an estimate of demand response to a price change.
    change['volume_loss_tolerable_at_full_list_price_pct'] = 100*(1-
        change.gross_profit_per_unit_after/
        (change.weighted_list_price_after-change.recorded_cost_per_unit_after).where(
            change.weighted_list_price_after>change.recorded_cost_per_unit_after))
    return summary, change.reset_index(), pd.DataFrame(branches), pd.DataFrame(exposure)


def branch_phase_economics(phases):
    x=phases.copy()
    x['gross_margin']=x.gross_profit/x.revenue
    x['gross_profit_per_day']=x.gross_profit/x.days
    return x[['branch','phase','days','orders_per_day','revenue','gross_profit',
              'gross_profit_per_day','gross_profit_per_order','gross_margin']]


def pattern_cards():
    """Three evidence-led arguments; all causal and value claims remain qualified."""
    return pd.DataFrame([
        {'pattern':'1. Item-level discount exposure and contribution',
         'question':'Does additional item volume come with weaker realized prices or contribution?',
         'evidence':'Harbour Iced Latte and Frozen Yoghurt Cup before/after March 2; full item/event tables',
         'decision':'Audit and test product-specific promotion depth; track gross profit, not units alone',
         'alternative_explanations':'Earlier growth, calendar composition, selection into discounts, product availability',
         'value_measure':'Conditional volume-loss and gross-profit-neutral volume thresholds',
         'validation':'Randomize promotion eligibility/depth in contemporaneous branch/daypart blocks'},
        {'pattern':'2. Branch profit conversion remains unequal',
         'question':'Does higher traffic translate into comparable profit at each branch?',
         'evidence':'Branch margins and profit/order by calendar phase; same-product branch prices and costs',
         'decision':'Use branch-specific contribution floors and audit Garden cost definitions before standardizing offers',
         'alternative_explanations':'Supplier, recipe, allocation, quality, or recording differences; baseline structural gap',
         'value_measure':'Conditional Garden cost-gap closure scenarios, holding volume/price unchanged',
         'validation':'Audit high-impact item costs and pilot achievable changes before claiming savings'},
        {'pattern':'3. Product mix and absolute demand require different actions',
         'question':'Which item/category demand changes persist and retain attractive unit contribution?',
         'evidence':'Harbour Quinoa Bowl, meals category sensitivity, and bakery absolute volume versus share',
         'decision':'Test small product-specific preparation changes; use food suggestions as an optional demand test',
         'alternative_explanations':'Small bases, availability, calendar mix, broad growth, substitution, and waste',
         'value_measure':'Additional-item contribution after assumed operating, spoilage, and setup costs',
         'validation':'Chronological preparation comparison and a small randomized suggestion pilot with waste logs'},
    ])


def value_scenarios(d,cost):
    post=d[d.date.between(CHANGE_DATE,CHANGE_DATE+pd.Timedelta(days=27))]
    rows=[]
    # Hypothetical partial closure of the recorded same-product cost gap.
    garden=post[post.branch=='Garden'].merge(
        cost[cost.branch=='Garden'][['product','reference_cost']],on='product',validate='many_to_one')
    gap=float(((garden.cost-garden.reference_cost)*garden.quantity).sum())
    for fraction in [.10,.25,.50]:
        rows.append(dict(pattern=2,scenario=f'Close {fraction:.0%} of recorded Garden cost gap',
            baseline_window='March 2–29',conditional_contribution_usd=gap*fraction,
            assumptions='Same product quantities, prices, discounts; Harbour cost comparable and partial gap closure attainable; before implementation costs'))
    q=post[(post.branch=='Harbour')&(post['product']=='Quinoa Bowl')]
    price=float((q.price*q.quantity).sum()/q.quantity.sum())
    unit_cost=float((q.cost*q.quantity).sum()/q.quantity.sum())
    for extra,waste in [(10,3),(20,5),(30,8)]:
        value=extra*(price-unit_cost-.25)-waste*unit_cost-20
        rows.append(dict(pattern=3,scenario=f'{extra} genuinely additional Quinoa Bowls, {waste} extra wasted units',
            baseline_window='Illustrative pilot, not a measured time horizon',conditional_contribution_usd=value,
            assumptions='Full recorded list price; $0.25 extra operating cost/addition; $20 setup; no displaced purchases; waste at recorded unit cost'))
    return pd.DataFrame(rows)


def make_figures(changes,phases,output):
    import matplotlib.pyplot as plt
    selected=changes[(changes.event=='March 2 / war context')&(changes.days_each_side==28)&
        (changes.branch=='Harbour')&changes['product'].isin(['Iced Latte','Frozen Yoghurt Cup','Quinoa Bowl'])].set_index('product')
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    labels=list(selected.index); pos=np.arange(len(labels))
    for ax,metric,title in zip(axes,['units','realized_price_per_unit','gross_profit_per_unit'],
                              ['Recorded units / 28 days','Realized revenue / unit (USD)','Recorded gross profit / unit (USD)']):
        ax.bar(pos-.18,selected[metric+'_before'],width=.36,color='#64748b',label='Before')
        ax.bar(pos+.18,selected[metric+'_after'],width=.36,color='#16877a',label='After')
        ax.set_xticks(pos,labels,rotation=18,ha='right');ax.set_title(title,fontsize=10)
    axes[0].legend(fontsize=8)
    fig.suptitle('Specific-item examples at Harbour: price, volume, and contribution\nFebruary 2–March 1 vs March 2–29; calendar-unadjusted, not price elasticity',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.87]);fig.savefig(output/'business_item_patterns.png',dpi=150);plt.close(fig)
    x=phases[(phases.branch!='All branches')&(phases.days>1)]
    fig,axes=plt.subplots(1,2,figsize=(13,5))
    for branch,g in x.groupby('branch',sort=False):
        axes[0].plot(range(len(g)),100*g.gross_margin,marker='o',label=branch)
        axes[1].plot(range(len(g)),g.gross_profit_per_order,marker='o',label=branch)
    for ax in axes:
        ax.set_xticks(range(5),['Before both','Both before\nMarch 2','Both after\nMarch 2','Lent only','After both'])
        ax.legend(fontsize=8)
    axes[0].set(title='Recorded margin by calendar phase',ylabel='Gross profit / revenue (%)')
    axes[1].set(title='Recorded contribution per order',ylabel='Gross profit / order (USD)')
    fig.suptitle('Branch profitability gaps persist across changing conditions\nPooled descriptive rates; a persistent baseline gap is not a newly caused disruption effect',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.88]);fig.savefig(output/'business_branch_patterns.png',dpi=150);plt.close(fig)


def run_business(d,b,calendar_results,diagnostics,output):
    output=Path(output)
    items,changes,branches,exposure=event_comparisons(d,b)
    phases=branch_phase_economics(calendar_results['phases'])
    cards=pattern_cards()
    scenarios=value_scenarios(d,diagnostics['cost'])
    for name,table in [('item_event_summary',items),('item_event_changes',changes),
        ('branch_event_comparison',branches),('event_window_calendar_exposure',exposure),
        ('branch_phase_economics',phases),('supporting_item_pattern_cards',cards),('supporting_item_value_scenarios',scenarios)]:
        table.to_csv(output/f'{name}.csv',index=False)
    make_figures(changes,phases,output/'figures')
    return {'items':items,'changes':changes,'branches':branches,'exposure':exposure,
            'phases':phases,'patterns':cards,'value_scenarios':scenarios}
