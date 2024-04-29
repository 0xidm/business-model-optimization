import random
import logging
from rich.logging import RichHandler
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console(file=open('var/sim.log', 'a'))
handler = RichHandler(markup=False, console=console, show_path=True, show_time=True, show_level=True, rich_tracebacks=True)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


class BusinessModel:
    def __init__(self, starting_deposits, growth_pct, starting_pcl, average_user_yield, starting_pol, average_protocol_yield, protocol_fee_pct, buyback_rate_pct, starting_credit_lines, monthly_swap_pressure, expected_apr):
        self.deposits_total = starting_deposits
        self.deposits_growth_pct = growth_pct
        self.sages_total = starting_pcl
        self.sages_average_yield = average_user_yield
        self.treasury_pol_total = starting_pol
        self.treasury_average_yield = average_protocol_yield
        self.treasury_fee_pct = protocol_fee_pct
        self.buyback_rate_pct = buyback_rate_pct
        self.lp_credit_lines = starting_credit_lines
        self.lp_monthly_swap_pressure = monthly_swap_pressure
        self.lp_expected_apr = expected_apr

    def calc_total_deposits(self, month):
        """
        month is the month number
        """
        total_deposits = self.deposits_total
        for i in range(month):
            net_deposits = total_deposits * self.deposits_growth_pct
            total_deposits += net_deposits
        return total_deposits

    def run(self):
        pass

    @property
    def score(self):
        return random.random()
