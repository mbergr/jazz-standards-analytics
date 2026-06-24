"""Central configuration for the ingestion pipeline.

Values come from environment variables (loaded from a local .env file when present),
with sensible defaults so the scraper runs out of the box. Only the Spotify
credentials are mandatory — and only for the recordings step.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Repo root = parent of this file's directory (ingestion/)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# --- Scraping (JazzStandards.com) ---
BASE_URL = "https://www.jazzstandards.com"
# How many top-ranked standards to ingest. MVP scope is the top 100.
TOP_N = int(os.getenv("TOP_N", "100"))
# Be polite: pause between every HTTP request (seconds).
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "1.0"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "jazz-standards-analytics/0.1 (portfolio project; "
    "+https://github.com/mbergr/jazz-standards-analytics)",
)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# --- Spotify Web API ---
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
RECORDINGS_PER_STANDARD = int(os.getenv("RECORDINGS_PER_STANDARD", "10"))

# --- Storage (DuckDB) ---
DATA_DIR = ROOT / "data"
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "jazz.duckdb")))
RAW_SCHEMA = "raw"
