-- Metric: how long each standard kept being (re)recorded — its longevity.
--   span_years   = latest - earliest recording year
--   eras_spanned = distinct jazz eras the recordings fall into
-- Caveat: based on Spotify release_year (release date, not recording date), so
-- reissues can stretch the span.

with fct as (
    select * from {{ ref('fct_recordings') }}
),

standards as (
    select * from {{ ref('dim_standards') }}
),

years as (
    select * from {{ ref('dim_years') }}
)

select
    s.standard_id,
    s.title,
    s.composer,
    s.composed_year,
    min(y.year)                as first_recording_year,
    max(y.year)                as latest_recording_year,
    max(y.year) - min(y.year)  as span_years,
    count(distinct y.jazz_era) as eras_spanned,
    count(*)                   as recording_count
from fct f
join standards s on f.standard_key = s.standard_key
join years y on f.year_key = y.year_key
group by 1, 2, 3, 4
order by span_years desc, recording_count desc
