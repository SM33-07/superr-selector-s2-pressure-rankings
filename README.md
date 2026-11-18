# SupeRR Selector S2 · Round 1 · Pressure dashboard

An interactive companion to the Rajasthan Royals (RR) IPL 2027 auction
methodology report, highlighting reliable batters and bowlers under pressure.

## Run locally

```shell
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Push this folder to a public GitHub repository, then on
[Streamlit Community Cloud](https://share.streamlit.io/) select the repository,
the `main` branch, and `app.py` as the main file.

## Data provenance and limitations

The included `data/batters.csv` and `data/bowlers.csv` are the eligible-player
pressure-ranking tables used by this dashboard. Raw ball-by-ball and match
inputs are not included in this repository. Rankings cover 803 IPL and men's
T20I matches from 2022–2026; DLS matches, super overs, and non-IPL/T20I games
are excluded. Pakistan national-team players are excluded from the pool.

Pressure is defined using a Leverage Index threshold of 1.5. Player ratings
compare outcomes with situation-par expectations and use shrinkage for sample
size. The methodology notes that the pressure-specific component is less
repeatable than overall performance, so rankings emphasize performance level.
The RR phase-gap comparison is directional because it is based on about 100
overs per side. Venue and pitch conditions, dew, matchups, batting position
beyond phase, and teammate effects are not modelled. Player availability is
not confirmed by these rankings.
