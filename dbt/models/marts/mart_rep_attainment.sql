-- Quota attainment per rep per fiscal quarter: the core RevOps performance mart.
-- Won ARR vs quota, attainment %, win rate, and average sales cycle.
with closed as (
    select
        rep_id,
        rep_name,
        fiscal_quarter,
        count(*)                                       as closed_opps,
        sum(case when is_won then 1 else 0 end)        as won_opps,
        sum(won_amount)                                as won_amount,
        avg(case when is_won then sales_cycle_days end) as avg_won_cycle_days
    from {{ ref('fct_opportunities') }}
    where is_closed
    group by 1, 2, 3
),
quotas as (
    select rep_id, fiscal_quarter, quota_amount
    from {{ ref('stg_quotas') }}
)

select
    c.rep_id,
    c.rep_name,
    c.fiscal_quarter,
    q.quota_amount,
    c.won_amount,
    c.closed_opps,
    c.won_opps,
    round(c.won_opps * 1.0 / nullif(c.closed_opps, 0), 3)        as win_rate,
    round(c.won_amount / nullif(q.quota_amount, 0), 3)           as quota_attainment,
    round(c.avg_won_cycle_days, 1)                              as avg_won_cycle_days,
    case when c.won_amount >= q.quota_amount then true else false end as hit_quota
from closed c
-- inner join: quota attainment is only defined for rep-quarters that carry a quota
inner join quotas q
    on c.rep_id = q.rep_id and c.fiscal_quarter = q.fiscal_quarter
