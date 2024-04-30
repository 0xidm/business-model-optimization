import pytest

from savvy import BusinessModel

def test_create(business_model):
    assert business_model.starting_deposits == 1_000_000

def test_calc_total_deposits(business_model):
    assert business_model.calc_total_deposits(month=1) == 1_000_000
    assert business_model.calc_total_deposits(month=2) == 1_100_000
    assert business_model.calc_total_deposits(month=3) == 1_210_000

def test_calc_net_new_deposits(business_model):
    assert business_model.calc_net_new_deposits(month=1) == 0
    assert business_model.calc_net_new_deposits(month=2) == 100_000
    assert business_model.calc_net_new_deposits(month=3) == 110_000

def test_calc_total_sages(business_model):
    assert business_model.calc_total_sages(month=1) == 9_000
    assert business_model.calc_total_sages(month=2) == 18_000
    assert business_model.calc_total_sages(month=3) == 27_900

def test_calc_total_treasury(business_model):
    assert business_model.calc_total_treasury(month=1) == 1_000
    assert business_model.calc_total_treasury(month=2) == pytest.approx(1_867, 50)
    assert business_model.calc_total_treasury(month=3) == pytest.approx(2_948, 50)

def test_calc_net_new_pol(business_model):
    assert business_model.calc_net_new_pol(month=1) == 1_000
    assert business_model.calc_net_new_pol(month=2) == pytest.approx(1_167, 1)
    assert business_model.calc_net_new_pol(month=3) == pytest.approx(1_431, 10)
    assert business_model.calc_net_new_pol(month=4) == pytest.approx(1_724, 20)

def test_calc_buybacks(business_model):
    assert business_model.calc_buybacks(month=1) == 300
    assert business_model.calc_buybacks(month=2) == pytest.approx(350, 6)
    assert business_model.calc_buybacks(month=3) == pytest.approx(429, 10)

def test_calc_cost_of_lp(business_model):
    assert business_model.calc_cost_of_lp(month=1) == 5000
    assert business_model.calc_cost_of_lp(month=2) == 5500
    assert business_model.calc_cost_of_lp(month=3) == 6050

def test_calc_net_zero(business_model):
    assert business_model.calc_net_zero(month=1) == -4_700
    assert business_model.calc_net_zero(month=2) == pytest.approx(-5_150, 10)
    assert business_model.calc_net_zero(month=3) == pytest.approx(-5_621, 10)
    assert business_model.calc_net_zero(month=12) == pytest.approx(-11_516, 10)
    assert business_model.calc_net_zero(month=12) == pytest.approx(-12_618, 10)

def test_calc_cumulative_base_asset_required(business_model):
    assert business_model.calc_cumulative_base_asset_required(month=1) == 500_000
    assert business_model.calc_cumulative_base_asset_required(month=2) == 550_000
    assert business_model.calc_cumulative_base_asset_required(month=3) == 605_000

def test_calc_monthly_swap_pressure(business_model):
    assert business_model.calc_monthly_swap_pressure(month=1) == 500_000
    assert business_model.calc_monthly_swap_pressure(month=2) == 50_000
    assert business_model.calc_monthly_swap_pressure(month=3) == 55_000

def test_calc_new_credit_lines(business_model):
    assert business_model.calc_new_credit_lines(month=1) == 500_000
    assert business_model.calc_new_credit_lines(month=2) == 50_000
    assert business_model.calc_new_credit_lines(month=3) == 55_000

@pytest.fixture
def business_model():
    return BusinessModel(
        starting_deposits=1_000_000,
        growth_pct=0.1,
        average_user_yield=0.12,
        starting_pol=1000,
        average_protocol_yield=0.2,
        protocol_fee_pct=0.1,
        buyback_rate_pct=0.3,
        expected_apr=0.12,
    )
