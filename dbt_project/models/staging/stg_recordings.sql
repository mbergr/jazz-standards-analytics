-- Staging: one clean row per candidate recording (standard × Spotify track).
-- Renames, trims, and normalizes the messy release_date into a usable release_year.

with source as (
    select * from {{ source('raw', 'recordings') }}
),

cleaned as (
    select
        standard_slug                                        as standard_id,   -- FK to stg_standards
        spotify_track_id                                     as track_id,
        trim(track_name)                                     as track_name,
        nullif(trim(artist_name), '')                        as artist_name,
        artist_id,
        nullif(trim(album_name), '')                         as album_name,
        album_release_date                                   as release_date_raw,
        -- release_date comes at mixed granularity ("1993" or "2011-09-20");
        -- the first four chars are always the year.
        try_cast(left(album_release_date, 4) as integer)     as release_year,
        duration_ms,
        round(duration_ms / 1000.0)                          as duration_seconds,
        ingested_at
    from source
)

select * from cleaned
