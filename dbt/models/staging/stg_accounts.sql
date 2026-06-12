with source as (
    select * from {{ ref('raw_accounts') }}
)

select
    account_id,
    account_name,
    segment,
    industry,
    region,
    cast(employee_count as integer) as employee_count
from source
