# From Bob Clyatt, author of "Work Less, Live More"
# The description is taken from McClung's Living Off Your Money

# This is a constant percentage (5% of current portfolio) but with
# a floor to smooth out income drops. This makes it very similar to
# Vanguard's strategy...except that one also smooths out the increases

from decimal import Decimal
from .abc import WithdrawalStrategy

class Clyatt(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=.05, floor=.95):
        super().__init__(portfolio, harvest_strategy)

        self.rate = Decimal(rate)
        self.floor = Decimal(floor)

    def start(self):
        amount = self.portfolio.value * self.rate
        self.minimum = self.floor * amount
        return amount

    def next(self):
        amount = self.portfolio.value * self.rate
        amount = max(amount, self.minimum)
        self.minimum = self.floor * amount
        return amount
