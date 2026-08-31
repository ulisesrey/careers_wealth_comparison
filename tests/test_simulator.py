import pytest

from careers_wealth_comparison.simulator import Config, Scenario, find_break_even_age, simulate


def make_config(**overrides):
    defaults = dict(
        current_age=30,
        retirement_age=30,
        cost_of_living=0.0,
        investment_return_rate=0.0,
        starting_net_worth=0.0,
    )
    return Config(**{**defaults, **overrides})


class TestSimulate:
    def test_single_year_net_worth_formula(self):
        scenario = Scenario(name="DS", cash_flows={30: 100_000})
        config = make_config(cost_of_living=50_000, investment_return_rate=0.10)
        [proj] = simulate([scenario], config)
        # 0.0 * 1.10 + 100_000 - 50_000
        assert proj.net_worth_by_age[30] == pytest.approx(50_000.0)

    def test_starting_net_worth_compounds_in_first_year(self):
        scenario = Scenario(name="DS", cash_flows={})
        config = make_config(investment_return_rate=0.10, starting_net_worth=100_000.0)
        [proj] = simulate([scenario], config)
        # 100_000 * 1.10 + 0 - 0
        assert proj.net_worth_by_age[30] == pytest.approx(110_000.0)

    def test_multi_year_compounding(self):
        scenario = Scenario(name="DS", cash_flows={30: 100_000, 31: 100_000})
        config = make_config(retirement_age=31, cost_of_living=50_000, investment_return_rate=0.10)
        [proj] = simulate([scenario], config)
        assert proj.net_worth_by_age[30] == pytest.approx(50_000.0)
        # 50_000 * 1.10 + 100_000 - 50_000
        assert proj.net_worth_by_age[31] == pytest.approx(105_000.0)

    def test_negative_cash_flow_tuition_year(self):
        scenario = Scenario(name="Doctor", cash_flows={30: -60_000})
        config = make_config(cost_of_living=50_000)
        [proj] = simulate([scenario], config)
        # 0.0 * 1.0 + (-60_000) - 50_000
        assert proj.net_worth_by_age[30] == pytest.approx(-110_000.0)

    def test_negative_net_worth_compounds_symmetrically(self):
        # If net worth were floored at 0, age-31 would be -50_000, not -110_000.
        scenario = Scenario(name="Doctor", cash_flows={30: -100_000})
        config = make_config(retirement_age=31, investment_return_rate=0.10)
        [proj] = simulate([scenario], config)
        assert proj.net_worth_by_age[30] == pytest.approx(-100_000.0)
        # (-100_000) * 1.10 + 0 - 0
        assert proj.net_worth_by_age[31] == pytest.approx(-110_000.0)

    def test_missing_cash_flow_age_defaults_to_zero(self):
        scenario = Scenario(name="DS", cash_flows={})
        config = make_config(cost_of_living=50_000)
        [proj] = simulate([scenario], config)
        # 0.0 * 1.0 + 0 - 50_000
        assert proj.net_worth_by_age[30] == pytest.approx(-50_000.0)

    def test_projection_name_matches_scenario_name(self):
        scenario = Scenario(name="DS", cash_flows={})
        [proj] = simulate([scenario], make_config())
        assert proj.name == "DS"

    def test_multiple_scenarios_returned_in_order(self):
        ds = Scenario(name="DS", cash_flows={})
        doctor = Scenario(name="Doctor", cash_flows={})
        projections = simulate([ds, doctor], make_config())
        assert [p.name for p in projections] == ["DS", "Doctor"]

    def test_retirement_age_is_inclusive(self):
        scenario = Scenario(name="DS", cash_flows={30: 10_000, 31: 10_000})
        config = make_config(retirement_age=31)
        [proj] = simulate([scenario], config)
        assert 31 in proj.net_worth_by_age

    def test_no_ages_beyond_retirement(self):
        scenario = Scenario(name="DS", cash_flows={30: 10_000, 31: 10_000, 32: 10_000})
        config = make_config(retirement_age=31)
        [proj] = simulate([scenario], config)
        assert 32 not in proj.net_worth_by_age


class TestFindBreakEvenAge:
    def test_break_even_age_detected(self):
        ds = Scenario(name="DS", cash_flows={30: 50_000, 31: 50_000})
        doctor = Scenario(name="Doctor", cash_flows={30: -100_000, 31: 500_000})
        config = make_config(retirement_age=31)
        projections = simulate([ds, doctor], config)
        # DS:     age30=50_000,  age31=100_000
        # Doctor: age30=-100_000, age31=400_000  → Doctor > DS at 31
        result = find_break_even_age(projections, baseline_name="DS")
        assert result["Doctor"] == 31

    def test_break_even_age_is_none_when_no_crossover(self):
        ds = Scenario(name="DS", cash_flows={30: 100_000, 31: 100_000})
        doctor = Scenario(name="Doctor", cash_flows={30: 50_000, 31: 50_000})
        config = make_config(retirement_age=31)
        projections = simulate([ds, doctor], config)
        result = find_break_even_age(projections, baseline_name="DS")
        assert result["Doctor"] is None

    def test_break_even_returns_first_crossing_age(self):
        # Doctor overtakes at 31, not 32
        ds = Scenario(name="DS", cash_flows={30: 50_000, 31: 50_000, 32: 50_000})
        doctor = Scenario(name="Doctor", cash_flows={30: -100_000, 31: 500_000, 32: 500_000})
        config = make_config(retirement_age=32)
        projections = simulate([ds, doctor], config)
        result = find_break_even_age(projections, baseline_name="DS")
        assert result["Doctor"] == 31

    def test_baseline_not_included_in_result(self):
        ds = Scenario(name="DS", cash_flows={})
        doctor = Scenario(name="Doctor", cash_flows={})
        projections = simulate([ds, doctor], make_config())
        result = find_break_even_age(projections, baseline_name="DS")
        assert "DS" not in result

    def test_missing_baseline_raises(self):
        ds = Scenario(name="DS", cash_flows={})
        [proj] = simulate([ds], make_config())
        with pytest.raises(ValueError):
            find_break_even_age([proj], baseline_name="Doctor")
