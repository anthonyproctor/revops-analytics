-- Clean and type the raw CRM opportunity export.
-- Casts text to proper types, normalizes booleans, derives sales-cycle days.
with source as (
    select * from {{ ref('raw_opportunities') }}
)

select
    opportunity_id,
    account_id,
    rep_id,
    lead_source,
    stage,
    cast(amount as double)                                   as amount,
    cast(created_date as date)                               as created_date,
    nullif(close_date, '')::date                             as close_date,
    fiscal_quarter,
    coalesce(lower(is_won) = 'true', false)                  as is_won,
    coalesce(lower(is_closed) = 'true', false)               as is_closed,
    case
        when nullif(close_date, '') is not null
        then date_diff('day', cast(created_date as date), cast(close_date as date))
    end                                                      as sales_cycle_days
from source
