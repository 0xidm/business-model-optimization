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
    def __init__(self, starting_deposits, growth_pct, average_user_yield, starting_pol, average_protocol_yield, protocol_fee_pct, buyback_rate_pct, expected_apr):
        self.starting_deposits = starting_deposits
        self.growth_pct = growth_pct
        self.average_user_yield = average_user_yield
        self.starting_pol = starting_pol
        self.average_protocol_yield = average_protocol_yield
        self.protocol_fee_pct = protocol_fee_pct
        self.buyback_rate_pct = buyback_rate_pct
        self.lp_expected_apr = expected_apr

        # static values
        self.periods_in_year = 12
        self.starting_credit_lines = 500_000
        self.credit_utilization = 0.5
        self.monthly_swap_pressure = 1.0

    def calc_total_deposits(self, month):
        """
        month is the month number
        """
        total_deposits = self.starting_deposits
        for i in range(month):
            net_deposits = total_deposits * self.growth_pct
            total_deposits += net_deposits
        return total_deposits

    def calc_net_new_deposits(self, month):
        """
        month is the month number
        """
        if month <= 0:
            return 0

        total_deposits = self.starting_deposits
        for i in range(month):
            net_deposits = total_deposits * self.growth_pct
            total_deposits += net_deposits
        return net_deposits

    def calc_total_sages(self, month):
        """
        month is the month number
        """
        total_sages = 0
        for i in range(month):
            deposits_last_month = self.calc_total_deposits(month-1)
            customer_yield = deposits_last_month * self.average_user_yield * (1-self.protocol_fee_pct) / self.periods_in_year
            total_sages += customer_yield
        return total_sages

    def calc_net_new_pol(self, month):
        """
        month is the month number
        """
        if month <= 0:
            return 0

        total_treasury_pol = self.starting_pol
        total_treasury_previous_month = total_treasury_pol

        for i in range(month):
            protocol_fee_from_deposits = self.calc_total_deposits(month-1) * self.average_user_yield * self.protocol_fee_pct / self.periods_in_year
            treasury_yield_on_yield = total_treasury_previous_month * self.average_protocol_yield / self.periods_in_year
            sage_yield_on_yield = self.calc_total_sages(month-1) * self.average_protocol_yield / self.periods_in_year
            net_new = protocol_fee_from_deposits + treasury_yield_on_yield + sage_yield_on_yield
            total_treasury_pol += net_new
            total_treasury_previous_month = total_treasury_pol

        return net_new

    def calc_total_treasury(self, month):
        """
        month is the month number
        """
        if month <= 0:
            return 0

        total_treasury_pol = self.starting_pol
        for i in range(month):
            total_treasury_pol += self.calc_net_new_pol(month)

        return total_treasury_pol

    def calc_buybacks(self, month):
        """
        month is the month number
        """
        buybacks = 0
        for i in range(month):
            buybacks_this_month = self.calc_net_new_pol(month) * self.buyback_rate_pct
            buybacks += buybacks_this_month
        return buybacks

    def calc_lp_rewards(self, month):
        """
        month is the month number
        """
        total_credit_lines = self.starting_credit_lines
        cumulative_credit_lines = 0

        for i in range(month):
            net_new_deposits = self.calc_net_new_deposits(month)
            new_credit_lines = net_new_deposits * self.credit_utilization
            monthly_swap_pressure = net_new_deposits * self.monthly_swap_pressure
            cumulative_credit_lines += new_credit_lines

        return new_credit_lines * self.lp_expected_apr / self.periods_in_year

    def calc_net_zero(self, month):
        """
        month is the month number
        """
        return self.calc_buybacks(month) - self.calc_lp_rewards(month)

    def run(self):
        self._net_zero = self.calc_net_zero(12)        

    @property
    def score(self):
        return self._net_zero
