import json
from pathlib import Path

from careers_wealth_comparison.simulator import Scenario


def load_scenarios(path: Path) -> list[Scenario]:
    with open(path) as f:
        data = json.load(f)
    return [
        Scenario(
            name=item["name"],
            cash_flows={int(k): float(v) for k, v in item["cash_flows"].items()},
        )
        for item in data
    ]
