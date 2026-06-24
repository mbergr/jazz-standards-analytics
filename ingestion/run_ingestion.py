"""Run the full ingestion pipeline end-to-end: scrape standards, then fetch recordings.

Usage (from the repo root):
    python -m ingestion.run_ingestion
"""
from . import db
from . import scrape_standards
from . import spotify_recordings


def main():
    con = db.connect()
    db.bootstrap(con)

    print("==> Scraping standards from JazzStandards.com")
    standard_rows = scrape_standards.scrape()
    scrape_standards.load(con, standard_rows)
    print(f"    {len(standard_rows)} standards loaded into raw.standards")

    print("==> Fetching recordings from Spotify")
    recording_rows = spotify_recordings.fetch_all(con)
    spotify_recordings.load(con, recording_rows)
    print(f"    {len(recording_rows)} recordings loaded into raw.recordings")

    con.close()
    print("Done.")


if __name__ == "__main__":
    main()
