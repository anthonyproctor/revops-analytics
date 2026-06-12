-- One enriched row per opportunity: the analysis-ready opportunity fact,
-- joined to account and rep attributes for slicing by segment, region, source.
with opps as (
    select * from {{ ref('stg_opportunities') }}
),
accounts as (
    select * from {{ ref('stg_accounts') }}
),
reps as (
    select * from {{ ref('stg_reps') }}
)

select
    o.opportunity_id,
    o.account_id,
    a.account_name,
    a.segment,
    a.industry,
    a.region                as account_region,
    o.rep_id,
    r.rep_name,
    o.lead_source,
    o.stage,
    o.amount,
    o.created_date,
    o.close_date,
    o.fiscal_quarter,
    o.is_won,
    o.is_closed,
    o.sales_cycle_days,
    case when o.is_won then o.amount else 0 end          as won_amount,
    case when o.is_closed and not o.is_won then o.amount else 0 end as lost_amount,
    case when not o.is_closed then o.amount else 0 end   as open_pipeline_amount
from opps o
left join accounts a on o.account_id = a.account_id
left join reps r on o.rep_id = r.rep_id
