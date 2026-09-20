-- Intermediate: deduplication to the fact grain.
-- Collapse near-identical releases (remasters, compilations, re-issues) of the same
-- standard by the same artist into a single row — the earliest known release.
-- Result grain: one recording of a standard by an artist.

with resolved as (
    select * from {{ ref('int_recordings_resolved') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by standard_id, coalesce(artist_id, lower(artist_name))
            order by release_year asc nulls last, track_id
        ) as rn
    from resolved
)

select
    standard_id,
    track_id,
    track_name,
    artist_name,
    artist_id,
    album_name,
    release_year,
    duration_ms,
    duration_seconds
from ranked
where rn = 1
