"""Customer-level discovery with explicit coverage, fixed cohorts, and follow-up."""
from pathlib import Path

import numpy as np
import pandas as pd

from .business import EVENTS
from .calendar import CHANGE_DATE


def customer_orders(d, b):
    x=b.copy()
    consistency=d.groupby('transaction').customer.nunique(dropna=False)
    if consistency.gt(1).any():
        raise ValueError('Conflicting Customer IDs within an order.')
    x['customer']=d.groupby('transaction').customer.first().reindex(x.index)
    x['units']=d.groupby('transaction').quantity.sum().reindex(x.index)
    return x


def period_metrics(x):
    known=x.dropna(subset=['customer'])
    visits=known.groupby('customer').date.nunique()
    n=known.customer.nunique()
    return dict(total_orders=len(x),identified_orders=len(known),
        id_coverage=len(known)/len(x) if len(x) else np.nan,
        active_identified_customers=n,orders_per_active_customer=len(known)/n if n else np.nan,
        distinct_customer_days=int(visits.sum()),days_per_active_customer=visits.mean(),
        repeat_day_customer_share=float(visits.ge(2).mean()),
        identified_gross_profit=float(known.gross_profit.sum()),
        identified_gross_profit_per_order=float(known.gross_profit.mean()))


def breadth_frequency(before,after):
    """Exact symmetric decomposition of identified-order change, not causal impact."""
    a,b=period_metrics(before),period_metrics(after)
    n0,n1=a['active_identified_customers'],b['active_identified_customers']
    f0,f1=a['orders_per_active_customer'],b['orders_per_active_customer']
    breadth=(n1-n0)*(f0+f1)/2
    frequency=(f1-f0)*(n0+n1)/2
    change=b['identified_orders']-a['identified_orders']
    return dict(identified_order_change=change,breadth_component_orders=breadth,
        frequency_component_orders=frequency,
        breadth_share_of_change=breadth/change if change else np.nan,
        frequency_share_of_change=frequency/change if change else np.nan)


def window_analysis(orders,widths=(14,28)):
    summaries,decompositions,flows=[],[],[]
    for event,cutoff in EVENTS:
        for width in widths:
            start,end=cutoff-pd.Timedelta(days=width),cutoff+pd.Timedelta(days=width-1)
            if start<orders.date.min() or end>orders.date.max():
                continue
            pre=orders[orders.date.between(start,cutoff-pd.Timedelta(days=1))]
            post=orders[orders.date.between(cutoff,end)]
            for branch in ['All branches',*sorted(orders.branch.unique())]:
                a=pre if branch=='All branches' else pre[pre.branch==branch]
                b=post if branch=='All branches' else post[post.branch==branch]
                meta=dict(event=event,cutoff=cutoff,days_each_side=width,branch=branch)
                for period,x in [('Before',a),('After',b)]:
                    summaries.append(dict(**meta,period=period,**period_metrics(x)))
                decompositions.append(dict(**meta,**breadth_frequency(a,b)))
                ak=a.dropna(subset=['customer']);bk=b.dropna(subset=['customer'])
                left,right=set(ak.customer),set(bk.customer)
                prior=set(orders.loc[(orders.date<start)&orders.customer.notna(),'customer'])
                segments=[('Observed in both windows',left&right),
                          ('Observed only in before window',left-right),
                          ('Observed only in after window',right-left)]
                for segment,ids in segments:
                    flows.append(dict(**meta,segment=segment,customers=len(ids),
                        before_orders=int(ak.customer.isin(ids).sum()),after_orders=int(bk.customer.isin(ids).sum()),
                        before_gross_profit=float(ak.loc[ak.customer.isin(ids),'gross_profit'].sum()),
                        after_gross_profit=float(bk.loc[bk.customer.isin(ids),'gross_profit'].sum()),
                        after_only_seen_earlier=int(len(ids&prior)) if segment=='Observed only in after window' else np.nan))
    return pd.DataFrame(summaries),pd.DataFrame(decompositions),pd.DataFrame(flows)


