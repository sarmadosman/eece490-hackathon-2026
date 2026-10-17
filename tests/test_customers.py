import numpy as np
import pandas as pd
import pytest

from stories.customers import breadth_frequency,period_metrics,fixed_cohorts,branch_continuity,follow_up


def frame(rows):
    x=pd.DataFrame(rows,columns=['date','customer','branch','gross_profit'])
    x['date']=pd.to_datetime(x.date)
    return x


def test_breadth_frequency_identity_and_missing_ids():
    pre=frame([('2026-02-02','A','X',3),('2026-02-02','A','X',3),
               ('2026-02-03','B','X',4),('2026-02-04',None,'X',5)])
    post=frame([('2026-03-02','A','X',3),('2026-03-03','A','X',3),
                ('2026-03-04','B','X',4),('2026-03-04','C','X',5)])
    m=period_metrics(pre)
    assert m['active_identified_customers']==2
    assert m['id_coverage']==.75
    assert m['distinct_customer_days']==2  # Two same-day A orders are one visit-day.
    d=breadth_frequency(pre,post)
    assert d['breadth_component_orders']+d['frequency_component_orders']==pytest.approx(1)
    assert d['breadth_share_of_change']+d['frequency_share_of_change']==pytest.approx(1)


def test_fixed_cohort_keeps_zero_visits_and_excludes_post_selected_members():
    x=frame([('2026-02-01',None,'X',0),('2026-02-05','A','X',2),('2026-02-06','B','X',2),
             ('2026-02-21','A','X',4),('2026-02-22','C','X',4),
             ('2026-03-03','A','X',6),('2026-03-04','D','X',6),('2026-03-30',None,'X',0)])
    c=fixed_cohorts(x,widths=(14,),thresholds=(1,))
    c=c[c.event=='March 2 / war context']
    assert c.cohort_customers.tolist()==[2,2]
    assert c.orders.tolist()==[1,1]
    assert c.orders_per_cohort_member.tolist()==[.5,.5]
    assert (c.calibration_end<pd.Timestamp('2026-02-16')).all()


def test_branch_absence_is_partitioned_into_elsewhere_and_no_chain_observation():
    x=frame([('2026-02-16',None,'Uptown',0),('2026-02-20','A','Uptown',4),
             ('2026-02-21','B','Uptown',4),('2026-02-22','C','Uptown',4),
             ('2026-03-03','A','Harbour',7),('2026-03-04','B','Uptown',5),('2026-03-15',None,'Uptown',0)])
    c=branch_continuity(x,widths=(14,))
    r=c[(c.event=='March 2 / war context')&(c.branch=='Uptown')].iloc[0]
    assert r.before_customers==3
    assert r.observed_same_branch_after==r.observed_other_branches_only_after==r.not_observed_chain_after==1
    assert r.apparent_branch_absent==2
    assert r.share_of_apparent_branch_absence_seen_elsewhere==.5


def test_incomplete_followup_is_not_scored_as_nonreturn():
    x=frame([('2026-02-02',None,'X',0),('2026-02-20','A','X',3),('2026-02-21','B','X',3),
             ('2026-03-10','A','X',3),('2026-03-29',None,'X',0)])
    cutoff=pd.Timestamp('2026-03-02')
    f=follow_up(x,cutoffs=[cutoff])
    assert f.followup_days.tolist()==[28]
    assert f.observed_return_rate.iloc[0]==.5
    x=pd.concat([x,frame([('2026-04-10','B','X',3),('2026-04-26',None,'X',0)])])
    f=follow_up(x,cutoffs=[cutoff]).set_index('followup_days')
    assert f.loc[56,'observed_return_rate']==1
    assert f.loc[56,'initially_absent_seen_by_horizon']==1
