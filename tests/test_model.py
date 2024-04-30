import pytest

from savvy import BusinessModel

def test_create(business_model):
    assert business_model.deposits_total == 1_000_000

def test_calc_total_deposits(business_model):
    assert business_model.calc_total_deposits(month=0) == 1_000_000
    assert business_model.calc_total_deposits(month=1) == 1_100_000
    assert business_model.calc_total_deposits(month=2) == 1_210_000
    assert business_model.calc_total_deposits(month=3) == 1_331_000

def test_calc_net_new_deposits(business_model):
    assert business_model.calc_net_new_deposits(month=0) == 0
    assert business_model.calc_net_new_deposits(month=1) == 100_000
    assert business_model.calc_net_new_deposits(month=2) == 110_000
    assert business_model.calc_net_new_deposits(month=3) == 121_000

def test_calc_total_sages(business_model):
    assert business_model.calc_total_sages(month=1) == 6_000
    assert business_model.calc_total_sages(month=2) == 13_200
    assert business_model.calc_total_sages(month=3) == 21_780

def test_calc_total_treasury(business_model):
    assert business_model.calc_total_treasury(month=1) == 8_066.666666666666
    assert business_model.calc_total_treasury(month=2) == 13_285.555555555555
    assert business_model.calc_total_treasury(month=3) == 19_896.93888888889

def test_calc_net_new_pol(business_model):
    assert business_model.calc_net_new_pol(month=1) == 4_066.6666666666665
    assert business_model.calc_net_new_pol(month=2) == 4_642.777777777777
    assert business_model.calc_net_new_pol(month=3) == 5_298.97962962963

def test_calc_buybacks(business_model):
    assert business_model.calc_buybacks(month=1) == 1220.0
    assert business_model.calc_buybacks(month=2) == 2785.6666666666665
    assert business_model.calc_buybacks(month=3) == 4769.081666666667

def test_calc_lp_rewards(business_model):
    assert business_model.calc_lp_rewards(month=1) == 500
    assert business_model.calc_lp_rewards(month=2) == 1100.0
    assert business_model.calc_lp_rewards(month=3) == 1815.0

def test_calc_net_zero(business_model):
    assert business_model.calc_net_zero(month=1) == 0
    assert business_model.calc_net_zero(month=2) == 0
    assert business_model.calc_net_zero(month=3) == 0

@pytest.fixture
def business_model():
    return BusinessModel(
        starting_deposits=1_000_000,
        growth_pct=0.1,
        average_user_yield=0.12,
        starting_pol=4_000,
        average_protocol_yield=0.2,
        protocol_fee_pct=0.4,
        buyback_rate_pct=0.3,
        expected_apr=0.12,
    )