def fixed_cohorts(orders,widths=(14,28),thresholds=(1,2,3)):
    """Membership fixed in an independent earlier window; include zero-visit members."""
    known=orders.dropna(subset=['customer'])
    records=[]
    for event,cutoff in EVENTS:
        for width in widths:
            train_start,train_end=cutoff-pd.Timedelta(days=2*width),cutoff-pd.Timedelta(days=width+1)
            if train_start<orders.date.min() or cutoff+pd.Timedelta(days=width-1)>orders.date.max():
                continue
            train=known[known.date.between(train_start,train_end)]
            counts=train.groupby('customer').date.nunique()
            for threshold in thresholds:
                ids=counts[counts>=threshold].index
                if not len(ids):
                    continue
                for period,start,end in [('Before',cutoff-pd.Timedelta(days=width),cutoff-pd.Timedelta(days=1)),
                                         ('After',cutoff,cutoff+pd.Timedelta(days=width-1))]:
                    x=known[known.date.between(start,end)&known.customer.isin(ids)]
                    records.append(dict(event=event,cutoff=cutoff,days_each_side=width,
                        calibration_start=train_start,calibration_end=train_end,
                        minimum_calibration_visit_days=threshold,period=period,cohort_customers=len(ids),
                        active_cohort_customers=x.customer.nunique(),orders=len(x),
                        distinct_customer_days=int(x.groupby('customer').date.nunique().sum()),
                        orders_per_cohort_member=len(x)/len(ids),
                        gross_profit=float(x.gross_profit.sum()),
                        gross_profit_per_cohort_member=float(x.gross_profit.sum()/len(ids))))
    return pd.DataFrame(records)


def branch_continuity(orders,widths=(14,28)):
    known=orders.dropna(subset=['customer'])
    rows=[]
    for event,cutoff in EVENTS:
        for width in widths:
            if cutoff-pd.Timedelta(days=width)<orders.date.min() or cutoff+pd.Timedelta(days=width-1)>orders.date.max():
                continue
            pre=known[known.date.between(cutoff-pd.Timedelta(days=width),cutoff-pd.Timedelta(days=1))]
            post=known[known.date.between(cutoff,cutoff+pd.Timedelta(days=width-1))]
            for branch,g in pre.groupby('branch'):
                ids=set(g.customer)
                any_return=set(post.customer)&ids
                same=set(post.loc[post.branch==branch,'customer'])&ids
                other_only=any_return-same
                absent=ids-any_return
                apparent_absent=ids-same
                rows.append(dict(event=event,cutoff=cutoff,days_each_side=width,branch=branch,
                    before_customers=len(ids),observed_same_branch_after=len(same),
                    observed_other_branches_only_after=len(other_only),not_observed_chain_after=len(absent),
                    apparent_branch_absent=len(apparent_absent),
                    share_of_apparent_branch_absence_seen_elsewhere=len(other_only)/len(apparent_absent) if apparent_absent else np.nan,
                    elsewhere_only_recorded_gross_profit=float(post.loc[post.customer.isin(other_only),'gross_profit'].sum())))
    return pd.DataFrame(rows)


def follow_up(orders,cutoffs=None,baseline_days=28,horizons=(28,56)):
    known=orders.dropna(subset=['customer'])
    if cutoffs is None:
        cutoffs=pd.date_range(orders.date.min()+pd.Timedelta(days=baseline_days),
            orders.date.max()-pd.Timedelta(days=max(horizons)-1),freq='7D')
        cutoffs=cutoffs.union(pd.DatetimeIndex([date for _,date in EVENTS])).sort_values()
    rows=[]
    for cutoff in cutoffs:
        if cutoff-pd.Timedelta(days=baseline_days)<orders.date.min():
            continue
        before=known[known.date.between(cutoff-pd.Timedelta(days=baseline_days),cutoff-pd.Timedelta(days=1))]
        ids=set(before.customer)
        if not ids:
            continue
        first=set(known.loc[known.date.between(cutoff,cutoff+pd.Timedelta(days=horizons[0]-1)),'customer'])
        initially_absent=ids-first
        for horizon in horizons:
            end=cutoff+pd.Timedelta(days=horizon-1)
            if end>orders.date.max():
                continue  # Never score incomplete follow-up as nonreturn.
            after=known[known.date.between(cutoff,end)]
            seen=set(after.customer)
            rows.append(dict(cutoff=cutoff,baseline_days=baseline_days,followup_days=horizon,
                followup_end=end,baseline_customers=len(ids),observed_return_customers=len(ids&seen),
                observed_return_rate=len(ids&seen)/len(ids),not_observed_customers=len(ids-seen),
                initially_absent_customers=len(initially_absent),
                initially_absent_seen_by_horizon=len(initially_absent&seen),
                later_return_share_of_initial_absence=len(initially_absent&seen)/len(initially_absent) if initially_absent else np.nan))
    return pd.DataFrame(rows)


