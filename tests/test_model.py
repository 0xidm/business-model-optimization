import pytest

from savvy import BusinessModel

def test_create(business_model):
    assert business_model.deposits_total == 1_000_000

def test_calc_total_deposits(business_model):
    assert business_model.calc_total_deposits(month=0) == 1_000_000
    assert business_model.calc_total_deposits(month=1) == 1_100_000
    assert business_model.calc_total_deposits(month=2) == 1_210_000

def test_calc_total_sages(business_model):
    assert business_model.calc_total_sages(month=0) == 6_000
    assert business_model.calc_total_sages(month=1) == 12_000
    assert business_model.calc_total_sages(month=2) == 18_600

@pytest.fixture
def business_model():
    return BusinessModel(
        starting_deposits=1_000_000,
        growth_pct=0.1,
        starting_pcl=6_000,
        average_user_yield=0.12,
        starting_pol=4_000,
        average_protocol_yield=0.2,
        protocol_fee_pct=0.4,
        buyback_rate_pct=0.3,
        starting_credit_lines=500_000,
        monthly_swap_pressure=1.0,
        expected_apr=0.12,
    )
