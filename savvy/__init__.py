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
    def __init__(self, starting_deposits, growth_pct, average_user_yield, starting_pol, average_protocol_yield, protocol_fee_pct, buyback_rate_pct, lp_expected_apr, monthly_swap_pressure_pct):

        self.starting_deposits = starting_deposits # parameters['starting_deposits']
        self.growth_pct = growth_pct # parameters['growth_pct']
        self.average_user_yield = average_user_yield # parameters['average_user_yield']
        self.starting_pol = starting_pol # parameters['starting_pol']
        self.average_protocol_yield = average_protocol_yield # parameters['average_protocol_yield']
        self.protocol_fee_pct = protocol_fee_pct # parameters['protocol_fee_pct']
        self.buyback_rate_pct = buyback_rate_pct # parameters['buyback_rate_pct']
        self.lp_expected_apr = lp_expected_apr # parameters['expected_apr']
        self.monthly_swap_pressure_pct = monthly_swap_pressure_pct # parameters['monthly_swap_pressure']

        # static values
        self.periods_in_year = 12
        self.starting_credit_lines = 500_000
        self.credit_utilization = 0.5

        self.df = pd.DataFrame()
    
    def run(self):
        ts = []
        for month in range(1, 72+1):
            ts.append([month, self.surplus(month)])

        result = stats.linregress(ts)
        self._slope = result.slope
        self._break_even_month = self.find_break_even_month()

    def plot(self, filename="surplus.png"):
        ts = []
        for month in range(1, 36+1):
            ts.append([month, self.surplus(month)])
        df = pd.DataFrame(ts, columns=['month', 'surplus'])
        # create a plot and write to png
        df.plot(x='month', y='surplus', kind='line')
        plt.savefig(filename)

    @property
    def slope(self):
        return self._slope

    @property
    def break_even_month(self):
        return self._break_even_month

    @functools.cache
    def find_break_even_month(self):
        """
        Find the month where net zero is reached
        """
        for month in range(3, 36+1):
            if self.surplus(month) >= 0:
                return month
        return -1

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
            deposits = self.total_deposits(1)
        else:
            deposits = self.total_deposits(month-1)

        return deposits * self.average_user_yield * (1-self.protocol_fee_pct) / self.periods_in_year

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
            deposits = self.total_deposits(1)
        else:
            deposits = self.total_deposits(month-1)

        return deposits * self.average_user_yield * self.protocol_fee_pct / self.periods_in_year
    
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
    def surplus(self, month):
        """
        AKA net_zero
        """
        if month <= 1:
            return 0
        return self.buybacks(month) - self.cost_of_lp(month)

