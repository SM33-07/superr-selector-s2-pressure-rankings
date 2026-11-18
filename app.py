"""SupeRR Selector S2 - Round 1 final pressure rankings for RR."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"
PINK, NAVY, BLUE = "#EA1B85", "#0B1033", "#254AA5"

st.set_page_config(page_title="Players Under Pressure | RR IPL 2027", page_icon="🏏", layout="wide")

st.markdown(
    f"""<style>
.block-container {{padding-top:1.6rem;max-width:1250px}}
h1,h2,h3 {{color:{NAVY};letter-spacing:-0.01em}}
.hero {{background:linear-gradient(120deg,{NAVY} 0%,#17205a 70%);border-radius:22px;padding:34px 40px;position:relative;overflow:hidden;margin-bottom:18px}}
.hero:before {{content:"";position:absolute;right:-80px;top:-110px;width:340px;height:340px;border-radius:50%;background:{PINK}}}
.hero:after {{content:"";position:absolute;right:90px;top:70px;width:210px;height:210px;border-radius:50%;background:{BLUE};opacity:.85}}
.hero .eyebrow {{color:{PINK};font-weight:700;font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;position:relative;z-index:2}}
.hero h1 {{color:#fff;font-size:2.6rem;margin:6px 0 8px;position:relative;z-index:2;line-height:1.1}}
.hero p {{color:#b9bfe0;margin:0;max-width:640px;font-size:1.02rem;position:relative;z-index:2}}
.card {{background:#F6F5FA;border-radius:16px;padding:16px 20px;border:1px solid #E8E6F2;min-height:110px;display:flex;flex-direction:column;justify-content:center}}
.card .big {{font-size:1.9rem;font-weight:800;color:{PINK};line-height:1.1}}
.card .lbl {{font-size:.85rem;color:#5c6385}}
.pill {{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.75rem;font-weight:700;margin-right:6px}}
[data-testid="stMetricValue"] {{color:{PINK}}}
</style>""",
    unsafe_allow_html=True,
)

BATTER_FIT = {
    "Abhishek Sharma": "Elite performance, but limited marginal fit because RR already has a strong powerplay.",
    "Suryakumar Yadav": "Middle-overs specialist, +52 per 100 pressure balls over 306 balls.",
    "Heinrich Klaasen": "Addresses both middle overs (+48) and death (+17); IPL-only rank 2.",
    "Phil Salt": "Powerplay specialist, but overlaps RR's existing strength.",
    "Tim David": "207 death pressure balls, +28.5 per 100; closest match to RR's death-overs weakness.",
    "Travis Head": "Primarily a powerplay pressure sample; lower priority.",
    "Yashasvi Jaiswal": "Retain; strong existing powerplay contribution.",
    "Jos Buttler": "IPL-only rank 37; not a priority.",
    "Shreyas Iyer": "Middle +31, death +72; IPL-only rank 5.",
    "Andre Russell": "Lowest-conviction batter: raw runs versus par are approximately -6.5 per 100 pressure balls, with 9.8 dismissals per 100 versus his usual 7.4.",
}

BOWLER_FIT = {
    "Sunil Narine": "Rank 1 pooled and IPL-only; strong middle and death evidence.",
    "Rashid Khan": "Largest sample; good middle/death contribution, though IPL-only rank is 11.",
    "Kuldeep Yadav": "Middle-overs specialist, +30 per 100.",
    "Varun Chakravarthy": "Death +23; IPL-only rank 3.",
    "Jasprit Bumrah": "Restrictive at the death but below par in wickets and powerplay pressure performance.",
    "Josh Hazlewood": "Strong in both powerplay and death; wide interval.",
    "Mitchell Santner": "Powerplay +47 and middle +13; IPL-only rank 15.",
    "Krunal Pandya": "Middle overs +81; largest uplift, but weakly repeatable.",
    "Mustafizur Rahman": "T20I-heavy evidence: 83 IPL versus 215 T20I pressure balls; IPL-only rank 31.",
    "Mohsin Khan": "Low-confidence candidate, effectively tied with Noor Ahmad around 10th and backed by a small sample and wide 0–39 interval.",
}

ROBUSTNESS = [
    ("LI ≥ 1.25", "8/10", "7/10"),
    ("LI ≥ 2.0", "8/10", "8/10"),
    ("IPL balls only", "6/10", "7/10"),
    ("Recency-weighted", "7/10", "8/10"),
    ("Weaker shrinkage (150)", "9/10", "9/10"),
    ("Stronger shrinkage (1000)", "9/10", "9/10"),
    ("Rating only", "8/10", "8/10"),
    ("Consistency-heavy (50/50)", "8/10", "8/10"),
]

PHASE = {
    "Abhishek Sharma": (232, 92, 3), "Suryakumar Yadav": (112, 306, 91),
    "Heinrich Klaasen": (8, 131, 89), "Phil Salt": (151, 76, 14),
    "Tim David": (11, 116, 207), "Travis Head": (133, 35, 0),
    "Yashasvi Jaiswal": (130, 121, 7), "Jos Buttler": (146, 116, 58),
    "Shreyas Iyer": (87, 218, 74), "Andre Russell": (0, 63, 100),
    "Sunil Narine": (32, 211, 66), "Rashid Khan": (36, 297, 128),
    "Kuldeep Yadav": (5, 229, 115), "Varun Chakravarthy": (51, 239, 69),
    "Jasprit Bumrah": (135, 69, 144), "Josh Hazlewood": (121, 51, 102),
    "Mitchell Santner": (50, 160, 60), "Krunal Pandya": (17, 189, 10),
    "Mustafizur Rahman": (63, 69, 166), "Mohsin Khan": (36, 56, 51),
}

@st.cache_data
def load(role: str) -> pd.DataFrame:
    df = pd.read_csv(DATA / f"{role}.csv")
    df["team"] = df["ipl26"].fillna("—").replace({"": "—"})
    df["cons_pct"] = df["cons"] * 100
    df["top10_pct"] = df["p_top10_rating"] * 100
    df["interval"] = df["boot_lo"].astype(int).astype(str) + "–" + df["boot_hi"].astype(int).astype(str)
    return df.sort_values("rank").reset_index(drop=True)


def remove_pick(state_key: str, player: str) -> None:
    st.session_state[state_key] = [
        name for name in st.session_state[state_key] if name != player
    ]


def clear_picks() -> None:
    st.session_state["pick_batters"] = []
    st.session_state["pick_bowlers"] = []


def card(big: str, label: str) -> str:
    return f'<div class="card"><div class="big">{big}</div><div class="lbl">{label}</div></div>'

st.markdown(
    """<div class="hero"><div class="eyebrow">SupeRR Selector · Season 2 · Round 1</div>
<h1>Who holds up when it matters?</h1>
<p>A ball-by-ball model of the most reliable IPL batters and bowlers under pressure, built for Rajasthan Royals at the IPL 2027 auction.</p></div>""",
    unsafe_allow_html=True,
)
k = st.columns(4)
k[0].markdown(card("189,555", "deliveries analysed"), unsafe_allow_html=True)
k[1].markdown(card("32,615", "high-pressure deliveries · 18.3%"), unsafe_allow_html=True)
k[2].markdown(card("65 / 76", "eligible batters / bowlers"), unsafe_allow_html=True)
k[3].markdown(card("r = 0.05", "uplift repeatability"), unsafe_allow_html=True)
st.caption("Final eligibility population is report-published; full 65/76 export is not present in this repository.")

role = st.radio("Role", ["Batters", "Bowlers"], horizontal=True)
is_batters = role == "Batters"
df = load("batters" if is_batters else "bowlers")
fit = BATTER_FIT if is_batters else BOWLER_FIT

tabs = st.tabs(["My picks", "Rankings", "Compare", "Player", "Insights", "RR fit", "Method"])

with tabs[0]:
    st.subheader("Auction target board")
    st.caption(
        "Build a personal, session-only shortlist from the report-published top 10. "
        "Selections are not confirmed auction picks or evidence of player availability."
    )
    for key in ("pick_batters", "pick_bowlers"):
        if key not in st.session_state:
            st.session_state[key] = []

    st.button("Clear all selections", on_click=clear_picks, key="clear_picks")
    pick_columns = st.columns(2)
    for column, title, kind, key in (
        (pick_columns[0], "Batting targets", "batters", "pick_batters"),
        (pick_columns[1], "Bowling targets", "bowlers", "pick_bowlers"),
    ):
        options = load(kind)
        with column:
            st.subheader(title)
            st.caption(f"{len(st.session_state[key])} selected")
            st.multiselect(
                f"Add {title.lower()}",
                options["name"].tolist(),
                key=key,
                placeholder="Choose one or more players",
            )
            selected = options[options["name"].isin(st.session_state[key])]
            if selected.empty:
                st.info(f"No {title.lower()} selected yet.")
            for _, player in selected.iterrows():
                with st.container(border=True):
                    heading, remove = st.columns([4, 1])
                    heading.markdown(
                        f"**#{int(player['rank'])} · {player['name']}**"
                    )
                    remove.button(
                        "Remove",
                        key=f"remove_{key}_{player['name']}",
                        on_click=remove_pick,
                        args=(key, player["name"]),
                        use_container_width=True,
                    )
                    rating_metrics = st.columns(2)
                    rating_metrics[0].metric("Rating", f"{player['pressure']:.1f}")
                    rating_metrics[1].metric("90% interval", player["interval"])
                    sample_metrics = st.columns(2)
                    sample_metrics[0].metric("Consistency", f"{player['cons_pct']:.0f}%")
                    sample_metrics[1].metric("Pressure balls", f"{int(player['p_balls'])}")

with tabs[1]:
    st.subheader("Composite ranking vs raw pressure rating")
    st.caption("The report-published top 10 is shown here; the full eligible pool is 65 batters and 76 bowlers.")
    rank_by = st.selectbox("Rank by", ["Composite rank (report)", "Pressure rating"])
    view = df.sort_values("rank" if rank_by.startswith("Composite") else "pressure",
                          ascending=rank_by.startswith("Composite"), kind="stable")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=view["pressure"], y=view["name"], mode="markers+text", text=view["rank"].astype(str),
        textposition="middle right", marker=dict(color=PINK, size=14),
        error_x=dict(type="data", symmetric=False,
                     array=(view["boot_hi"] - view["pressure"]).values,
                     arrayminus=(view["pressure"] - view["boot_lo"]).values,
                     color="#9aa3bd", thickness=3),
        customdata=view[["boot_lo", "boot_hi", "p_balls", "cons_pct", "top10_pct"]],
        hovertemplate="<b>%{y}</b><br>Composite rank %{text}<br>Rating %{x:.1f}<br>90% interval %{customdata[0]:.0f}–%{customdata[1]:.0f}<br>Pressure balls %{customdata[2]}<br>Consistency %{customdata[3]:.0f}%<br>P(top-10) %{customdata[4]:.0f}%<extra></extra>",
    ))
    fig.update_layout(height=480, margin=dict(l=10,r=20,t=30,b=10), plot_bgcolor="white",
                      xaxis_title="Pressure rating: runs above situation-par per 100 balls")
    st.plotly_chart(fig, width="stretch")
    st.caption("Composite rank is not the same as sorting by the raw pressure rating.")
    out = view[["rank", "name", "team", "pressure", "interval", "cons_pct", "p_balls", "top10_pct"]].copy()
    out.columns = [
        "Rank", "Player", "IPL 2026 team", "Pressure Rating", "90% Interval",
        "Consistency", "Pressure Balls", "P(top-10)",
    ]
    out["Consistency"] = out["Consistency"].round(0).astype(int).astype(str) + "%"
    out["P(top-10)"] = out["P(top-10)"].round(0).astype(int).astype(str) + "%"
    st.dataframe(out.round(1), hide_index=True, width="stretch")
    st.download_button("Download shortlist (CSV)", out.to_csv(index=False), f"{role.lower()}_top10.csv", "text/csv")

with tabs[2]:
    st.subheader("Compare final top 10")
    names = st.multiselect("Select up to 4 players", df["name"].tolist(), default=df["name"].head(3).tolist(), max_selections=4)
    if names:
        selected = df[df["name"].isin(names)].set_index("name").loc[names]
        fig = go.Figure()
        palette = [PINK, BLUE, NAVY, "#F5A300"]
        labels = ["Rating","Consistency","P(top-10)","Pressure balls"]
        for i, name in enumerate(names):
            row = selected.loc[name]
            vals = [row["pressure"] / df["pressure"].max() * 100,
                    row["cons"] * 100,
                    row["top10_pct"],
                    row["p_balls"] / df["p_balls"].max() * 100]
            fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=labels + labels[:1],
                                          name=name, fill="toself", opacity=0.35,
                                          line=dict(color=palette[i])))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0,100],visible=False)), height=500)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(selected[["rank","pressure","boot_lo","boot_hi","cons_pct","p_balls","top10_pct"]]
                     .rename(columns={"rank":"Rank","pressure":"Rating","boot_lo":"Lo","boot_hi":"Hi",
                                      "cons_pct":"Consistency %","p_balls":"Pressure balls","top10_pct":"P(top-10) %"}),
                     width="stretch")
    else:
        st.info("Select at least one player.")

with tabs[3]:
    name = st.selectbox("Player", df["name"].tolist())
    p = df[df["name"] == name].iloc[0]
    st.subheader(f"{p['name']} · composite rank {int(p['rank'])}")
    m = st.columns(3)
    m[0].metric("Pressure rating", f"{p['pressure']:.1f}")
    m[1].metric("90% interval", p["interval"])
    m[2].metric("Consistency", f"{p['cons_pct']:.0f}%")
    sample_metrics = st.columns(2)
    sample_metrics[0].metric("P(top-10)", f"{p['top10_pct']:.0f}%")
    sample_metrics[1].metric("Pressure balls", f"{int(p['p_balls'])}")
    fig = go.Figure(go.Bar(
        x=["Powerplay","Overs 7–15","Death"], y=list(PHASE[name]),
        marker_color=[PINK,BLUE,NAVY],
    ))
    fig.update_layout(height=360, plot_bgcolor="white",
                      yaxis_title="Pressure balls", title="Pressure balls by phase",
                      margin=dict(l=10, r=10, t=55, b=20))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Phase sample: {sum(PHASE[name])} pressure balls "
        f"{'bowled' if not is_batters else 'faced'} (total published sample: {int(p['p_balls'])})."
    )
    if name == "Mohsin Khan":
        st.warning(
            "Low-confidence ranking: Mohsin is effectively tied with Noor Ahmad "
            "around 10th, with a small 143-ball sample and a very wide 90% interval "
            "of approximately 0–39."
        )
    with st.container(border=True):
        st.markdown("**RR squad-fit interpretation**")
        st.write(fit[name])

with tabs[4]:
    st.subheader("Robustness: top-10 players retained")
    robustness = pd.DataFrame({
        "Specification": [row[0] for row in ROBUSTNESS],
        "Batters": [row[1] for row in ROBUSTNESS],
        "Bowlers": [row[2] for row in ROBUSTNESS],
    })
    st.dataframe(robustness, hide_index=True, width="stretch")
    st.markdown("**Repeatability: overall level vs pressure-specific uplift**")
    repeatability = pd.DataFrame({
        "Measure": ["Overall pressure rating", "Pressure-specific uplift", "Consistency / hit rate"],
        "Batters": ["0.42", "0.05", "0.08"],
        "Bowlers": ["0.39", "0.05", "0.09"],
    })
    repeat_cols = st.columns([1.1, 1])
    repeat_cols[0].dataframe(repeatability, hide_index=True, width="stretch")
    measures = repeatability["Measure"].tolist()
    fig = go.Figure()
    for label, values, color in (
        ("Batters", [0.42, 0.05, 0.08], PINK),
        ("Bowlers", [0.39, 0.05, 0.09], NAVY),
    ):
        fig.add_bar(
            name=label, x=measures, y=values, marker_color=color,
            text=[f"{value:.2f}" for value in values], textposition="outside",
        )
    fig.update_layout(
        barmode="group", height=330, yaxis=dict(range=[0, 0.5], title="Split-half correlation"),
        margin=dict(l=10, r=10, t=20, b=80), plot_bgcolor="white",
        legend=dict(orientation="h", y=1.12),
    )
    repeat_cols[1].plotly_chart(fig, width="stretch")
    st.caption(
        "Overall level is more repeatable than the pressure-specific uplift. "
        "Full-sample Spearman–Brown approximate reliability: 0.60 for batters and 0.56 for bowlers."
    )
    st.warning("Ranks 6–10 are close in uncertainty to 11–15. Composite ranking should be read with the 90% intervals.")

with tabs[5]:
    st.subheader("Where RR is weak under pressure (2025–26)")
    gaps = pd.DataFrame(
        [["+70", "+12", "−5"], ["−12", "−11", "−6"]],
        index=["Batting", "Bowling"],
        columns=["Powerplay", "Overs 7–15", "Death"],
    )
    st.table(gaps)
    st.caption("Runs above situation-par per 100 high-pressure balls.")
    st.caption("Phase comparisons are directional and based on approximately 100 overs per side.")
    st.write("RR batting is strong in the powerplay, slightly above par in overs 7–15, and below par at the death. "
             "RR bowling is below par in all three phases.")
    c1,c2 = st.columns(2)
    c1.metric("Batting sample", "632 pressure balls", "rank 3 of 10")
    c2.metric("Bowling sample", "669 pressure balls", "rank 5 of 10")

    st.markdown("**RR existing-squad batting pressure ratings**")
    batting_rr = pd.DataFrame([
        ("Vaibhav Sooryavanshi","+54.3","82 — watch item: small sample"),
        ("Yashasvi Jaiswal","+22.2","258"),("Riyan Parag","+14.3","240"),
        ("Dasun Shanaka","+13.7","200"),("Donovan Ferreira","+10.6","58"),
        ("Shimron Hetmyer","+9.1","265"),("Dhruv Jurel","+6.0","227"),
        ("Ravindra Jadeja","+4.0","232"),("Sam Curran","+2.2","209"),
        ("Shubham Dubey","+1.8","59"),
    ], columns=["Player","Rating","Pressure balls"])
    st.table(batting_rr)

    st.markdown("**RR existing-squad bowling pressure ratings**")
    bowling_rr = pd.DataFrame([
        ("Ravindra Jadeja","+11.9","232"),("Jofra Archer","+8.9","200"),
        ("Ravi Bishnoi","+8.3","512"),("Kuldeep Sen","+1.9","81"),
        ("Brijesh Sharma","+1.2","89"),("Sandeep Sharma","-1.8","200"),
        ("Tushar Deshpande","-2.1","218"),("Adam Milne","-5.2","96"),
        ("Sam Curran","-8.4","268"),("Kwena Maphaka","-8.5","48"),
        ("Dasun Shanaka","-9.5","85"),("Nandre Burger","-11.6","90"),
    ], columns=["Player","Rating","Pressure balls"])
    st.table(bowling_rr)

    st.markdown("**Recommended pursuit order**")
    left,right = st.columns(2)
    left.markdown("""
- Batting: Tim David and Heinrich Klaasen
- Shreyas Iyer and Suryakumar Yadav
- Retain Yashasvi Jaiswal
""")
    right.markdown("""
- Bowling: Sunil Narine, Josh Hazlewood,
  Kuldeep Yadav and Rashid Khan
""")
    st.info("Player availability is not established by this model. These are analytical pursuits, not confirmed auction availability.")

with tabs[6]:
    st.subheader("How the rating is built")
    overview = st.columns(3)
    overview[0].metric("Deliveries", "189,555")
    overview[1].metric("Matches", "803")
    overview[2].metric("High-pressure deliveries", "32,615 · 18.3%")

    st.markdown("**Pressure and delivery value**")
    st.write(
        "High pressure is Leverage Index (LI) ≥ 1.5. Delivery value is runs plus "
        "the change in expected future runs after versus before the delivery. "
        "Players are compared with situation-par and adjusted for opposition."
    )
    st.markdown("**Estimation and score**")
    st.write(
        "Opposition-adjusted two-block ridge regression separates baseline level "
        "from pressure-specific uplift. Penalties were selected through cross-validation: "
        "400 for baseline and 8,000 for uplift. Final Composite = 85% Pressure Rating "
        "+ 15% Consistency. Consistency is the share of pressure innings or spells "
        "beating par, shrunk using a 12-appearance prior."
    )
    st.markdown("**Uncertainty and repeatability**")
    st.write(
        "Intervals are the 5th–95th percentiles of 40 match-level bootstrap resamples. "
        "P(top-10) is the proportion of bootstrap samples in which a player's pressure "
        "rating ranks in the top 10; it is not a guarantee."
    )
    st.dataframe(
        pd.DataFrame({
            "Measure": ["Overall pressure rating", "Pressure-specific uplift", "Consistency / hit rate"],
            "Batters": ["0.42", "0.05", "0.08"],
            "Bowlers": ["0.39", "0.05", "0.09"],
        }),
        hide_index=True, width="stretch",
    )
    st.caption("Full-sample Spearman–Brown approximate reliability is 0.60 for batters and 0.56 for bowlers.")

    st.markdown("**Final eligibility and dashboard coverage**")
    eligibility = st.columns(2)
    eligibility[0].markdown(
        "- Batters: at least 90 high-pressure balls faced\n"
        "- Bowlers: at least 60 high-pressure balls bowled\n"
        "- Both: at least 20 matches and one 2025–26 appearance\n"
        "- Both: at least 60 IPL high-pressure balls"
    )
    eligibility[1].markdown(
        "**Final eligible population:** 65 batters and 76 bowlers.\n\n"
        "**Dashboard data:** report-published top 10 for each role; complete "
        "eligible-player exports are not available here.\n\n"
        "Reeza Hendricks (0 IPL pressure balls) and Blessing Muzarabani "
        "(4) are excluded by the IPL sample rule."
    )
    with st.expander("Model limitations and implementation details"):
        st.markdown(
            "- Venue and pitch conditions are not fully modelled.\n"
            "- Toss and dew effects are not included.\n"
            "- Batter–bowler matchup effects are not included.\n"
            "- Batting position beyond phase and wicket context is not fully modelled.\n"
            "- Injuries, current form, and teammate effects are not included.\n"
            "- The win-probability model is state-only and does not model team strength or venue.\n"
            "- First-innings expected-run valuation is applied to chases; situation-cell adjustment addresses the resulting bias.\n"
            "- Wides, no-balls, and free hits are approximated."
        )

st.divider()
st.caption("SupeRR Selector Season 2 · Final Round 1 report values. Composite ranks, not raw rating order.")
