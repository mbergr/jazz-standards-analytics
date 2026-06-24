"""Scrape the ranked jazz standards canon from JazzStandards.com into raw.standards.

The ranking lives across paginated index pages (index.htm, index2.htm, ...), each
listing 100 standards in popularity order. Each standard links to a detail page
(compositions-0/<slug>.htm) that holds composer, lyricist, year and original source.

Rank is taken from the order entries appear on the index pages — robust against
messy inline HTML. The remaining fields come from each detail page.
"""
import re
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import config
from . import db


def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": config.USER_AGENT})
    return s


def _get(session, url):
    resp = session.get(url, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    # JazzStandards.com is UTF-8 but doesn't declare it in headers; requests would
    # otherwise fall back to ISO-8859-1 and mangle smart quotes / accents.
    resp.encoding = resp.apparent_encoding or "utf-8"
    time.sleep(config.REQUEST_DELAY_SECONDS)
    return resp.text


def _index_url(page_num):
    """Page 1 is index.htm; subsequent pages are index2.htm, index3.htm, ..."""
    suffix = "" if page_num == 1 else str(page_num)
    return f"{config.BASE_URL}/compositions/index{suffix}.htm"


def parse_index(html, base_url):
    """Return an ordered, de-duplicated list of (slug, title, detail_url)."""
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "compositions-0/" not in href or not href.endswith(".htm"):
            continue
        detail_url = urljoin(base_url, href)
        slug = detail_url.rsplit("/", 1)[-1][:-4]  # strip trailing ".htm"
        title = a.get_text(strip=True)
        if not title or slug in seen:
            continue
        seen.add(slug)
        out.append((slug, title, detail_url))
    return out


_YEAR_RE = re.compile(r"\(\s*(\d{4})\s*\)")


def _origin_cells(soup):
    """Return the cell texts of the 'Origin and Chart Information' table, or None.

    That table lays out label/value cells, e.g.:
        ['Rank', '1', 'Music', 'Johnny Green', 'Lyrics', 'Edward Heyman', 'Robert Sour', ...]

    The site nests tables heavily, so several tables contain the 'Music'/'Rank'
    labels (the outer wrappers include the whole article). We want the innermost,
    compact one — i.e. the matching table with the fewest cells.
    """
    candidates = []
    for tbl in soup.find_all("table"):
        cells = [c.get_text(" ", strip=True) for c in tbl.find_all(["td", "th"])]
        if "Music" in cells and "Rank" in cells:
            candidates.append(cells)
    return min(candidates, key=len) if candidates else None


def parse_detail(html):
    """Pull composer, lyricist and year from a detail page.

    `original_source` (the originating show/film) lives only in free prose on the
    page, not in the structured table, so it's left NULL here and deferred to a
    later enrichment pass rather than scraped unreliably.
    """
    soup = BeautifulSoup(html, "html.parser")
    fields = {"composer": None, "lyricist": None, "year": None, "original_source": None}

    cells = _origin_cells(soup)
    if cells:
        i = cells.index("Music")
        if i + 1 < len(cells) and cells[i + 1] not in ("Lyrics", ""):
            fields["composer"] = cells[i + 1]
        if "Lyrics" in cells:
            j = cells.index("Lyrics")
            lyricists = []
            for c in cells[j + 1:]:
                if not c:
                    continue
                if len(c) > 40:  # safety net: real names are short, prose is not
                    break
                lyricists.append(c)
            if lyricists:
                fields["lyricist"] = ", ".join(lyricists)

    ym = _YEAR_RE.search(soup.get_text(" ", strip=True))
    if ym:
        fields["year"] = int(ym.group(1))
    return fields


def scrape(top_n=None):
    """Scrape up to `top_n` standards and return rows ready for raw.standards."""
    top_n = top_n or config.TOP_N
    session = _session()

    entries = []
    page = 1
    while len(entries) < top_n and page <= 10:
        url = _index_url(page)
        try:
            html = _get(session, url)
        except requests.HTTPError as e:
            print(f"  ! index page {url} failed: {e}", file=sys.stderr)
            break
        page_entries = parse_index(html, url)
        if not page_entries:
            break
        entries.extend(page_entries)
        page += 1
    entries = entries[:top_n]

    rows = []
    for rank, (slug, title, detail_url) in enumerate(entries, start=1):
        try:
            fields = parse_detail(_get(session, detail_url))
        except Exception as e:  # noqa: BLE001 - keep going on individual failures
            print(f"  ! detail failed for {slug}: {e}", file=sys.stderr)
            fields = {"composer": None, "lyricist": None, "year": None, "original_source": None}
        rows.append((
            rank, title, slug, fields["composer"], fields["lyricist"],
            fields["year"], fields["original_source"], detail_url, datetime.utcnow(),
        ))
        print(f"  [{rank}/{len(entries)}] {title}")
    return rows


def load(con, rows):
    """Full-refresh raw.standards with the scraped rows."""
    con.execute(f"DELETE FROM {config.RAW_SCHEMA}.standards;")
    if rows:
        con.executemany(
            f"INSERT INTO {config.RAW_SCHEMA}.standards VALUES (?,?,?,?,?,?,?,?,?)", rows
        )


def main():
    con = db.connect()
    db.bootstrap(con)
    rows = scrape()
    load(con, rows)
    n = con.execute(f"SELECT COUNT(*) FROM {config.RAW_SCHEMA}.standards").fetchone()[0]
    print(f"Loaded {n} standards into {config.RAW_SCHEMA}.standards")
    con.close()


if __name__ == "__main__":
    main()
