import pytest
from pytest import approx

from savvy import BusinessModel

def test_create(business_model):
    assert business_model.starting_deposits == 1_000_000

def test_net_new_deposits(business_model):
    assert business_model.net_new_deposits(month=1) == 1_000_000
    assert business_model.net_new_deposits(month=2) == 30_000
    assert business_model.net_new_deposits(month=3) == 30_900

def test_net_new_pcl(business_model):
    assert business_model.net_new_pcl(month=1) == 9_000
    assert business_model.net_new_pcl(month=2) == 9_000
    assert business_model.net_new_pcl(month=3) == 9_270

def test_protocol_fee_from_deposits(business_model):
    assert business_model.protocol_fee_from_deposits(month=1) == 1_000
    assert business_model.protocol_fee_from_deposits(month=2) == 1_000
    assert business_model.protocol_fee_from_deposits(month=3) == 1_030

def test_buybacks(business_model):
    assert business_model.buybacks(month=1) == 400
    assert business_model.buybacks(month=2) == approx(7_131, abs=1)
    assert business_model.buybacks(month=3) == approx(7_240, abs=1)
    assert business_model.buybacks(month=4) == approx(7_396, abs=1)

def test_sage_yield_on_yield(business_model):
    assert business_model.sage_yield_on_yield(month=1) == 0
    assert business_model.sage_yield_on_yield(month=2) == 150
    assert business_model.sage_yield_on_yield(month=3) == 300

def test_treasury_yield_on_yield(business_model):
    assert business_model.treasury_yield_on_yield(month=1) == 0
    assert business_model.treasury_yield_on_yield(month=2) == approx(16_677, abs=1)
    assert business_model.treasury_yield_on_yield(month=3) == approx(16_769, abs=1)

def test_net_new_pol(business_model):
    assert business_model.net_new_pol(month=1) == 1_000
    assert business_model.net_new_pol(month=2) == approx(17_827, abs=1)
    assert business_model.net_new_pol(month=3) == approx(18_099, abs=1)
    assert business_model.net_new_pol(month=4) == approx(18_489, abs=1)

def test_new_credit_lines(business_model):
    assert business_model.new_credit_lines(month=1) == 500_000
    assert business_model.new_credit_lines(month=2) == 15_000
    assert business_model.new_credit_lines(month=3) == 15_450
    assert business_model.new_credit_lines(month=4) == approx(15_914, abs=1)

def test_monthly_swap_pressure(business_model):
    assert business_model.monthly_swap_pressure(month=1) == 500_000
    assert business_model.monthly_swap_pressure(month=2) == 15_000
    assert business_model.monthly_swap_pressure(month=3) == 15_450

def test_cumulative_base_asset_required(business_model):
    assert business_model.cumulative_base_asset_required(month=1) == 500_000
    assert business_model.cumulative_base_asset_required(month=2) == 515_000
    assert business_model.cumulative_base_asset_required(month=3) == 530_450

def test_new_base_asset_required(business_model):
    assert business_model.new_base_asset_required(month=1) == 500_000
    assert business_model.new_base_asset_required(month=2) == 15_000
    assert business_model.new_base_asset_required(month=3) == 15_450

def test_cost_of_lp(business_model):
    assert business_model.cost_of_lp(month=1) == approx(-5_155, abs=1)
    assert business_model.cost_of_lp(month=2) == approx(1_409, abs=1)
    assert business_model.cost_of_lp(month=3) == approx(1_346, abs=1)

def test_total_deposits(business_model):
    assert business_model.total_deposits(month=1) == 1_000_000
    assert business_model.total_deposits(month=2) == 1_030_000
    assert business_model.total_deposits(month=3) == 1_060_900

def test_total_sages(business_model):
    assert business_model.total_sages(month=1) == 9_000
    assert business_model.total_sages(month=2) == 18_000
    assert business_model.total_sages(month=3) == 27_270

def test_total_treasury(business_model):
    assert business_model.total_treasury(month=1) == 1_000_600
    assert business_model.total_treasury(month=2) == approx(1_006_141, abs=1)
    assert business_model.total_treasury(month=3) == approx(1_018_409, abs=1)

def test_surplus(business_model):
    assert business_model.surplus(month=1) == approx(-5_155, abs=1)
    assert business_model.surplus(month=2) == approx(1_409, abs=1)
    assert business_model.surplus(month=3) == approx(1_346, abs=1)
    assert business_model.surplus(month=11) == approx(1_325, abs=1)
    assert business_model.surplus(month=12) == approx(1_302, abs=1)

def test_tvl(business_model):
    assert business_model.final_deposits == approx(3762180, abs=1)
    assert business_model.final_sages == approx(902446, abs=1)
    assert business_model.final_treasury == approx(1837206, abs=1)
    assert business_model.final_tvl == approx(6761670, abs=1)

def test_growth_pct(business_model):
    assert business_model.starting_growth_pct == 0.03
    assert business_model.current_growth_pct(month=36) == 0.03

def test_plot(business_model):
    business_model.run()
    business_model.plot('var/surplus.png')

def test_cost_of_lp(business_model):
    assert business_model.current_lp_apr(month=1) == 0.13479
    assert business_model.cost_of_lp(month=1) == approx(5555, abs=1)
    assert business_model.cost_of_lp(month=2) == approx(5722, abs=1)
    assert business_model.cost_of_lp(month=3) == approx(5894, abs=1)

def test_finals(business_model):
    assert business_model.final_treasury == approx(1_837_207, abs=1e4)
    assert business_model.final_deposits == approx(4_011_895, abs=1e6)
    assert business_model.final_sages == approx(912_569, abs=1e5)
    assert business_model.final_tvl == approx(6_761_670, abs=1e6)

def test_finals_2(business_model_2):
    assert business_model_2.final_treasury == approx(3_133_069, abs=1e3)
    assert business_model_2.final_deposits == approx(104_146_265, abs=1e4)
    assert business_model_2.final_sages == approx(8_174_117, abs=1e4)
    assert business_model_2.final_tvl == approx(114_644_998, abs=1e6)

@pytest.fixture
def business_model():
    return BusinessModel(**{
        "starting_deposits": 1_000_000,
        "starting_growth_pct": 0.03,
        "average_user_yield": 0.12,
        "starting_pol": 1_000_000,
        "average_protocol_yield": 0.2,
        "protocol_fee_pct": 0.1,
        "buyback_rate_pct": 0.4,
        "monthly_swap_pressure_pct": 1.0,
    })

@pytest.fixture
def business_model_2():
    return BusinessModel(**{
        "starting_deposits": 1_000_000,
        "starting_growth_pct": 0.2,
        "average_user_yield": 0.08,
        "starting_pol": 1_000_000,
        "average_protocol_yield": 0.13,
        "protocol_fee_pct": 0.30,
        "buyback_rate_pct": 1.0,
        "monthly_swap_pressure_pct": 0.8,
        "credit_utilization": 0.4,
    })
