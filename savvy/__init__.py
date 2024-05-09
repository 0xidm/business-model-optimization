import math
import random
import logging
import functools

import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

from rich.logging import RichHandler
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console(file=open('var/sim.log', 'a'))
handler = RichHandler(markup=False, console=console, show_path=True, show_time=True, show_level=True, rich_tracebacks=True)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


class BusinessModel:
    def __init__(self, starting_deposits, growth_pct, average_user_yield, starting_pol, average_protocol_yield, protocol_fee_pct, buyback_rate_pct, lp_expected_apr, monthly_swap_pressure_pct, credit_utilization=0.5, periods_in_year=12, periods_in_simulation=48):

        self.starting_deposits = starting_deposits
        self.growth_pct = growth_pct
        self.average_user_yield = average_user_yield
        self.starting_pol = starting_pol
        self.average_protocol_yield = average_protocol_yield
        self.protocol_fee_pct = protocol_fee_pct
        self.buyback_rate_pct = buyback_rate_pct
        self.lp_expected_apr = lp_expected_apr
        self.monthly_swap_pressure_pct = monthly_swap_pressure_pct
        self.periods_in_year = periods_in_year
        self.credit_utilization = credit_utilization
        self.periods_in_simulation = periods_in_simulation

        self.df = pd.DataFrame()
    
    @property
    def slope(self):
        return self.find_slope_of_surplus()

    @property
    def break_even_month(self):
        return self.find_break_even_month()

    @property
    def final_treasury(self):
        return self.total_treasury(self.periods_in_simulation)
    
    @property
    def final_deposits(self):
        return self.total_deposits(self.periods_in_simulation)
    
    @property
    def final_sages(self):
        return self.total_sages(self.periods_in_simulation)

    @property
    def final_tvl(self):
        return self.tvl(self.periods_in_simulation)

    def run(self):
        """
        Simulate the business model for the given number of periods.
        Calculating self.slope ensures all values are cached so they will be ready for analysis.
        """
        assert self.slope, "slope is not calculated"

    def plot(self, filename="surplus.png"):
        ts = []
        for month in range(1, self.periods_in_simulation+1):
            ts.append([month, self.surplus(month)])
        df = pd.DataFrame(ts, columns=['month', 'surplus'])
        # create a plot and write to png
        df.plot(x='month', y='surplus', kind='line')
        plt.savefig(filename)

    @functools.cache
    def current_lp_apr(self, month):
        _current_tvl = self.total_treasury(self.periods_in_simulation) + self.total_sages(self.periods_in_simulation) + self.total_deposits(self.periods_in_simulation)
        apr_levels = [
            (3.477, 73.17),
            (4.129, 32.44),
            (10.909, 16.24),
            (9.559, 8.00),
            (14.264, 4.03),
            (13.745, 2.02),
            (13.479, 1.00),
            (13.333, 0),
            # (13.333, 0.50),
        ]

        for apr, tvl in apr_levels:
            if _current_tvl >= tvl * 1_000_000:
                return apr

        # return self.lp_expected_apr

    @functools.cache
    def current_growth_pct(self, month):
        _current_tvl = self.t

        if _current_tvl >= 50_000_000:
            _scaling_factor = 0.2
        elif _current_tvl >= 10_000_000:
            _scaling_factor = 0.6
        elif _current_tvl >= 5_000_000:
            _scaling_factor = 0.8
        else:
            _scaling_factor = 1
        return growth_pct_scaled

    @functools.cache
    def find_break_even_month(self):
        """
        Find the month where net zero is reached
        """
        for month in range(3, self.periods_in_simulation+1):
            if self.surplus(month) >= 0:
                return month
        return -1

    @functools.cache
    def find_slope_of_surplus(self):
        ts = []
        for month in range(1, self.periods_in_simulation+1):
            ts.append([month, self.surplus(month)])

        result = stats.linregress(ts)
        return result.slope

    @functools.cache
    def total_deposits(self, month):
        if month <= 1:
            return self.starting_deposits
        else:
            return self.total_deposits(month-1) + self.net_new_deposits(month)

    @functools.cache
    def net_new_deposits(self, month):
        return self.new_deposits(month)

    @functools.cache
    def new_deposits(self, month):
        if month == 1:
            return self.starting_deposits
        else:
            return self.total_deposits(month-1) * self.growth_pct

    @functools.cache
    def total_sages(self, month):
        if month == 1:
            return self.net_new_pcl(1)
        else:
            return self.total_sages(month-1) + self.net_new_pcl(month)
    
    @functools.cache
    def net_new_pcl(self, month):
        return self.customer_yield(month)

    @functools.cache
    def customer_yield(self, month):
        if month == 1:
            _deposits = self.total_deposits(1)
        else:
            _deposits = self.total_deposits(month-1)

        return _deposits * self.average_user_yield * (1-self.protocol_fee_pct) / self.periods_in_year

    @functools.cache
    def total_treasury(self, month):
        if month == 1:
            _treasury = self.starting_pol
        else:
            _treasury = self.total_treasury(month-1)
        return _treasury + self.net_new_pol(month) - self.buybacks(month) + self.surplus(month-1)

    @functools.cache
    def net_new_pol(self, month):
        return self.protocol_fee_from_deposits(month) + self.treasury_yield_on_yield(month) + self.sage_yield_on_yield(month)
    
    @functools.cache
    def protocol_fee_from_deposits(self, month):
        if month == 1:
            _deposits = self.total_deposits(1)
        else:
            _deposits = self.total_deposits(month-1)

        return _deposits * self.average_user_yield * self.protocol_fee_pct / self.periods_in_year
    
    @functools.cache
    def treasury_yield_on_yield(self, month):
        if month == 1:
            return 0
        return self.total_treasury(month-1) * self.average_protocol_yield / self.periods_in_year
    
    @functools.cache
    def sage_yield_on_yield(self, month):
        if month == 1:
            return 0
        else:
            _total_sages = self.total_sages(month-1)
        return _total_sages * self.average_protocol_yield / self.periods_in_year

    @functools.cache
    def buybacks(self, month):
        return self.net_new_pol(month) * self.buyback_rate_pct
    
    @functools.cache
    def new_credit_lines(self, month):
        return self.net_new_deposits(month) * self.credit_utilization

    @functools.cache
    def monthly_swap_pressure(self, month):
        return self.new_credit_lines(month) * self.monthly_swap_pressure_pct

    @functools.cache
    def cumulative_base_asset_required(self, month):
        if month == 1:
            return self.new_base_asset_required(1)
        else:
            return self.cumulative_base_asset_required(month-1) + self.new_base_asset_required(month)

    @functools.cache
    def new_base_asset_required(self, month):
        return self.new_credit_lines(month)

    @functools.cache
    def cost_of_lp(self, month):
        return self.lp_expected_apr * self.cumulative_base_asset_required(month) / self.periods_in_year
    
    @functools.cache
    def tvl(self, month):
        return self.total_treasury(month) + self.total_deposits(month) + self.total_sages(month)

    @functools.cache
    def surplus(self, month):
        """
        AKA net_zero
        """
        if month <= 1:
            return 0
        return self.buybacks(month) - self.cost_of_lp(month)
