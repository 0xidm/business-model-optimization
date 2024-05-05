import os

from savvy import BusinessModel

def main():
    params = {
        "starting_deposits": 1_000_000,
        "growth_pct": 0.09,
        "average_user_yield": 0.15,
        "starting_pol": 0,
        "average_protocol_yield": 0.15,
        "protocol_fee_pct": 0.45,
        "buyback_rate_pct": 0.6,
        "lp_expected_apr": 0.08,
        "monthly_swap_pressure_pct": 1.0,
    }
    business_model = BusinessModel(**params)
    business_model.run()
    business_model.plot(os.path.expanduser('~/Work/business-model-optimization/var/surplus.png'))

if __name__ == "__main__":
    main()
