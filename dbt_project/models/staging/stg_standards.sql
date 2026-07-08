-- Staging: one clean row per jazz standard.
-- 1:1 with raw.standards — just trims, renames, and light typing. No business logic.

with source as (
    select * from {{ source('raw', 'standards') }}
),

cleaned as (
    select
        slug                         as standard_id,      -- natural key (URL slug)
        rank                         as popularity_rank,
        trim(title)                  as title,
        nullif(trim(composer), '')   as composer,
        nullif(trim(lyricist), '')   as lyricist,
        year                         as composed_year,
        original_source,
        detail_url,
        scraped_at
    from source
)

select * from cleaned
