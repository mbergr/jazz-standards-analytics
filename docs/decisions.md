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
