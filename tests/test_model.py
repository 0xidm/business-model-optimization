import pytest

from savvy import BusinessModel

def test_create(business_model):
    assert business_model.deposits_total == 100

def test_calc_total_deposits(business_model):
    assert business_model.calc_total_deposits(month=0) == 100
    assert business_model.calc_total_deposits(month=1) == 110
    assert business_model.calc_total_deposits(month=2) == 121

@pytest.fixture
def business_model():
    return BusinessModel(
        starting_deposits=100,
        growth_pct=0.1,
        starting_pcl=100,
        average_user_yield=0.1,
        starting_pol=100,
        average_protocol_yield=0.1,
        protocol_fee_pct=0.1,
        buyback_rate_pct=0.1,
        starting_credit_lines=100,
        monthly_swap_pressure=0.1,
        expected_apr=0.1,
    )
