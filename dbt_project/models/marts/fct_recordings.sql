-- Fact: one recording of a standard by an artist (resolved + deduplicated).
-- Grain: one row per (standard, artist). Joins to the three dimensions by key.

with recordings as (
    select * from {{ ref('int_recordings_deduped') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['standard_id', 'artist_id', 'track_id']) }} as recording_key,
    -- foreign keys
    {{ dbt_utils.generate_surrogate_key(['standard_id']) }} as standard_key,
    {{ dbt_utils.generate_surrogate_key(['artist_id']) }}   as artist_key,
    release_year                                            as year_key,
    -- degenerate dimensions
    track_id,
    track_name,
    album_name,
    -- measures
    duration_ms,
    duration_seconds
from recordings
