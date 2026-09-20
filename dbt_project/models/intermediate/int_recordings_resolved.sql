-- Intermediate: entity resolution.
-- Spotify search returns candidates, some of which merely share a title with the
-- standard ("Summertime Sadness" for "Summertime", "Easy Livin'" for "Easy Living").
-- Keep only candidates whose normalized track title equals the standard's.

with recordings as (
    select * from {{ ref('stg_recordings') }}
),

standards as (
    select standard_id, title from {{ ref('stg_standards') }}
),

matched as (
    select
        r.standard_id,
        r.track_id,
        r.track_name,
        r.artist_name,
        r.artist_id,
        r.album_name,
        r.release_year,
        r.duration_ms,
        r.duration_seconds,
        {{ normalize_title('r.track_name') }} as track_title_norm,
        {{ normalize_title('s.title') }}      as standard_title_norm
    from recordings r
    inner join standards s on r.standard_id = s.standard_id
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
from matched
where track_title_norm = standard_title_norm
