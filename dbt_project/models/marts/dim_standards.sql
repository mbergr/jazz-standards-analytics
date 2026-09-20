-- Dimension: one row per jazz standard.

with standards as (
    select * from {{ ref('stg_standards') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['standard_id']) }} as standard_key,
    standard_id,
    title,
    composer,
    lyricist,
    composed_year,
    (composed_year / 10) * 10 as composed_decade,
    popularity_rank
from standards
