"""Local executive demonstrator. Read only from the last validated database."""

import json
import gzip
import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hardship Insights", page_icon="◈", layout="wide")
st.markdown("""<style>
.stApp {background:#f5f7fa;} h1,h2,h3 {color:#173449;}
[data-testid="stMetric"] {background:white;padding:18px;border:1px solid #e0e7ed;border-radius:10px;}
</style>""", unsafe_allow_html=True)
st.title("Hardship Insights")
st.caption("Independent case study · SYNTHETIC customer journeys · No real lender results")
root = Path(__file__).resolve().parents[1]
path = Path(os.environ.get("HARDSHIP_DASHBOARD_DB", str(root / "data/warehouse/hardship.duckdb")))
snapshot = Path(os.environ.get("HARDSHIP_DEMO_SNAPSHOT_PATH", str(root / "demo/snapshot.json.gz")))
demo_mode = os.environ.get("HARDSHIP_DEMO_MODE") == "1" or (not path.exists() and "HARDSHIP_DASHBOARD_DB" not in os.environ)
source_path = snapshot if demo_mode else path
if not source_path.exists():
    st.info("Build the data first: python -m hardship_insights.cli; or supply the bundled demo snapshot.")
    st.stop()


@st.cache_data(ttl=300, max_entries=4)
def load_data(filename, file_version, from_snapshot):
    # File size/mtime are explicit cache keys; publishing a new file invalidates it.
    if from_snapshot:
        payload = json.loads(gzip.decompress(Path(filename).read_bytes()))
        if payload.get("format_version") != 1:
            raise ValueError("Unsupported demo snapshot version")
        apps = pd.DataFrame(payload["applications"])
        episodes = pd.DataFrame(payload["outcomes"])
        for column in ["notice_date", "decision_date"]:
            apps[column] = pd.to_datetime(apps[column])
        return payload["metadata"], apps, episodes
    with duckdb.connect(filename, read_only=True) as con:
        meta = con.execute("select * from run_metadata").fetchdf().iloc[0].to_dict()
        apps = con.execute("select * from fct_application").fetchdf()
        episodes = con.execute("select * from fct_episode_outcome").fetchdf()
    return meta, apps, episodes


stat = source_path.stat()
metadata, applications, outcomes = load_data(str(source_path), (stat.st_mtime_ns, stat.st_size), demo_mode)
if metadata.get("build_scope") != "outcomes" or metadata.get("quality_status") != "passed":
    st.info("Run the full pipeline to create validated account and outcome models.")
    st.stop()
if demo_mode:
    st.caption("Public demo snapshot · Fixed synthetic dataset · Rebuild and export to update")

st.sidebar.header("Explore cohorts")
markets = st.sidebar.multiselect("Market", ["AU", "UK"], default=["AU", "UK"])
products = st.sidebar.multiselect("Product", sorted(applications["product"].unique()), default=sorted(applications["product"].unique()))
channels = st.sidebar.multiselect("Channel", sorted(applications["channel"].unique()), default=sorted(applications["channel"].unique()))
st.sidebar.caption("Rates need at least 20 eligible observations. Currency amounts are not pooled.")
st.caption(f"Observation cutoff: {metadata['cutoff']} · Metric version: {metadata['metric_version']} · Data checks: passed")
apps = applications[applications["jurisdiction"].isin(markets) & applications["product"].isin(products) & applications["channel"].isin(channels)].copy()
episodes = outcomes[outcomes["jurisdiction"].isin(markets) & outcomes["product"].isin(products) & outcomes["channel"].isin(channels)].copy()
if apps.empty:
    st.info("No requests match these filters. Select at least one market, product and channel.")
    st.stop()


def rate(numerator, denominator):
    return f"{numerator / denominator:.1%}" if denominator >= 20 else "Unavailable"


