-- Metric: how many (deduplicated) recordings each standard has in the dataset.
-- Caveat: capped by the ingestion limit (RECORDINGS_PER_STANDARD=10), so this is
-- "most recorded within what we fetched", not the true canon count.

with fct as (
    select * from {{ ref('fct_recordings') }}
),

standards as (
    select * from {{ ref('dim_standards') }}
)

select
    s.standard_id,
    s.title,
    s.composer,
    s.composed_year,
    s.popularity_rank,
    count(*)                     as recording_count,
    count(distinct f.artist_key) as distinct_artists
from fct f
join standards s on f.standard_key = s.standard_key
group by 1, 2, 3, 4, 5
order by recording_count desc, s.popularity_rank
