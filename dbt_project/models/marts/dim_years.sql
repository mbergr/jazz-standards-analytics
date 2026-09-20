-- Dimension: time at year grain (the granularity Spotify release dates give us),
-- enriched with decade and a jazz-era label applied to the recording year.

with years as (
    select distinct release_year as year
    from {{ ref('int_recordings_deduped') }}
    where release_year is not null
)

select
    year            as year_key,
    year,
    (year / 10) * 10 as decade,
    case
        when year <= 1929               then 'Early Jazz'
        when year between 1930 and 1944 then 'Swing Era'
        when year between 1945 and 1959 then 'Bebop & Cool'
        when year between 1960 and 1969 then 'Hard Bop & Modal'
        when year between 1970 and 1989 then 'Fusion & Post-Bop'
        else 'Contemporary'
    end as jazz_era
from years
