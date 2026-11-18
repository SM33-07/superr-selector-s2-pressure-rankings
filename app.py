"""SupeRR Selector S2 - Round 1: Most reliable players under pressure.
Interactive companion to the methodology report (RR, IPL 2027 auction)."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"
import streamlit as st

PINK, NAVY, BLUE = "#EA1B85", "#0B1033", "#254AA5"

st.set_page_config(page_title="Players Under Pressure | RR IPL 2027", page_icon="🏏", layout="wide")
st.markdown(
    f"""<style>
    .block-container {{padding-top: 2rem;}}
    h1, h2, h3 {{color: {NAVY};}}
    [data-testid="stMetricValue"] {{color: {PINK};}}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_data
def load(kind: str) -> pd.DataFrame:
    df = pd.read_csv(DATA / f"{kind}.csv")
    df["team"] = df["ipl26"].fillna("-").replace({"-": "No 2026 squad"})
    df["cons_pct"] = df["cons"] * 100
    df["top10_pct"] = df["p_top10_rating"] * 100
    return df
st.title("Who holds up when it matters?")
st.caption("SupeRR Selector Season 2 · Round 1 · Most reliable players under pressure for Rajasthan Royals · IPL 2027 auction")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Deliveries analysed", "189,555")
c2.metric("Matches (IPL + T20I, 2022-26)", "803")
c3.metric("High-pressure balls", "18%")
c4.metric("Split-half reliability (level)", "r = 0.42 / 0.39")

tab_rank, tab_player, tab_robust, tab_rr, tab_method = st.tabs(
    ["Rankings", "Player explorer", "Robustness", "RR fit", "Method"]
)

# ---------------------------------------------------------------- Rankings
with tab_rank:
    role = st.radio("Role", ["Batters", "Bowlers"], horizontal=True)
    df = load(role.lower())
    f1, f2, f3, f4 = st.columns([1, 1, 1, 1])
    top_n = f1.slider("Show top N", 5, 30, 10)
    teams = f2.multiselect("IPL 2026 team", sorted(df["team"].unique()))
    min_balls = f3.slider("Min pressure balls", 0, int(df["p_balls"].max()), 0, step=10)
    rank_by = f4.selectbox("Rank by", ["Composite rank (report)", "Pressure rating", "IPL-only rank", "Recent form rank"])

    view = df[df["p_balls"] >= min_balls]
    if teams:
        view = view[view["team"].isin(teams)]
    if rank_by == "Composite rank (report)":
        view = view.sort_values("rank")
    elif rank_by == "Pressure rating":
        view = view.sort_values("pressure", ascending=False)
    elif rank_by == "IPL-only rank":
        view = view.dropna(subset=["ipl_only_rank"]).sort_values("ipl_only_rank")
    else:
        view = view.sort_values("recent_rank")
    view = view.head(top_n).reset_index(drop=True)

