from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from careers_wealth_comparison.loader import load_scenarios
from careers_wealth_comparison.simulator import Config, find_break_even_age, simulate

_SCENARIOS_PATH = Path(__file__).parent / "data" / "raw" / "scenarios.json"

st.set_page_config(page_title="Career Wealth Comparison", layout="wide")
st.title("Career Wealth Comparison")

scenarios = load_scenarios(_SCENARIOS_PATH)

with st.sidebar:
    st.header("Parameters")
    current_age = st.slider("Current age", min_value=22, max_value=55, value=37)
    retirement_age = st.slider("Retirement age", min_value=50, max_value=75, value=65)
    cost_of_living = st.slider(
        "Annual cost of living (€)", min_value=20_000, max_value=150_000, value=50_000, step=1_000
    )
    investment_return_rate = (
        st.slider("Investment return rate (%)", min_value=1, max_value=15, value=7) / 100
    )
    starting_net_worth = st.slider(
        "Starting net worth (€)", min_value=0, max_value=500_000, value=50_000, step=5_000
    )

if retirement_age <= current_age:
    st.warning("Retirement age must be greater than current age.")
    st.stop()

config = Config(
    current_age=current_age,
    retirement_age=retirement_age,
    cost_of_living=cost_of_living,
    investment_return_rate=investment_return_rate,
    starting_net_worth=starting_net_worth,
)

projections = simulate(scenarios, config)
break_even_ages = find_break_even_age(projections, baseline_name=scenarios[0].name)

# --- Chart ---
fig = go.Figure()
for proj in projections:
    ages = sorted(proj.net_worth_by_age)
    net_worths = [proj.net_worth_by_age[a] for a in ages]
    fig.add_trace(go.Scatter(x=ages, y=net_worths, mode="lines", name=proj.name, line=dict(width=2)))

for scenario_name, age in break_even_ages.items():
    if age is not None:
        fig.add_vline(
            x=age,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"{scenario_name} break-even: age {age}",
            annotation_position="top right",
        )

fig.update_layout(
    xaxis_title="Age",
    yaxis_title="Net Worth (€)",
    yaxis_tickprefix="€",
    yaxis_tickformat=",.0f",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=60),
)
st.plotly_chart(fig, use_container_width=True)

# --- Break-even messages ---
for scenario_name, age in break_even_ages.items():
    if age is None:
        st.info(
            f"**{scenario_name}** never surpasses **{scenarios[0].name}** "
            "within the simulation horizon."
        )
    else:
        st.success(f"**{scenario_name}** surpasses **{scenarios[0].name}** at age **{age}**.")

# --- Summary table ---
st.subheader("Net Worth at Retirement")
summary_df = pd.DataFrame(
    {
        "Scenario": [p.name for p in projections],
        "Net Worth at Retirement": [
            f"€{p.net_worth_by_age.get(retirement_age, 0):,.0f}" for p in projections
        ],
    }
)
st.dataframe(summary_df, use_container_width=True, hide_index=True)
