"""DuckDB connection helper and raw-schema bootstrap.

The `raw` schema lands source data as-is (no cleaning) so the pipeline can always
be rebuilt from the crude layer without re-hitting the network. All cleaning and
typing happens later, in the dbt staging layer.
"""
import duckdb

from . import config

DDL = [
    f"CREATE SCHEMA IF NOT EXISTS {config.RAW_SCHEMA};",
    f"""
    CREATE TABLE IF NOT EXISTS {config.RAW_SCHEMA}.standards (
        rank             INTEGER,
        title            VARCHAR,
        slug             VARCHAR,
        composer         VARCHAR,
        lyricist         VARCHAR,
        year             INTEGER,
        original_source  VARCHAR,
        detail_url       VARCHAR,
        scraped_at       TIMESTAMP
    );
    """,
    f"""
    CREATE TABLE IF NOT EXISTS {config.RAW_SCHEMA}.recordings (
        standard_slug       VARCHAR,
        spotify_track_id    VARCHAR,
        track_name          VARCHAR,
        artist_name         VARCHAR,
        artist_id           VARCHAR,
        album_name          VARCHAR,
        album_release_date  VARCHAR,
        duration_ms         INTEGER,
        ingested_at         TIMESTAMP
    );
    """,
]


def connect():
    """Open (and create if needed) the DuckDB database file."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(config.DB_PATH))


def bootstrap(con):
    """Create the raw schema and tables if they don't exist yet."""
    for stmt in DDL:
        con.execute(stmt)
