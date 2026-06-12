with source as (
    select * from {{ ref('raw_quotas') }}
)

select
    rep_id,
    fiscal_quarter,
    cast(quota_amount as double) as quota_amount
from source
