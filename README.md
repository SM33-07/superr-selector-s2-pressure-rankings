# SupeRR Selector S2 · Round 1 · Pressure dashboard

An interactive companion to the final Round 1 pressure report for the
Rajasthan Royals IPL 2027 auction. The dashboard uses the report-published
composite top-10 rankings and player profiles.

## Run locally

```shell
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Push this folder to a public GitHub repository, then on
[Streamlit Community Cloud](https://share.streamlit.io/) select the repository,
the `main` branch, and `app.py` as the main file.

## Data provenance and eligibility

The final report states 65 eligible batters and 76 eligible bowlers. Its
eligibility rules require at least 90 batter or 60 bowler high-pressure balls,
at least 20 matches, at least one 2025–26 appearance, and at least 60 IPL
high-pressure balls. Reeza Hendricks and Blessing Muzarabani are excluded.

The repository contained only superseded CSVs, without the PDF, original
analysis pipeline, raw ball-by-ball data, or final 65/76 exports. Therefore,
the included `data/batters.csv` and `data/bowlers.csv` contain only the
report-published top-10 shortlist. They do not claim to be the complete final
eligible populations. Filtration or renumbering of the old CSVs was not used.
The final report is the source of truth for these displayed rankings.

The final report PDF was available at
`C:\Users\SOHAM\Downloads\SupeRR_Round1_Pressure_Report.pdf` and was checked
against the values implemented here. It is not committed to the repository.

## Method and limitations

The analysis covers 189,555 deliveries from 803 matches and 32,615
high-pressure deliveries (18.3% of deliveries). Pressure uses Leverage Index ≥ 1.5. Outcomes are
valued against situation-par expectations and estimated with opposition-
adjusted two-block ridge regression, with 400 baseline penalty and 8,000
uplift penalty. The final score is 85% pressure rating and 15% consistency,
with a 12-appearance consistency prior and 40 match-level bootstrap resamples.

Pressure-specific uplift repeats weakly (approximately r = 0.05), despite
stronger repeatability of the overall pressure rating. The ranking should not
be interpreted as confirmed player availability. The model does not fully
account for venue/pitch, toss/dew, batter–bowler matchups, batting position
beyond phase/wickets, injuries, current form, teammate effects, or team strength
and venue in the state-only win-probability model. Wides, no-balls and free hits
are approximated.