overview, outcome_tab, governance = st.tabs(["Support operations", "After assistance", "Trust and definitions"])
with overview:
    st.subheader("From request to decision")
    closed = apps.status.isin(["withdrawn", "lost_contact"]).sum()
    observed = apps.days_past_due.notna().sum()
    early = apps.days_past_due.eq(0).sum()
    pending = apps.status.eq("pending")
    decided = apps.decision_date.notna()
    days = (apps.loc[decided, "decision_date"] - apps.loc[decided, "notice_date"]).dt.days
    a, b, c, d = st.columns(4)
    a.metric("Requests", f"{len(apps):,}")
    b.metric("Application dropout", rate(closed, len(apps)))
    b.caption(f"{closed:,} withdrawn / lost contact out of {len(apps):,} requests")
    c.metric("Early contact", rate(early, observed))
    c.caption(f"{early:,} current at notice / {observed:,} known; {len(apps)-observed:,} unknown")
    d.metric("Median decision days", f"{days.median():.0f}" if len(days) >= 20 else "Unavailable")
    d.caption(f"{len(days):,} decided requests; {pending.sum():,} pending")
    left, right = st.columns(2)
    with left:
        st.markdown("**Request status**")
        st.bar_chart(apps.status.value_counts().rename("Requests"), color="#187f86")
    with right:
        st.markdown("**Requests by notice month**")
        trend = apps.assign(month=apps.notice_date.dt.to_period("M").astype(str)).groupby("month").size()
        st.line_chart(trend.rename("Requests"), color="#187f86")
    age = (pd.Timestamp(metadata["cutoff"]) - apps.loc[pending, "notice_date"]).dt.days
    st.caption(f"Pending age: median {age.median():.0f} calendar days." if len(age) >= 20 else "Pending age is unavailable for fewer than 20 pending requests.")
    st.info("Use this view to investigate delays and closure reasons. A faster decision alone does not establish appropriate support.")

with outcome_tab:
    st.subheader("Three month-end payment stability")
    st.caption("Current at each of the first three month-ends after assistance ends. This is a payment-status proxy, not a wellbeing measure or an exact 90-day window.")
    mature = int(episodes.mature.sum())
    eligible = int(episodes.eligible.sum())
    stable = int(episodes.is_stable.sum())
    missing = mature - eligible
    a, b, c, d = st.columns(4)
    a.metric("Assistance episodes", f"{len(episodes):,}")
    b.metric("Payment stability", rate(stable, eligible))
    b.caption(f"{stable:,} stable / {eligible:,} complete mature episodes")
    c.metric("Follow-up coverage", rate(eligible, mature))
    c.caption(f"{eligible:,} complete / {mature:,} mature episodes")
    d.metric("Not yet mature", f"{len(episodes)-mature:,}")
    d.caption(f"{missing:,} mature episodes have missing follow-up")
    records = []
    for cohort, frame in episodes.groupby("contact_cohort"):
        n, successes = int(frame.eligible.sum()), int(frame.is_stable.sum())
        records.append({"Contact at notice": cohort, "Episodes": len(frame), "Mature": int(frame.mature.sum()), "Complete follow-up": n, "Stable": successes, "Stability": rate(successes, n)})
    st.dataframe(pd.DataFrame(records), hide_index=True, width="stretch")
    st.warning("These differences come from authored simulation assumptions. Cohorts are descriptive; they do not show that early contact caused better outcomes.")
    st.markdown("**Suggested investigation:** inspect missing follow-up before comparing cohorts, then examine starting arrears, product and channel. Define a separate evaluation before recommending an intervention.")

with governance:
    st.subheader("Evidence behind this run")
    st.markdown("- Only a completed dbt build with passing tests is published.\n- Invalid submissions preserve the previous valid database.\n- Source hashes and configuration travel with the published database.\n- Rates with fewer than 20 eligible observations are unavailable; this is a demonstration display rule.")
    st.code(str(metadata["source_sha256"]), language=None)
    st.caption("SHA-256 of the request submission")
    manifest = json.loads(metadata["manifest_json"])
    st.dataframe(pd.DataFrame([{"File": name, "Rows": item["rows"], "SHA-256": item["sha256"]} for name, item in manifest["files"].items()]), hide_index=True)
    with st.expander("Simulation configuration and assumptions"):
        st.json(manifest["config"])
    st.markdown("Definitions: dropout includes explicit withdrawal/lost-contact closures; pending requests remain in its denominator. Early-contact rate excludes unknown arrears. Decision time includes decided cases only. Outcome eligibility requires a mature horizon and three observed month-ends.")
    st.caption("Owner: project author · Review status: demonstrator, not an approved production metric set · No public economic series integrated yet")
