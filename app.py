"""SupeRR Selector S2 - Round 1: Most reliable players under pressure.
Interactive companion to the methodology report (RR, IPL 2027 auction)."""
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


st.title("Who holds up when it matters?")
st.caption("SupeRR Selector Season 2 · Round 1 · Most reliable players under pressure for Rajasthan Royals · IPL 2027 auction")

