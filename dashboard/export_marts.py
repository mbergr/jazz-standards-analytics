"""Export the dbt marts / metrics to small CSVs the Streamlit dashboard reads.

The DuckDB file is gitignored, so Streamlit Community Cloud (which clones the repo)
can't see it. These CSVs are the dashboard's committed, portable data source.
Re-run after `dbt build` to refresh:

    python dashboard/export_marts.py
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jazz.duckdb"
OUT_DIR = Path(__file__).resolve().parent / "data"

QUERIES = {
    "most_recorded": """
        select title, composer, composed_year, popularity_rank,
               recording_count, distinct_artists
        from main.rpt_most_recorded_standards
    """,
    "longevity": """
        select title, composer, composed_year, first_recording_year,
               latest_recording_year, span_years, eras_spanned, recording_count
        from main.rpt_standard_longevity
    """,
    "composer_footprint": """
        select composer, standards_in_canon, total_recordings,
               earliest_composition, latest_composition
        from main.rpt_composer_footprint
    """,
    "artists": """
        select artist_name, standards_recorded, recordings_count
        from main.dim_artists
        order by standards_recorded desc, recordings_count desc
    """,
    "era_distribution": """
        select y.jazz_era, min(y.year) as era_start, count(*) as recordings
        from main.fct_recordings f
        join main.dim_years y on f.year_key = y.year_key
        group by y.jazz_era
        order by era_start
    """,
    "kpis": """
        select
            (select count(*) from main.dim_standards)                               as standards_total,
            (select count(*) from main.rpt_most_recorded_standards)                 as standards_with_recordings,
            (select count(*) from main.fct_recordings)                              as recordings,
            (select count(*) from main.dim_artists)                                 as artists,
            (select count(distinct composer) from main.dim_standards
             where composer is not null)                                           as composers,
            (select min(composed_year) from main.dim_standards)                    as earliest_composed,
            (select max(composed_year) from main.dim_standards)                    as latest_composed
    """,
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    for name, sql in QUERIES.items():
        df = con.execute(sql).df()
        out = OUT_DIR / f"{name}.csv"
        df.to_csv(out, index=False)
        print(f"  wrote {out.relative_to(ROOT)}  ({len(df)} rows)")
    con.close()
    print("Done.")


if __name__ == "__main__":
    main()
