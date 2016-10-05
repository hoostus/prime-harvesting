# From https://advisors.vanguard.com/iwe/pdf/ISGELR.pdf?oeaut=JcoSRRSTMv
# "From Assets to Income" (2016)

from decimal import Decimal
from .abc import WithdrawalStrategy

class Vanguard(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=.04, ceiling=.05, floor=0.025):
        super().__init__(portfolio, harvest_strategy)

        self.rate = Decimal(rate)
        self.ceiling = Decimal(ceiling)
        self.floor = Decimal(floor)

    def start(self):
        amount = self.portfolio.value * self.rate
        self.last_year = amount
        return amount

    def next(self):
        amount = self.portfolio.value * self.rate

        ceiling = self.last_year * (1 + self.current_inflation) * (1 + self.ceiling)
        floor = self.last_year * (1 + self.current_inflation) * (1 - self.floor)

        amount = min(amount, ceiling)
        amount = max(amount, floor)
        self.last_year = amount
        return amount
