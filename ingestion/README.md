# Ingestion

Python scripts that land raw source data into DuckDB. Two sources feed the `raw` schema:

1. **JazzStandards.com** — scrapes the ranked canon into `raw.standards`.
2. **Spotify Web API** — searches recordings per standard into `raw.recordings`.

Everything is written to `data/jazz.duckdb` (gitignored). The `raw` schema lands data
as-is; cleaning and typing happen later in the dbt staging layer.

## Setup

```bash
pip install -r requirements.txt          # from the repo root
cp .env.example .env                      # then fill in your Spotify credentials
```

Spotify credentials come from a free app at <https://developer.spotify.com/dashboard>.
The scraper needs no credentials — only the recordings step does.

## Run

From the repo root:

```bash
# Full pipeline (scrape, then Spotify)
python -m ingestion.run_ingestion

# Or each step on its own
python -m ingestion.scrape_standards
python -m ingestion.spotify_recordings
```

## Configuration

All knobs are environment variables (read from `.env`), with defaults in `config.py`:

| Variable | Default | Meaning |
|---|---|---|
| `TOP_N` | `100` | How many top-ranked standards to ingest |
| `RECORDINGS_PER_STANDARD` | `10` | Spotify results to keep per standard |
| `REQUEST_DELAY_SECONDS` | `1.0` | Polite pause between HTTP requests |
| `DB_PATH` | `data/jazz.duckdb` | DuckDB database file location |

Tip: run a quick smoke test before a full crawl with `TOP_N=3 python -m ingestion.scrape_standards`.

## Raw schema

- **`raw.standards`** — `rank, title, slug, composer, lyricist, year, original_source, detail_url, scraped_at`
- **`raw.recordings`** — `standard_slug, spotify_track_id, track_name, artist_name, artist_id, album_name, album_release_date, duration_ms, ingested_at`

Both tables are full-refreshed on every run.
