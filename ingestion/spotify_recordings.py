"""Fetch recordings for each standard from the Spotify Web API into raw.recordings.

Uses the Client Credentials flow (app-only auth, no user login needed) to search
Spotify for each standard's title and land the top results as candidate recordings.
Matching standards to the *right* recordings is intentionally left to later dbt
layers — raw simply lands what the search returns.
"""
import sys
import time
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from . import config
from . import db


def client():
    """Build an authenticated Spotipy client, or exit with a helpful message."""
    if not config.SPOTIFY_CLIENT_ID or not config.SPOTIFY_CLIENT_SECRET:
        raise SystemExit(
            "Missing Spotify credentials. Copy .env.example to .env and set "
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET "
            "(create an app at https://developer.spotify.com/dashboard)."
        )
    auth = SpotifyClientCredentials(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
    )
    return spotipy.Spotify(auth_manager=auth, requests_timeout=config.REQUEST_TIMEOUT, retries=3)


def search_recordings(sp, slug, title, limit):
    """Search Spotify for a standard's title and return raw.recordings rows.

    Note: the search returns *candidate* recordings — any track whose name matches
    the title, including unrelated modern songs that happen to share it. Matching
    candidates to the actual jazz standard (entity resolution) is deferred to the
    dbt intermediate layer, per the project's decision log.
    """
    results = sp.search(q=f'track:"{title}"', type="track", limit=limit)
    items = results.get("tracks", {}).get("items", [])
    rows = []
    for t in items:
        artist = (t.get("artists") or [{}])[0]
        album = t.get("album") or {}
        rows.append((
            slug,
            t.get("id"),
            t.get("name"),
            artist.get("name"),
            artist.get("id"),
            album.get("name"),
            album.get("release_date"),
            t.get("duration_ms"),
            datetime.utcnow(),
        ))
    return rows


def fetch_all(con):
    """Search recordings for every standard already in raw.standards."""
    sp = client()
    standards = con.execute(
        f"SELECT slug, title FROM {config.RAW_SCHEMA}.standards ORDER BY rank"
    ).fetchall()
    all_rows = []
    for i, (slug, title) in enumerate(standards, start=1):
        try:
            rows = search_recordings(sp, slug, title, config.RECORDINGS_PER_STANDARD)
        except Exception as e:  # noqa: BLE001 - keep going on individual failures
            print(f"  ! search failed for {title}: {e}", file=sys.stderr)
            rows = []
        all_rows.extend(rows)
        print(f"  [{i}/{len(standards)}] {title}: {len(rows)} recordings")
        time.sleep(config.REQUEST_DELAY_SECONDS)
    return all_rows


def load(con, rows):
    """Full-refresh raw.recordings with the fetched rows."""
    con.execute(f"DELETE FROM {config.RAW_SCHEMA}.recordings;")
    if rows:
        con.executemany(
            f"INSERT INTO {config.RAW_SCHEMA}.recordings VALUES (?,?,?,?,?,?,?,?,?)", rows
        )


def main():
    con = db.connect()
    db.bootstrap(con)
    if con.execute(f"SELECT COUNT(*) FROM {config.RAW_SCHEMA}.standards").fetchone()[0] == 0:
        raise SystemExit("raw.standards is empty — run scrape_standards first.")
    rows = fetch_all(con)
    load(con, rows)
    n = con.execute(f"SELECT COUNT(*) FROM {config.RAW_SCHEMA}.recordings").fetchone()[0]
    print(f"Loaded {n} recordings into {config.RAW_SCHEMA}.recordings")
    con.close()


if __name__ == "__main__":
    main()
