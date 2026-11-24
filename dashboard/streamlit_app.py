"""Jazz Standards Repertoire Analytics — Streamlit dashboard.

Reads the exported marts/metrics CSVs in dashboard/data/ (produced by
export_marts.py) so it runs anywhere, including Streamlit Community Cloud, without
the local DuckDB file. Refresh the data with `python dashboard/export_marts.py`.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).resolve().parent / "data"
ACCENT = "#D9A44E"
ACCENT_SCALE = ["#3b4252", "#8a7a3e", ACCENT]

st.set_page_config(page_title="Jazz Standards Analytics", page_icon="🎷", layout="wide")


@st.cache_data
def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv")


kpis = load("kpis").iloc[0]
most_recorded = load("most_recorded")
longevity = load("longevity")
composers = load("composer_footprint")
artists = load("artists")
eras = load("era_distribution")


def style(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        font=dict(color="#E7ECF5"),
        coloraxis_showscale=False,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.07)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)", zeroline=False)
    return fig


# ---------------- Header ----------------
st.title("🎷 Jazz Standards Repertoire Analytics")
st.caption(
    "An end-to-end analytics engineering project over the jazz standards canon · "
    "Python → DuckDB → dbt → Streamlit · "
    "[source](https://github.com/mbergr/jazz-standards-analytics)"
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Standards", int(kpis.standards_total))
c2.metric("Recordings", int(kpis.recordings))
c3.metric("Artists", int(kpis.artists))
c4.metric("Composers", int(kpis.composers))
c5.metric("Composed", f"{int(kpis.earliest_composed)}–{int(kpis.latest_composed)}")

st.divider()

# ---------------- Most-recorded ----------------
st.subheader("Most-recorded standards")
top = most_recorded.head(15).sort_values("recording_count")
fig = px.bar(
    top, x="recording_count", y="title", orientation="h",
    color="recording_count", color_continuous_scale=ACCENT_SCALE,
    labels={"recording_count": "Recordings", "title": ""},
)
fig.update_traces(hovertemplate="%{y}<br>%{x} recordings<extra></extra>")
st.plotly_chart(style(fig, 440), use_container_width=True)
st.caption("⚠️ Recordings per standard are capped at 10 by the ingestion limit, so this ranks within what was fetched.")

st.divider()

# ---------------- Composer footprint + Eras ----------------
left, right = st.columns(2)

with left:
    st.subheader("Composer footprint")
    cf = composers.head(12).sort_values("total_recordings")
    fig = px.bar(
        cf, x="total_recordings", y="composer", orientation="h",
        color="total_recordings", color_continuous_scale=ACCENT_SCALE,
        labels={"total_recordings": "Recordings", "composer": ""},
        hover_data={"standards_in_canon": True},
    )
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption("Co-written credits form their own group (not split).")

with right:
    st.subheader("Recordings by jazz era")
    fig = px.bar(
        eras, x="jazz_era", y="recordings",
        color="recordings", color_continuous_scale=ACCENT_SCALE,
        labels={"jazz_era": "", "recordings": "Recordings"},
        category_orders={"jazz_era": eras["jazz_era"].tolist()},
    )
    st.plotly_chart(style(fig), use_container_width=True)
    st.caption("By Spotify *release* year, not recording date — reissues inflate the modern era.")

st.divider()

# ---------------- Longevity ----------------
st.subheader("Standard longevity")
st.caption("How long each standard kept being recorded. Bubble size = number of recordings.")
fig = px.scatter(
    longevity, x="composed_year", y="span_years",
    size="recording_count", color="eras_spanned",
    color_continuous_scale=ACCENT_SCALE, hover_name="title",
    labels={"composed_year": "Year composed", "span_years": "Recording span (years)",
            "eras_spanned": "Eras"},
)
fig.update_coloraxes(showscale=True)
st.plotly_chart(style(fig, 420), use_container_width=True)

st.divider()

# ---------------- Widest repertoire ----------------
st.subheader("Widest repertoire")
wr = artists.head(15).sort_values("standards_recorded")
fig = px.bar(
    wr, x="standards_recorded", y="artist_name", orientation="h",
    color="standards_recorded", color_continuous_scale=ACCENT_SCALE,
    labels={"standards_recorded": "Distinct standards recorded", "artist_name": ""},
)
st.plotly_chart(style(fig, 440), use_container_width=True)

# ---------------- Caveats ----------------
with st.expander("Data notes & caveats"):
    st.markdown(
        """
- **Scope:** the top 100 standards from JazzStandards.com; up to 10 Spotify recordings each.
- **Entity resolution:** Spotify candidates are matched to a standard by normalized title, then
  deduplicated to one recording per (standard, artist). This drops false positives like
  "Summertime Sadness", at the cost of a few legitimate variants.
- **Release year ≠ recording date:** Spotify dates are release dates, so reissues shift recordings
  into later eras and can make a standard's first "recording" year precede its composition year.
- **Most-recorded is capped** at the ingestion limit, not a true canon count.

Built with Python · DuckDB · dbt · Streamlit. Pipeline, tests and docs on
[GitHub](https://github.com/mbergr/jazz-standards-analytics).
        """
    )
