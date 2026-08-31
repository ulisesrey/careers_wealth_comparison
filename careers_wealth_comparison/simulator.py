from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    cash_flows: dict[int, float]


@dataclass
class Config:
    current_age: int
    retirement_age: int
    cost_of_living: float
    investment_return_rate: float
    starting_net_worth: float


@dataclass
class WealthProjection:
    name: str
    net_worth_by_age: dict[int, float]


def simulate(scenarios: list[Scenario], config: Config) -> list[WealthProjection]:
    projections = []
    for scenario in scenarios:
        net_worth_by_age: dict[int, float] = {}
        net_worth = config.starting_net_worth
        for age in range(config.current_age, config.retirement_age + 1):
            cash_flow = scenario.cash_flows.get(age, 0.0)
            net_worth = net_worth * (1 + config.investment_return_rate) + cash_flow - config.cost_of_living
            net_worth_by_age[age] = net_worth
        projections.append(WealthProjection(name=scenario.name, net_worth_by_age=net_worth_by_age))
    return projections


def find_break_even_age(
    projections: list[WealthProjection], baseline_name: str
) -> dict[str, int | None]:
    baseline = next((p for p in projections if p.name == baseline_name), None)
    if baseline is None:
        raise ValueError(f"Baseline scenario '{baseline_name}' not found in projections")

    result: dict[str, int | None] = {}
    for proj in projections:
        if proj.name == baseline_name:
            continue
        crossover = None
        for age in sorted(proj.net_worth_by_age):
            if proj.net_worth_by_age[age] > baseline.net_worth_by_age[age]:
                crossover = age
                break
        result[proj.name] = crossover
    return result
