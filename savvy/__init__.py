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
        if month == 1:
            return self.starting_deposits

        total_deposits = self.starting_deposits
        for i in range(month-1):
            net_deposits = total_deposits * self.growth_pct
            total_deposits += net_deposits
        return total_deposits

    def calc_net_new_deposits(self, month):
        """
        month is the month number
        """
        if month <= 1:
            return 0

        total_deposits = self.starting_deposits
        for i in range(month-1):
            net_deposits = total_deposits * self.growth_pct
            total_deposits += net_deposits
        return net_deposits

    def calc_total_sages(self, month):
        """
        month is the month number
        """
        if month <= 0:
            return 0
        
        total_sages = 0
        for i in range(1, month+1):
            if i == 1:
                deposits = self.calc_total_deposits(1)
            else:
                deposits = self.calc_total_deposits(i-1)

            customer_yield = deposits * self.average_user_yield * (1-self.protocol_fee_pct) / self.periods_in_year
            total_sages += customer_yield
        return total_sages

    def calc_net_new_pol(self, month, cumulative=False):
        """
        month is the month number
        """
        if month <= 0:
            return 0

        total_treasury_pol = self.starting_pol
        total_treasury_previous_month = total_treasury_pol

        if month == 1:
            return total_treasury_pol

        for i in range(1, month+1):
            protocol_fee_from_deposits = self.calc_total_deposits(i-1) * self.average_user_yield * self.protocol_fee_pct / self.periods_in_year

            treasury_yield_on_yield = total_treasury_previous_month * self.average_protocol_yield / self.periods_in_year

            sage_yield_on_yield = self.calc_total_sages(i-1) * self.average_protocol_yield / self.periods_in_year

            net_new = protocol_fee_from_deposits + treasury_yield_on_yield + sage_yield_on_yield

            total_treasury_pol += net_new
            total_treasury_previous_month = total_treasury_pol

        if cumulative:
            return total_treasury_pol
        else:
            return net_new

    def calc_total_treasury(self, month):
        """
        month is the month number
        """
        if month == 1:
            return self.starting_pol

        buybacks = self.calc_buybacks(month-1)
        last_month = self.calc_total_treasury(month-1)
        net_new_pol = self.calc_net_new_pol(month)
        return last_month + net_new_pol - buybacks

    def calc_buybacks(self, month):
        """
        month is the month number
        """
        net_new_pol = self.calc_net_new_pol(month)
        return net_new_pol * self.buyback_rate_pct

    def calc_cost_of_lp(self, month):
        """
        month is the month number
        """
        cumulative_base_asset_required = self.starting_credit_lines
        for i in range(1, month+1):
            net_new_deposits = self.calc_net_new_deposits(i)
            new_credit_lines = net_new_deposits * self.credit_utilization
            cumulative_base_asset_required += new_credit_lines


        return total_treasury * self.lp_expected_apr / self.periods_in_year

    def calc_monthly_swap_pressure(self, month):
        """
        month is the month number
        """
        if month == 1:
            return self.starting_credit_lines
        return self.calc_new_credit_lines(month) * self.monthly_swap_pressure

    def calc_new_credit_lines(self, month):
        if month == 1:
            return self.starting_credit_lines
        return self.calc_net_new_deposits(month) * self.credit_utilization

    def calc_cumulative_base_asset_required(self, month):
        """
        month is the month number
        """
        if month == 1:
            return self.starting_credit_lines

        cumulative_previous = self.calc_cumulative_base_asset_required(month-1)
        new_base_asset_required = self.calc_monthly_swap_pressure(month)
        return cumulative_previous + new_base_asset_required

    def calc_cost_of_lp(self, month):
        """
        month is the month number
        """
        return self.calc_cumulative_base_asset_required(month) * self.lp_expected_apr / self.periods_in_year

    def calc_net_zero(self, month):
        """
        month is the month number
        """
        return self.calc_buybacks(month) - self.calc_cost_of_lp(month)

    def run(self):
        self._net_zero = self.calc_net_zero(12)

    @property
    def net_zero(self):
        return self._net_zero