def cards():
    return pd.DataFrame([
        dict(pattern='1. Growth comes mainly from observed audience breadth',
             evidence='Distinct identified customers, exact breadth/frequency decomposition, independent earlier customer cohorts',
             decision='Separate observed audience breadth, reactivation, and repeat frequency; do not label after-only IDs as new acquisition',
             competing_explanations='Incomplete customer capture, customer mix, calendar overlap, normal growth; observed first appearance is not acquisition',
             validation='Freeze customer cohorts before comparison, include zero visits, and randomize a chosen continuity/onboarding service'),
        dict(pattern='2. Branch absence can be continued business elsewhere in the chain',
             evidence='Same customer IDs linked across all three branches with disjoint branch-continuity categories',
             decision='Use chain-wide customer recognition and check cross-branch activity before loss-recovery targeting',
             competing_explanations='Routine multi-branch use, incomplete capture, or temporary route changes; relocation and war causation are unobserved',
             validation='Compare with other cutoffs and test chain-wide continuity/routing against current branch-only processes'),
        dict(pattern='3. A short absence is not permanent customer loss',
             evidence='Same baseline cohort followed for complete 28- and 56-day horizons; alternative-cutoff checks',
             decision='Use a staged inactivity policy and compare 28-day versus longer-horizon service/recovery timing',
             competing_explanations='Normal infrequent visits, missing IDs, observation horizon, calendar and promotion exposure; late return is not proven organic',
             validation='Use complete fixed follow-up and randomized intervention timing before adopting any inactivity threshold'),
    ])


def value_scenarios(orders,continuity):
    cutoff=CHANGE_DATE
    known=orders.dropna(subset=['customer'])
    pre=known[known.date.between(cutoff-pd.Timedelta(days=28),cutoff-pd.Timedelta(days=1))]
    post=known[known.date.between(cutoff,cutoff+pd.Timedelta(days=27))]
    gp_per_order=float(post.gross_profit.mean())
    ids=set(pre.customer)
    rows=[]
    for incremental_return in [.01,.02,.05]:
        added=len(ids)*incremental_return
        rows.append(dict(pattern=1,scenario=f'{incremental_return:.0%} of baseline identified customers make one genuinely additional order',
            conditional_contribution_usd=added*gp_per_order,
            assumptions='Observed mean identified-order gross profit; no substitution; before intervention, labor, and other incremental costs; return uplift unmeasured'))
    case=continuity[(continuity.cutoff==cutoff)&(continuity.days_each_side==28)&(continuity.branch=='Uptown')].iloc[0]
    for cost in [.25,.50,1.]:
        rows.append(dict(pattern=2,scenario=f'Avoid one assumed ${cost:.2f} branch-loss contact for each Uptown customer already observed elsewhere',
            conditional_contribution_usd=case.observed_other_branches_only_after*cost,
            assumptions='Hypothetical avoidable per-contact cost; current recovery policy/cost unknown; no actual messaging or savings measured; branch cohorts must not be summed'))
    return pd.DataFrame(rows)


