-- Metric: each composer's footprint across the canon.
-- Note: composer is the raw credit string; multi-writer credits are not split
-- (a known raw-layer limitation), so co-written tunes form their own group.

with fct as (
    select * from {{ ref('fct_recordings') }}
),

standards as (
    select * from {{ ref('dim_standards') }}
)

select
    s.composer,
    count(distinct s.standard_id) as standards_in_canon,
    count(*)                      as total_recordings,
    min(s.composed_year)          as earliest_composition,
    max(s.composed_year)          as latest_composition
from fct f
join standards s on f.standard_key = s.standard_key
where s.composer is not null
group by 1
order by total_recordings desc
