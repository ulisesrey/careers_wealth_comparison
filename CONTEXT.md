# Careers Wealth Comparison

A personal financial simulation that projects net worth over a working lifetime under different career paths, letting you compare the long-run wealth impact of staying in your current career versus switching careers (including periods of zero or negative income).

## Language

**Scenario**:
A named career path with an age-keyed schedule of annual cash flows. The data file holds all scenarios; a simulation is always run for every scenario and results compared.
_Avoid_: career, option, path, branch

**Annual cash flow**:
The net money received (positive) or paid out of pocket (negative) in a single year of a Scenario. A tuition year has a negative value; a salary year has a positive value.
_Avoid_: salary, income, earnings (too narrow — they exclude tuition outflows)

**Career break**:
A contiguous span of ages within a Scenario where annual cash flow is negative because the person is paying tuition out of pocket rather than earning a salary.
_Avoid_: training period, gap year, school years

**Net worth**:
The accumulated wealth of a person at a given age: the previous year's net worth compounded at the investment return rate, plus annual cash flow, minus cost of living. Can be negative.
_Avoid_: savings, wealth, balance

**WealthProjection**:
The ordered time series of net worth values produced by simulating a single Scenario from the person's current age to their retirement age. One WealthProjection per Scenario.
_Avoid_: simulation output, results, forecast

**Break-even age**:
The first age at which a non-baseline Scenario's net worth first exceeds the baseline Scenario's net worth. May not exist if the alternative never catches up within the horizon.
_Avoid_: crossover point, payoff age

**Retirement age**:
The final age included in a WealthProjection; the simulation horizon. Configured by the user; the simulation stops here regardless of scenario.
_Avoid_: end age, horizon
