"""SupeRR Selector S2 - Round 1: Most reliable players under pressure.
Interactive companion to the methodology report (RR, IPL 2027 auction)."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).parent / "data"
import plotly.graph_objects as go
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
FIT = {
    "batters": {
        "Tim David": "Death overs: 207 of 334 pressure balls at the death, +28.5/100. Closest match to RR's death gap.",
        "Heinrich Klaasen": "Both gaps: +48 in overs 7-15 and +17 at the death. IPL-only rank 2.",
        "Shreyas Iyer": "Overs 7-15 +31 and death +72; IPL-only rank 5. Strong IPL-validated fit.",
        "Suryakumar Yadav": "Overs 7-15 specialist (+52/100 on 306 balls). Weaker at the death.",
        "Yashasvi Jaiswal": "Already at RR. Powerplay +92 on 130 balls. Retain.",
        "Abhishek Sharma": "Elite, but powerplay pressure batting is already RR's strength.",
    },
    "bowlers": {
        "Sunil Narine": "Rank 1 pooled and IPL-only. Overs 7-15 +19, death +61.",
        "Josh Hazlewood": "Only top-10 bowler strong at both ends: powerplay +50, death +61. Widest interval.",
        "Kuldeep Yadav": "Overs 7-15 +30 on 229 balls; wickets 7.1/100 vs par 5.3.",
        "Rashid Khan": "Largest sample (461 balls). Overs 7-15 +10, death +42.",
    },
}st.title("Who holds up when it matters?")
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

    plot = view.iloc[::-1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot["pressure"], y=plot["name"], mode="markers", name="Pressure rating",
        marker=dict(color=PINK, size=13),
        error_x=dict(type="data", symmetric=False,
                     array=plot["boot_hi"] - plot["pressure"], arrayminus=plot["pressure"] - plot["boot_lo"],
                     color="#9aa3bd", thickness=3),
        customdata=plot[["team", "p_balls", "cons_pct", "boot_lo", "boot_hi"]],
        hovertemplate="<b>%{y}</b> (%{customdata[0]})<br>Rating %{x:.1f}<br>90%% interval %{customdata[3]:.0f} to %{customdata[4]:.0f}<br>Pressure balls %{customdata[1]}<br>Consistency %{customdata[2]:.0f}%%<extra></extra>"))
    fig.add_trace(go.Scatter(x=plot["baseline"], y=plot["name"], mode="markers", name="Baseline (all situations)",
                             marker=dict(color="rgba(0,0,0,0)", size=11, line=dict(color=NAVY, width=2))))
    fig.update_layout(height=max(380, 46 * len(plot) + 120), margin=dict(l=10, r=10, t=30, b=10),
                      xaxis_title="Runs above situation-par per 100 high-pressure balls",
                      legend=dict(orientation="h", y=1.08), plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
    st.caption("Filled dot = pressure rating. Hollow dot = baseline from all situations. Bar = 90% bootstrap interval.")

    is_bat = role == "Batters"
    out = view[["rank", "name", "team", "pressure", "boot_lo", "boot_hi", "cons_pct", "p_ipl", "p_t20i",
                "sr_act", "sr_par", "out_act", "out_par", "ipl_only_rank", "top10_pct"]].copy()
    out.columns = ["Rank", "Player", "IPL 2026", "Rating", "Lo (5%)", "Hi (95%)", "Consistency %", "IPL balls", "T20I balls",
                   "SR actual" if is_bat else "Econ actual", "SR par" if is_bat else "Econ par",
                   "Outs/100" if is_bat else "Wkts/100", "Outs/100 par" if is_bat else "Wkts/100 par",
                   "IPL-only rank", "P(top-10) %"]
    st.dataframe(out.round(1), hide_index=True, width="stretch")
    st.download_button("Download table (CSV)", out.to_csv(index=False), f"{role.lower()}_view.csv", "text/csv")

with tab_player:
    role2 = st.radio("Role ", ["Batters", "Bowlers"], horizontal=True, key="role2")
    d2 = load(role2.lower()).sort_values("rank")
    name = st.selectbox("Player", d2["name"])
    p = d2[d2["name"] == name].iloc[0]
    st.subheader(f"{p['name']}  ·  {p['team']}  ·  rank {int(p['rank'])}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pressure rating", f"{p['pressure']:.1f}", f"{p['uplift']:+.1f} uplift vs baseline")
    m2.metric("90% interval", f"{p['boot_lo']:.0f} to {p['boot_hi']:.0f}")
    m3.metric("Consistency", f"{p['cons_pct']:.0f}%")
    m4.metric("P(top-10)", f"{p['top10_pct']:.0f}%")
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Pie(labels=["IPL", "T20I"], values=[p["p_ipl"], p["p_t20i"]], hole=0.55,
                               marker=dict(colors=[PINK, BLUE])))
        fig.update_layout(title="Where the pressure balls come from", height=320, margin=dict(t=50, b=10))
        st.plotly_chart(fig, width="stretch")
    with b:
        lab = ["Strike rate" if role2 == "Batters" else "Economy", "Dismissals/100" if role2 == "Batters" else "Wickets/100"]
        fig = go.Figure()
        fig.add_bar(name="Player", x=lab, y=[p["sr_act"], p["out_act"]], marker_color=PINK)
        fig.add_bar(name="Situation par", x=lab, y=[p["sr_par"], p["out_par"]], marker_color=NAVY)
        fig.update_layout(barmode="group", title="Actual vs situation-par (own pressure balls)", height=320, margin=dict(t=50, b=10))
        st.plotly_chart(fig, width="stretch")
    st.write(
        f"**Rank under each variant:** pooled {int(p['rank'])} · rating only {int(p['rating_only_rank'])} · "
        f"recency-weighted {int(p['recent_rank'])} · IPL balls only {'n/a' if pd.isna(p['ipl_only_rank']) else int(p['ipl_only_rank'])}. "
        f"Seasons beating par: {int(p['yrs_pos'])} of {int(p['yrs_tot'])}."
    )
    fit = FIT["batters" if role2 == "Batters" else "bowlers"].get(name)
    if fit:
        st.info(f"RR fit: {fit}")

