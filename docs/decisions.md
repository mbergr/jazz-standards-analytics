# Decision log

Short notes on non-obvious choices, in chronological order.

## 2026-06 — Initial scope
- **Standards universe:** start with the top ~100 standards from JazzStandards.com.
  Expand to ~500 only after the full pipeline works end-to-end. Reason: a working
  MVP beats a bigger dataset with no marts.
- **DuckDB over Postgres/BigQuery:** zero infrastructure, file-based, and dbt-duckdb
  keeps the transformation layer identical to a warehouse setup. Skills transfer 1:1.
- **One recording = one fact row:** deduplication of near-identical releases
  (remasters, compilations) handled in the intermediate layer, documented per rule.

## 2026-06 — Ingestion findings (steps 02.1 / 02.2)
- **`original_source` left NULL at ingestion:** the originating show/film lives only
  in free prose on the JazzStandards.com detail page, not in the structured table.
  Scraping it reliably is hard, so it's deferred to a later enrichment pass rather
  than landed as noise.
- **Spotify `popularity` is not available:** apps created under Spotify's late-2024
  API restrictions get trimmed track objects (no `popularity`, no `preview_url`) and
  the batch `/tracks` endpoint returns 403. We dropped `popularity` from
  `raw.recordings` instead of keeping an always-NULL column.
- **Spotify search lands *candidates*, not matches:** `track:"<title>"` returns any
  track with that name, including unrelated modern songs that share the title
  (precision varies — "'Round Midnight" is clean, "Body and Soul" is noisy). Entity
  resolution (candidate → the real jazz standard) is an intermediate-layer job, not
  an ingestion one. This keeps raw faithful to the source.
