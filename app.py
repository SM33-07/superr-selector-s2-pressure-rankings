"""SupeRR Selector S2 - Round 1: Most reliable players under pressure.
Interactive companion to the methodology report (RR, IPL 2027 auction)."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"
PINK, NAVY, BLUE, GREY = "#EA1B85", "#0B1033", "#254AA5", "#C9CEE0"

st.set_page_config(page_title="Players Under Pressure | RR IPL 2027", page_icon="🏏", layout="wide")

st.markdown(
    f"""<style>
.block-container {{padding-top: 1.6rem; max-width: 1250px;}}
h1, h2, h3 {{color: {NAVY}; letter-spacing: -0.01em;}}
.hero {{background: linear-gradient(120deg, {NAVY} 0%, #17205a 70%); border-radius: 22px; padding: 34px 40px; position: relative; overflow: hidden; margin-bottom: 18px;}}
.hero:before {{content: ""; position: absolute; right: -80px; top: -110px; width: 340px; height: 340px; border-radius: 50%; background: {PINK};}}
.hero:after {{content: ""; position: absolute; right: 90px; top: 70px; width: 210px; height: 210px; border-radius: 50%; background: {BLUE}; opacity: .85;}}
.hero .eyebrow {{color: {PINK}; font-weight: 700; font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; position: relative; z-index: 2;}}
.hero h1 {{color: #fff; font-size: 2.6rem; margin: 6px 0 8px; position: relative; z-index: 2; line-height: 1.1;}}
.hero p {{color: #b9bfe0; margin: 0; max-width: 640px; font-size: 1.02rem; position: relative; z-index: 2;}}
.card {{background: #F6F5FA; border-radius: 16px; padding: 16px 20px; border: 1px solid #E8E6F2;}}
.card .big {{font-size: 1.9rem; font-weight: 800; color: {PINK}; line-height: 1.1;}}
.card .lbl {{font-size: .85rem; color: #5c6385;}}
.pill {{display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .75rem; font-weight: 700; margin-right: 6px;}}
.pill.high {{background: #dff5e8; color: #14753f;}} .pill.medium {{background: #fff1d6; color: #8a5a00;}} .pill.low {{background: #fde0e0; color: #a12020;}}
.pill.flag {{background: #e6eaff; color: {BLUE};}}
[data-testid="stMetricValue"] {{color: {PINK};}}
</style>""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ data
FIT = {
    "Tim David": "Death overs: 207 of 334 pressure balls at the death, +28.5/100. Closest match to RR's death gap.",
    "Heinrich Klaasen": "Both gaps: +48 in overs 7-15 and +17 at the death. IPL-only rank 2.",
    "Shreyas Iyer": "Overs 7-15 +31 and death +72; IPL-only rank 5. Strong IPL-validated fit.",
    "Suryakumar Yadav": "Overs 7-15 specialist (+52/100 on 306 balls). Weaker at the death.",
    "Yashasvi Jaiswal": "Already at RR. Powerplay +92 on 130 balls. Retain.",
    "Abhishek Sharma": "Elite, but powerplay pressure batting is already RR's strength.",
    "Phil Salt": "Powerplay specialist (+54 on 151 balls); overlaps RR's existing strength.",
    "Travis Head": "Powerplay-only pressure sample; lower priority.",
    "Jos Buttler": "Solid, not special; IPL-only rank 37. Not a priority.",
    "Reeza Hendricks": "No IPL pressure sample (T20I only); cannot be validated for the IPL.",
    "Sunil Narine": "Rank 1 pooled and IPL-only. Overs 7-15 +19, death +61.",
    "Josh Hazlewood": "Only top-10 bowler strong at both ends: powerplay +50, death +61. Widest interval.",
    "Kuldeep Yadav": "Overs 7-15 +30 on 229 balls; wickets 7.1/100 vs par 5.3.",
    "Rashid Khan": "Largest sample (461 balls). Overs 7-15 +10, death +42.",
    "Varun Chakravarthy": "Death +23 (69 balls); middle overs about par. IPL-only rank 3.",
    "Jasprit Bumrah": "Death +25 on 144 balls, but powerplay -25 and fewer wickets than par: restrictive, not penetrative.",
    "Blessing Muzarabani": "T20I-only evidence (4 IPL pressure balls). Low confidence for the IPL.",
    "Mitchell Santner": "Powerplay +47 (50 balls), overs 7-15 +13. IPL-only rank 15.",
    "Krunal Pandya": "Overs 7-15 +81 on 189 balls; largest uplift but the least repeatable component.",
    "Mustafizur Rahman": "T20I-heavy (83 IPL vs 215 T20I pressure balls); IPL-only rank 31.",
}
# Pressure balls faced/bowled by phase (powerplay / overs 7-15 / death), report Section 7.
PHASE = {
    "Abhishek Sharma": (232, 92, 3), "Suryakumar Yadav": (112, 306, 91), "Heinrich Klaasen": (8, 131, 89),
    "Phil Salt": (151, 76, 14), "Tim David": (11, 116, 207), "Travis Head": (133, 35, 0),
    "Yashasvi Jaiswal": (130, 121, 7), "Jos Buttler": (146, 116, 58), "Shreyas Iyer": (87, 218, 74),
    "Reeza Hendricks": (53, 78, 16),
    "Sunil Narine": (32, 211, 66), "Rashid Khan": (36, 297, 128), "Kuldeep Yadav": (5, 229, 115),
    "Varun Chakravarthy": (51, 239, 69), "Jasprit Bumrah": (135, 69, 144), "Josh Hazlewood": (121, 51, 102),
    "Blessing Muzarabani": (66, 13, 72), "Mitchell Santner": (50, 160, 60), "Krunal Pandya": (17, 189, 10),
    "Mustafizur Rahman": (63, 69, 166),
}


@st.cache_data
def load(kind: str) -> pd.DataFrame:
    df = pd.read_csv(DATA / f"{kind}.csv")
    df["team"] = df["ipl26"].fillna("-").replace({"-": "No 2026 squad"})
    df["cons_pct"] = df["cons"] * 100
    df["top10_pct"] = df["p_top10_rating"] * 100
    df["ipl_share"] = df["p_ipl"] / df["p_balls"]
    df["confidence"] = np.select([df["top10_pct"] >= 80, df["top10_pct"] >= 50], ["High", "Medium"], "Low")
    df["interval"] = df["boot_lo"].round(0).astype(int).astype(str) + " to " + df["boot_hi"].round(0).astype(int).astype(str)
    df["evidence"] = np.where(df["ipl_share"] < 0.4, "T20I-heavy", "IPL-backed")
    return df.sort_values("rank").reset_index(drop=True)


def card(big: str, label: str) -> str:
    return f'<div class="card"><div class="big">{big}</div><div class="lbl">{label}</div></div>'


# ------------------------------------------------------------------ header
st.markdown(
    """<div class="hero"><div class="eyebrow">SupeRR Selector · Season 2 · Round 1</div>
<h1>Who holds up when it matters?</h1>
<p>A ball-by-ball model of the most reliable IPL batters and bowlers under pressure, built for Rajasthan Royals at the IPL 2027 auction.</p></div>""",
    unsafe_allow_html=True,
)
k = st.columns(4)
k[0].markdown(card("189,555", "deliveries analysed"), unsafe_allow_html=True)
k[1].markdown(card("803", "IPL + T20I matches, 2022-26"), unsafe_allow_html=True)
k[2].markdown(card("18%", "of deliveries are high-pressure"), unsafe_allow_html=True)
k[3].markdown(card("r = 0.42 / 0.39", "split-half reliability of level (batters / bowlers)"), unsafe_allow_html=True)
st.write("")

ROLE = st.radio("Role", ["Batters", "Bowlers"], horizontal=True, key="role")
IS_BAT = ROLE == "Batters"
df = load(ROLE.lower())
UNIT = ("Strike rate", "Dismissals/100") if IS_BAT else ("Economy", "Wickets/100")

tabs = st.tabs(["My picks", "Rankings", "Compare", "Player", "Insights", "RR fit", "Method"])
t_picks, t_rank, t_cmp, t_player, t_ins, t_rr, t_method = tabs

# ------------------------------------------------------------------ picks
with t_picks:
    st.subheader(f"Top 10 {ROLE.lower()} under pressure")
    top = df.head(10)
    show = pd.DataFrame({
        "Rank": top["rank"], "Player": top["name"], "IPL 2026": top["team"], "Rating": top["pressure"],
        "90% interval": top["interval"], "Consistency %": top["cons_pct"].round(0), "Pressure balls": top["p_balls"],
        "P(top-10) %": top["top10_pct"].round(0), "Confidence": top["confidence"], "Evidence": top["evidence"],
        "Why / fit for RR": top["name"].map(FIT).fillna(""),
    })
    st.dataframe(
        show, hide_index=True, width="stretch",
        column_config={
            "Rating": st.column_config.ProgressColumn("Rating", min_value=0, max_value=50, format="%.1f",
                                                       help="Runs above situation-par per 100 high-pressure balls"),
            "Why / fit for RR": st.column_config.TextColumn(width="large"),
        },
    )
    st.caption("Confidence = share of 40 bootstrap resamples in which the player stays in the top 10 (High 80%+, Medium 50-80%, Low below 50%). "
               "T20I-heavy = under 40% of pressure balls come from the IPL.")
    bat, bowl = load("batters").head(10), load("bowlers").head(10)
    with st.expander("Copy-ready lists for the submission form"):
        st.code("BATTERS\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(bat["name"], 1)) +
                "\n\nBOWLERS\n" + "\n".join(f"{i}. {n}" for i, n in enumerate(bowl["name"], 1)), language="text")

# ------------------------------------------------------------------ rankings
with t_rank:
    f1, f2, f3, f4 = st.columns(4)
    top_n = f1.slider("Show top N", 5, 30, 10)
    teams = f2.multiselect("IPL 2026 team", sorted(df["team"].unique()))
    min_balls = f3.slider("Min pressure balls", 0, int(df["p_balls"].max()), 0, step=10)
    rank_by = f4.selectbox("Rank by", ["Composite rank (report)", "Pressure rating", "IPL-only rank", "Recent form rank"])

    view = df[df["p_balls"] >= min_balls]
    if teams:
        view = view[view["team"].isin(teams)]
    sorters = {"Composite rank (report)": ("rank", True), "Pressure rating": ("pressure", False),
               "IPL-only rank": ("ipl_only_rank", True), "Recent form rank": ("recent_rank", True)}
    col, asc = sorters[rank_by]
    view = view.dropna(subset=[col]).sort_values(col, ascending=asc).head(top_n)

    if view.empty:
        st.warning("No players match these filters.")
    else:
        plot = view.iloc[::-1]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot["pressure"], y=plot["name"], mode="markers", name="Pressure rating", marker=dict(color=PINK, size=13),
            error_x=dict(type="data", symmetric=False, array=plot["boot_hi"] - plot["pressure"],
                         arrayminus=plot["pressure"] - plot["boot_lo"], color="#9aa3bd", thickness=3),
            customdata=plot[["team", "p_balls", "cons_pct", "boot_lo", "boot_hi"]],
            hovertemplate="<b>%{y}</b> (%{customdata[0]})<br>Rating %{x:.1f}<br>90% interval %{customdata[3]:.0f} to %{customdata[4]:.0f}"
                          "<br>Pressure balls %{customdata[1]}<br>Consistency %{customdata[2]:.0f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=plot["baseline"], y=plot["name"], mode="markers", name="Baseline (all situations)",
                                 marker=dict(color="rgba(0,0,0,0)", size=11, line=dict(color=NAVY, width=2)),
                                 hovertemplate="Baseline %{x:.1f}<extra></extra>"))
        fig.update_layout(height=max(380, 44 * len(plot) + 130), margin=dict(l=10, r=10, t=30, b=10),
                          xaxis_title="Runs above situation-par per 100 high-pressure balls",
                          legend=dict(orientation="h", y=1.08), plot_bgcolor="white")
        st.plotly_chart(fig, width="stretch")
        st.caption("Filled dot = pressure rating. Hollow dot = baseline from all situations. Bar = 90% bootstrap interval.")

        out = view[["rank", "name", "team", "pressure", "boot_lo", "boot_hi", "cons_pct", "p_ipl", "p_t20i", "sr_act", "sr_par",
                    "out_act", "out_par", "ipl_only_rank", "top10_pct"]].copy()
        out.columns = ["Rank", "Player", "IPL 2026", "Rating", "Lo (5%)", "Hi (95%)", "Consistency %", "IPL balls", "T20I balls",
                       f"{UNIT[0]} actual", f"{UNIT[0]} par", f"{UNIT[1]}", f"{UNIT[1]} par", "IPL-only rank", "P(top-10) %"]
        st.dataframe(out.round(1), hide_index=True, width="stretch")
        st.download_button("Download table (CSV)", out.to_csv(index=False), f"{ROLE.lower()}_view.csv", "text/csv")

# ------------------------------------------------------------------ compare
with t_cmp:
    names = df["name"].tolist()
    sel = st.multiselect("Pick up to 4 players", names, default=names[:3], max_selections=4)
    axes = {"Pressure rating": "pressure", "Baseline level": "baseline", "Consistency": "cons",
            "Top-10 stability": "p_top10_rating", "IPL evidence": "ipl_share"}
    pct = df[list(axes.values())].rank(pct=True) * 100
    pct["Recent form"] = (1 - df["recent_rank"].rank(pct=True)) * 100 + 1
    labels = list(axes.keys()) + ["Recent form"]
    if sel:
        fig = go.Figure()
        palette = [PINK, BLUE, NAVY, "#F5A300"]
        for i, n in enumerate(sel):
            idx = df.index[df["name"] == n][0]
            vals = [pct.loc[idx, c] for c in list(axes.values())] + [pct.loc[idx, "Recent form"]]
            fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=labels + labels[:1], name=n, fill="toself", opacity=0.45,
                                          line=dict(color=palette[i % 4])))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100], showticklabels=False)), height=520,
                          margin=dict(t=30, b=30), legend=dict(orientation="h", y=-0.05))
        a, b = st.columns([1.1, 1])
        a.plotly_chart(fig, width="stretch")
        cmp = df[df["name"].isin(sel)].set_index("name").loc[sel]
        tbl = pd.DataFrame({"Rank": cmp["rank"], "Rating": cmp["pressure"].round(1), "Baseline": cmp["baseline"].round(1),
                            "Consistency %": cmp["cons_pct"].round(0), "Pressure balls": cmp["p_balls"],
                            "IPL balls": cmp["p_ipl"], "IPL-only rank": cmp["ipl_only_rank"], "Confidence": cmp["confidence"]}).T
        b.dataframe(tbl.astype(str), width="stretch")
        st.caption("Radar axes are percentile ranks within the whole eligible pool for this role (100 = best).")
    else:
        st.info("Select at least one player.")

# ------------------------------------------------------------------ player
with t_player:
    name = st.selectbox("Player", df["name"])
    p = df[df["name"] == name].iloc[0]
    st.subheader(f"{p['name']}  ·  {p['team']}  ·  rank {int(p['rank'])}")
    st.markdown(f'<span class="pill {p["confidence"].lower()}">{p["confidence"]} confidence</span>'
                f'<span class="pill flag">{p["evidence"]}</span>', unsafe_allow_html=True)
    m = st.columns(4)
    m[0].metric("Pressure rating", f"{p['pressure']:.1f}", f"{p['uplift']:+.1f} uplift vs baseline")
    m[1].metric("90% interval", p["interval"])
    m[2].metric("Consistency", f"{p['cons_pct']:.0f}%")
    m[3].metric("P(top-10)", f"{p['top10_pct']:.0f}%")
    a, b, c = st.columns(3)
    with a:
        fig = go.Figure(go.Pie(labels=["IPL", "T20I"], values=[p["p_ipl"], p["p_t20i"]], hole=0.55, marker=dict(colors=[PINK, BLUE])))
        fig.update_layout(title="Source of pressure balls", height=300, margin=dict(t=50, b=10))
        st.plotly_chart(fig, width="stretch")
    with b:
        fig = go.Figure()
        fig.add_bar(name="Player", x=list(UNIT), y=[p["sr_act"], p["out_act"]], marker_color=PINK)
        fig.add_bar(name="Situation par", x=list(UNIT), y=[p["sr_par"], p["out_par"]], marker_color=NAVY)
        fig.update_layout(barmode="group", title="Actual vs par", height=300, margin=dict(t=50, b=10))
        st.plotly_chart(fig, width="stretch")
    with c:
        if name in PHASE:
            fig = go.Figure(go.Bar(x=["Powerplay", "Overs 7-15", "Death"], y=list(PHASE[name]), marker_color=[PINK, BLUE, NAVY]))
            fig.update_layout(title="Pressure balls by phase", height=300, margin=dict(t=50, b=10))
            st.plotly_chart(fig, width="stretch")
        else:
            st.caption("Phase split is shown for the top-10 players only.")
    st.write(f"**Rank under each variant:** pooled {int(p['rank'])} · rating only {int(p['rating_only_rank'])} · "
             f"recency-weighted {int(p['recent_rank'])} · IPL balls only "
             f"{'n/a' if pd.isna(p['ipl_only_rank']) else int(p['ipl_only_rank'])}. "
             f"Seasons beating par: {int(p['yrs_pos'])} of {int(p['yrs_tot'])}.")
    if name in FIT:
        st.info(f"RR fit: {FIT[name]}")

# ------------------------------------------------------------------ insights
with t_ins:
    st.subheader("Level repeats. “Clutch” doesn’t.")
    left, right = st.columns(2)
    with left:
        fig = go.Figure()
        cats = ["Pressure rating (level)", "Pressure-specific uplift", "Consistency (hit rate)"]
        fig.add_bar(name="Batters", x=cats, y=[0.42, 0.05, 0.08], marker_color=PINK, text=[0.42, 0.05, 0.08], textposition="outside")
        fig.add_bar(name="Bowlers", x=cats, y=[0.39, 0.05, 0.09], marker_color=NAVY, text=[0.39, 0.05, 0.09], textposition="outside")
        fig.update_layout(barmode="group", height=380, yaxis_title="Split-half correlation", yaxis_range=[0, 0.5],
                          plot_bgcolor="white", margin=dict(t=20, b=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
    with right:
        top10 = df["rank"] <= 10
        fig = go.Figure()
        for flag, color, nm, size in [(False, GREY, "Other eligible players", 7), (True, PINK, "Top 10", 11)]:
            d = df[top10 == flag]
            fig.add_trace(go.Scatter(x=d["baseline"], y=d["uplift"], mode="markers", name=nm, text=d["name"],
                                     marker=dict(color=color, size=size),
                                     hovertemplate="%{text}<br>Baseline %{x:.1f}<br>Uplift %{y:+.2f}<extra></extra>"))
        fig.add_hline(y=0, line_color="#9aa3bd", line_dash="dot")
        fig.update_layout(height=380, xaxis_title="Baseline rating (all situations)", yaxis_title="Pressure-specific uplift",
                          plot_bgcolor="white", margin=dict(t=20, b=10), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
    st.caption("Uplift stays close to zero for nearly everyone, while baseline varies widely. Players who do well under pressure "
               "are mostly just very good players, so the ranking leans on level.")

    st.subheader("Does the ranking survive pooled vs IPL-only evidence?")
    d3 = df.dropna(subset=["ipl_only_rank"]).query("rank <= 25")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 45], y=[1, 45], mode="lines", line=dict(color="#c6cbe0", dash="dash"), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=d3["rank"], y=d3["ipl_only_rank"], mode="markers+text", text=d3["name"], textposition="top center",
                             textfont=dict(size=10), marker=dict(color=PINK, size=10), showlegend=False,
                             hovertemplate="%{text}<br>Pooled %{x} · IPL-only %{y}<extra></extra>"))
    fig.update_layout(height=520, xaxis_title="Pooled rank (IPL + T20I)", yaxis_title="IPL-only rank (lower is better)",
                      xaxis=dict(range=[0, 26]), yaxis=dict(range=[0, 45], autorange="reversed"), plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
    st.caption("Points far below the dashed line lean on T20I evidence; points near it hold up on IPL balls alone.")

    st.markdown("**Stress tests: how many of the top 10 stay in the top 10?**")
    st.dataframe(pd.DataFrame({
        "Specification": ["LI ≥ 1.25 (24% of balls)", "LI ≥ 2.0 (11% of balls)", "IPL balls only", "Recency-weighted (2-yr half-life)",
                          "Weaker shrinkage (150)", "Stronger shrinkage (1000)", "Rating only", "Consistency-heavy (50/50)"],
        "Batters": ["8/10", "10/10", "6/10", "7/10", "9/10", "9/10", "8/10", "8/10"],
        "Bowlers": ["7/10", "9/10", "6/10", "8/10", "8/10", "9/10", "7/10", "9/10"]}), hide_index=True, width="stretch")
    st.warning("Ranks 6-10 are within statistical noise of 11-15. The firm names are Abhishek Sharma, Suryakumar Yadav and "
               "Heinrich Klaasen (batters), and Sunil Narine and Varun Chakravarthy (bowlers).")

# ------------------------------------------------------------------ RR fit
with t_rr:
    st.subheader("Where RR is weak under pressure (2025-26)")
    gaps = pd.DataFrame({"Powerplay": [70, -12], "Overs 7-15": [12, -11], "Death": [-5, -6]}, index=["Batting", "Bowling"])
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for col, color in zip(gaps.columns, [PINK, BLUE, NAVY]):
            fig.add_bar(name=col, x=gaps.index, y=gaps[col], marker_color=color)
        fig.update_layout(barmode="group", height=380, yaxis_title="Runs vs par per 100 pressure balls", plot_bgcolor="white",
                          margin=dict(t=20), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
        st.caption("About 100 overs per side, so directional. Source: methodology report, Section 7.")
    with c2:
        sub = df.head(10)
        sub = sub[sub["name"].isin(PHASE)]
        fig = go.Figure()
        for i, (ph, color) in enumerate(zip(["Powerplay", "Overs 7-15", "Death"], [PINK, BLUE, NAVY])):
            fig.add_bar(name=ph, y=sub["name"][::-1], x=[PHASE[n][i] for n in sub["name"][::-1]], orientation="h", marker_color=color)
        fig.update_layout(barmode="stack", height=380, xaxis_title=f"Pressure balls ({'faced' if IS_BAT else 'bowled'})",
                          plot_bgcolor="white", margin=dict(t=20), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Where each top-10 {ROLE.lower()[:-1]} actually meets pressure, to match against RR's gaps.")

    st.markdown("**Suggested order of pursuit (if available):**")
    pa, pb = st.columns(2)
    pa.markdown("**Batting**\n- Tim David and Heinrich Klaasen (death / middle)\n- Shreyas Iyer and Suryakumar Yadav (middle)\n- Retain Yashasvi Jaiswal")
    pb.markdown("**Bowling**\n- Sunil Narine and Josh Hazlewood\n- Kuldeep Yadav and Rashid Khan (middle overs)")
    st.info("Availability is unconfirmed: retention lists were due 17 Nov 2026 and the mini-auction is on 16 Dec 2026 in Goa.")

# ------------------------------------------------------------------ method
with t_method:
    st.markdown(
        """
**1. Pressure = leverage.** For every delivery, the Leverage Index (LI) is the expected absolute change in win probability across possible outcomes, scaled so the mean is 1. High-pressure means LI ≥ 1.5 (18% of deliveries).

**2. Value of a ball.** Runs scored + expected future runs after − before, so a wicket costs what it cost at that moment.

**3. Compare like with like.** Two-block ridge regression: situation cell + player baseline + player pressure uplift, minus opposition terms. Shrinkage controls sample size (penalties 400 and 8,000, chosen by match-grouped cross-validation).

**4. Final score.** 85% pressure rating + 15% consistency (share of pressure innings/spells beating par, shrunk to the league rate).

**Scope.** 803 IPL and men's T20I matches (2022-26), 189,555 deliveries. Excluded: DLS matches, super overs, non-IPL/T20I games. Pakistan national-team players removed from the pool (no IPL appearances since 2009).

**Not modelled.** Venue/pitch, dew, matchups, batting position beyond phase, team-mate effects.
"""
    )

st.divider()
st.caption("Independent analysis for SupeRR Selector Season 2 (Rajasthan Royals x Unstop). Ratings are model estimates with wide "
           "intervals, not predictions. Built with Python, pandas, Plotly and Streamlit.")