def figures(summary,decomposition,cohorts,continuity,followup,output):
    import matplotlib.pyplot as plt
    x=summary[(summary.event=='March 2 / war context')&(summary.days_each_side==28)&(summary.branch=='All branches')].set_index('period').loc[['Before','After']]
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,metric,title in zip(axes,['active_identified_customers','orders_per_active_customer','id_coverage'],
            ['Active identified customers','Orders / active identified customer','Customer-ID coverage (%)']):
        ax.bar(['Before','After'],x[metric]*(100 if metric=='id_coverage' else 1),color=['#64748b','#16877a'])
        ax.set_title(title,fontsize=10)
        for i,v in enumerate(x[metric]):ax.text(i,v*(100 if metric=='id_coverage' else 1),f'{v*100:.1f}%' if metric=='id_coverage' else f'{v:,.2f}',ha='center',va='bottom',fontsize=9)
        ax.margins(y=.2)
    fig.suptitle('Customer growth: breadth, frequency, and capture are different measures\nEqual 28-day March 2 windows; identified customers only',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.86]);fig.savefig(output/'customer_growth_sources.png',dpi=150);plt.close(fig)
    c=continuity[(continuity.cutoff==CHANGE_DATE)&(continuity.days_each_side==28)].set_index('branch')
    fig,ax=plt.subplots(figsize=(9,5));bottom=np.zeros(len(c))
    for metric,label,color in [('observed_same_branch_after','Seen at same branch','#16877a'),
            ('observed_other_branches_only_after','Seen only at other branches','#d08a36'),
            ('not_observed_chain_after','Not observed anywhere in 28 days','#94a3b8')]:
        ax.bar(c.index,c[metric],bottom=bottom,label=label,color=color)
        for i,v in enumerate(c[metric]):ax.text(i,bottom[i]+v/2,str(v),ha='center',va='center',fontsize=9)
        bottom+=c[metric].to_numpy()
    ax.set(ylabel='Identified customers active at branch before March 2',title='Branch absence is not the same as chain-wide absence')
    ax.legend(fontsize=8);fig.text(.5,.01,'Customers can belong to multiple baseline branch cohorts. Do not sum branch counts as unique people.',ha='center',fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(output/'customer_branch_continuity.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    f=followup[followup.cutoff==CHANGE_DATE].sort_values('followup_days')
    axes[0].bar(f.followup_days.astype(str),100*f.observed_return_rate,color='#16877a')
    axes[0].set(xlabel='Complete follow-up (days)',ylabel='Baseline customers observed again (%)',title='Same cohort, longer observation horizon',ylim=(0,100))
    for _,r in f.iterrows():axes[0].text(str(r.followup_days),100*r.observed_return_rate,f'{r.observed_return_rate:.1%}',ha='center',va='bottom')
    for horizon,g in followup.groupby('followup_days'):
        axes[1].plot(g.cutoff,100*g.observed_return_rate,label=f'{horizon} days')
    axes[1].axvline(CHANGE_DATE,color='#c25a28',ls='--')
    axes[1].set(title='Return rates at other cutoffs',ylabel='Observed return (%)');axes[1].legend();axes[1].tick_params(axis='x',rotation=25)
    fig.suptitle('Observed nonreturn depends on follow-up; a missing ID can hide a real visit',fontsize=11)
    fig.tight_layout(rect=[0,0,1,.91]);fig.savefig(output/'customer_followup.png',dpi=150);plt.close(fig)


def run_customers(d,b,output):
    output=Path(output)
    orders=customer_orders(d,b)
    summary,decomposition,flows=window_analysis(orders)
    cohorts=fixed_cohorts(orders)
    continuity=branch_continuity(orders)
    returns=follow_up(orders)
    scenarios=value_scenarios(orders,continuity)
    patterns=cards()
    for name,table in [('customer_window_summary',summary),('customer_growth_decomposition',decomposition),
        ('customer_window_flows',flows),('customer_fixed_cohorts',cohorts),
        ('customer_branch_continuity',continuity),('customer_followup',returns),
        ('business_pattern_cards',patterns),('business_value_scenarios',scenarios)]:
        table.to_csv(output/f'{name}.csv',index=False)
    figures(summary,decomposition,cohorts,continuity,returns,output/'figures')
    return {'summary':summary,'decomposition':decomposition,'flows':flows,'cohorts':cohorts,
            'continuity':continuity,'followup':returns,'patterns':patterns,'value_scenarios':scenarios}
