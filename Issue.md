# Build career wealth comparison pipeline and Streamlit dashboard

## Problem Statement

I want to understand how my long-run wealth (net worth at retirement) would differ if I stay in my current career as a Data Scientist versus taking a career break to become a doctor. Right now there is no tool to project and compare net worth over a working lifetime under these two career paths. Without a quantitative model I cannot reason about the opportunity cost of the career break, the years of negative cash flow from tuition, or the crossover point where the higher doctor salary might eventually catch up.

## Solution

A Python simulation pipeline backed by a Streamlit dashboard that:

1. Reads career scenarios from a single JSON file, each scenario containing an age-keyed schedule of annual cash flows (positive for salary years, negative for tuition years).
2. Simulates net worth year-by-year for each scenario from the user's current age to retirement age, applying a configurable investment return rate and cost of living.
3. Presents the results in an interactive Streamlit dashboard with sliders for all configuration parameters, a comparative line chart, a break-even age annotation, and a retirement-age summary table.

## User Stories

1. As a user, I want to load career scenario data from a single JSON file, so that I can edit salary and tuition assumptions without touching code.
2. As a user, I want each scenario to be identified by a name (e.g. "DS", "Doctor"), so that the chart and table are clearly labelled.
3. As a user, I want annual cash flow values to support negative numbers, so that tuition years are correctly represented as money going out of pocket.
4. As a user, I want annual cash flow to be keyed by career age (integer), so that the simulation aligns naturally with my current age.
5. As a user, I want to configure my current age via a slider, so that I can model my real starting point.
6. As a user, I want to configure my retirement age via a slider, so that I can explore retiring earlier or later.
7. As a user, I want to configure my annual cost of living via a slider, so that I can adjust for where I live.
8. As a user, I want to configure an annual investment return rate via a slider, so that I can stress-test optimistic vs pessimistic market assumptions.
9. As a user, I want to configure a starting net worth via a slider, so that I can seed the simulation with my real savings today.
10. As a user, I want the simulation to compound net worth annually at the investment return rate, so that the opportunity cost of the career break is accurately reflected.
11. As a user, I want negative net worth to compound symmetrically at the same return rate, so that the model does not artificially hide the cost of tuition years.
12. As a user, I want cost of living to be deducted uniformly every year for all scenarios, so that the comparison is on a level playing field.
13. As a user, I want to see a line chart with one line per scenario showing net worth on the Y-axis and age on the X-axis, so that I can compare trajectories at a glance.
14. As a user, I want the chart to update instantly when I move any slider, so that I can explore assumptions interactively.
15. As a user, I want to see a break-even age annotation on the chart (the first age at which the doctor path exceeds the DS path), so that I can understand when the career switch pays off.
16. As a user, I want to be informed clearly if no break-even age exists within the simulation horizon, so that I am not misled into thinking one will eventually occur.
17. As a user, I want a summary table showing the final net worth at retirement age for each scenario, so that I can compare end-state outcomes directly.
18. As a user, I want the dashboard to run locally with a single command, so that I can use it without any cloud infrastructure.
19. As a user, I want to add a third scenario to the JSON file and have it automatically appear on the chart, so that I can compare more than two career paths without touching code.
20. As a user, I want the simulation logic to be independent of the dashboard framework, so that I could swap Streamlit for another tool later.

## Implementation Decisions

- **Simulation module**: A pure function `simulate(scenarios, config) → list[WealthProjection]` holds all financial logic. It takes a list of `Scenario` objects and a config object and returns one `WealthProjection` per scenario. It has no dependency on Streamlit or file I/O.

- **Net worth formula**: For each age from `current_age` to `retirement_age` (inclusive):
  `net_worth[age] = net_worth[age - 1] × (1 + investment_return_rate) + annual_cash_flow[age] − cost_of_living`
  The first year seeds from `starting_net_worth`.

- **Negative net worth**: Compounded symmetrically at `investment_return_rate` (no floor, no separate borrowing rate). This makes the opportunity cost of tuition years honest and keeps the formula uniform.

- **Missing cash flow ages**: If a scenario's JSON does not contain an entry for a given age, `annual_cash_flow` defaults to `0` for that year.

- **Break-even age**: Computed after simulation as the first age where a non-baseline scenario's net worth strictly exceeds the baseline scenario's net worth. If none exists, the dashboard surfaces a clear message rather than omitting the annotation silently. The baseline is the first scenario in the JSON array.

- **Scenario data file**: A single `scenarios.json` in `data/raw/`, structured as a list of objects: `[{"name": "...", "cash_flows": {"30": 130000, "31": 140000, ...}}, ...]`. Keys are string-encoded ages (standard JSON); the loader converts them to integers.

- **Configuration**: Five parameters — `current_age`, `retirement_age`, `cost_of_living`, `investment_return_rate`, `starting_net_worth` — exposed as Streamlit sliders in the sidebar. No separate config file is required; defaults are hardcoded in the app.

- **Dashboard layout**: Streamlit single-page app. Sidebar holds all five sliders. Main area shows the comparative Plotly line chart followed by the summary table. Break-even age rendered as a vertical line or text callout on the chart.

- **New dependencies**: `streamlit`, `plotly`, `pandas`.

## Testing Decisions

- **What makes a good test**: Assert on the outputs of `simulate()` given controlled inputs. Do not assert on internal computation steps, intermediate variables, or Streamlit widget state. A test is good if it breaks when the financial logic is wrong and stays green when implementation details change.

- **Primary seam**: `simulate(scenarios, config) → list[WealthProjection]`. This is the only seam that needs tests. It is a pure function — deterministic, no side effects, no file I/O.

- **Cases to cover**:
  - Single scenario, single year: verify the exact net worth formula.
  - Positive net worth compounds correctly over multiple years.
  - Negative net worth (tuition year) compounds symmetrically.
  - Break-even age is identified correctly when one scenario overtakes another.
  - Break-even age returns `None` when no crossover exists within the horizon.
  - Cash flow defaults to `0` for ages absent from the scenario's schedule.

- **Modules not tested**: The Streamlit app (UI behaviour, slider rendering) and the JSON loader (trivial file read + type coercion) do not warrant dedicated tests.

- **Prior art**: No tests exist in the repo yet. This will be the first test suite.

## Out of Scope

- Tax modelling (income tax, capital gains tax).
- Loan/debt amortisation — tuition is modelled as negative cash flow only, with no separate debt ledger or amortisation schedule.
- Per-scenario or per-phase cost of living — cost of living is a single global value applied uniformly.
- Inflation adjustment — all values are in nominal dollars.
- Salary growth rate or annual raise modelling — salary trajectories are fully encoded in the cash flow schedule.
- Healthcare, malpractice insurance, or specialty-specific costs.
- Deployment to any cloud or hosted environment.
- Saving or exporting simulation results.

## Further Notes

- Domain vocabulary is defined in `CONTEXT.md` at the repo root. Use `Scenario`, `Annual cash flow`, `WealthProjection`, `Net worth`, `Break-even age`, and `Retirement age` consistently throughout the codebase.
- Residency years (modest positive salary after med school) are encoded directly in the Doctor scenario's cash flow schedule — no special modelling concept is needed.
- The baseline scenario for break-even comparison is the first scenario in the JSON array.
