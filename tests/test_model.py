import pytest

from savvy import BusinessModel

def test_create(business_model):
    assert business_model.starting_deposits == 1_000_000

def test_total_deposits(business_model):
    assert business_model.total_deposits(month=1) == 1_000_000
    assert business_model.total_deposits(month=2) == 1_030_000
    assert business_model.total_deposits(month=3) == 1_060_900

def test_net_new_deposits(business_model):
    assert business_model.net_new_deposits(month=1) == 1_000_000
    assert business_model.net_new_deposits(month=2) == 30_000
    assert business_model.net_new_deposits(month=3) == 30_900

def test_total_sages(business_model):
    assert business_model.total_sages(month=1) == 9_000
    assert business_model.total_sages(month=2) == 18_000
    assert business_model.total_sages(month=3) == 27_270

def test_net_new_pcl(business_model):
    assert business_model.net_new_pcl(month=1) == 9_000
    assert business_model.net_new_pcl(month=2) == 9_000
    assert business_model.net_new_pcl(month=3) == 9_270

def test_total_treasury(business_model):
    assert business_model.total_treasury(month=1) == 1_000_600
    assert business_model.total_treasury(month=2) == pytest.approx(1_005_863, 1)
    assert business_model.total_treasury(month=3) == pytest.approx(1_017_842, 1)

def test_net_new_pol(business_model):
    assert business_model.net_new_pol(month=1) == 1_000
    assert business_model.net_new_pol(month=2) == pytest.approx(17_827, 1)
    assert business_model.net_new_pol(month=3) == pytest.approx(18_094, 1)
    assert business_model.net_new_pol(month=4) == pytest.approx(18_479, 1)

def test_protocol_fee_from_deposits(business_model):
    assert business_model.protocol_fee_from_deposits(month=1) == 1_000
    assert business_model.protocol_fee_from_deposits(month=2) == 1_000
    assert business_model.protocol_fee_from_deposits(month=3) == 1_030

def test_treasury_yield_on_yield(business_model):
    assert business_model.treasury_yield_on_yield(month=1) == 0
    assert business_model.treasury_yield_on_yield(month=2) == pytest.approx(16_677, 1)
    assert business_model.treasury_yield_on_yield(month=3) == pytest.approx(16_764, 1)

def test_sage_yield_on_yield(business_model):
    assert business_model.sage_yield_on_yield(month=1) == 0
    assert business_model.sage_yield_on_yield(month=2) == 150
    assert business_model.sage_yield_on_yield(month=3) == 300

def test_buybacks(business_model):
    assert business_model.buybacks(month=1) == 400
    assert business_model.buybacks(month=2) == pytest.approx(7_131, 1)
    assert business_model.buybacks(month=3) == pytest.approx(7_238, 1)

def test_new_credit_lines(business_model):
    assert business_model.new_credit_lines(month=1) == 500_000
    assert business_model.new_credit_lines(month=2) == 15_000
    assert business_model.new_credit_lines(month=3) == 15_450

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
    assert business_model.cost_of_lp(month=1) == pytest.approx(5_833, 1)
    assert business_model.cost_of_lp(month=2) == pytest.approx(6_008, 1)
    assert business_model.cost_of_lp(month=3) == pytest.approx(6_189, 1)

def test_surplus(business_model):
    assert business_model.surplus(month=1) == pytest.approx(-5_433, 1)
    assert business_model.surplus(month=2) == pytest.approx(1_122, 1)
    assert business_model.surplus(month=3) == pytest.approx(1_049, 10)
    assert business_model.surplus(month=11) == pytest.approx(733, 10)
    assert business_model.surplus(month=12) == pytest.approx(683, 10)

def test_plot(business_model):
    business_model.run()
    business_model.plot('var/surplus.png')

@pytest.fixture
def business_model():
    return BusinessModel(**{
        "starting_deposits": 1_000_000,
        "growth_pct": 0.03,
        "average_user_yield": 0.12,
        "starting_pol": 1_000_000,
        "average_protocol_yield": 0.2,
        "protocol_fee_pct": 0.1,
        "buyback_rate_pct": 0.4,
        "lp_expected_apr": 0.14,
        "monthly_swap_pressure_pct": 1.0,
    })
