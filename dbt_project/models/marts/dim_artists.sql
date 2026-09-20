-- Dimension: one row per artist with at least one resolved, deduplicated recording.

with recordings as (
    select * from {{ ref('int_recordings_deduped') }}
),

artists as (
    select
        artist_id,
        max(artist_name)            as artist_name,        -- names vary slightly; pick one
        count(distinct standard_id) as standards_recorded,
        count(*)                    as recordings_count
    from recordings
    group by artist_id
)

select
    {{ dbt_utils.generate_surrogate_key(['artist_id']) }} as artist_key,
    artist_id,
    artist_name,
    standards_recorded,
    recordings_count
from artists
