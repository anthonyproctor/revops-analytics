with source as (
    select * from {{ ref('raw_reps') }}
)

select
    rep_id,
    rep_name,
    region,
    primary_segment,
    cast(hire_date as date) as hire_date
from source
