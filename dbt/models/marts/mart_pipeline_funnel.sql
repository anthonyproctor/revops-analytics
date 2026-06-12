-- Conversion funnel and pipeline health by segment and lead source.
-- Win rate, average deal size, and open pipeline for RevOps reporting.
with f as (
    select * from {{ ref('fct_opportunities') }}
)

select
    segment,
    lead_source,
    count(*)                                          as total_opps,
    sum(case when is_closed then 1 else 0 end)        as closed_opps,
    sum(case when is_won then 1 else 0 end)           as won_opps,
    round(sum(case when is_won then 1 else 0 end) * 1.0
          / nullif(sum(case when is_closed then 1 else 0 end), 0), 3) as win_rate,
    sum(won_amount)                                   as won_amount,
    sum(open_pipeline_amount)                         as open_pipeline_amount,
    round(avg(case when is_won then amount end), 0)   as avg_won_deal_size,
    round(avg(case when is_won then sales_cycle_days end), 1) as avg_won_cycle_days
from f
group by 1, 2
order by 1, won_amount desc
