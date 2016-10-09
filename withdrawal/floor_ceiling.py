from decimal import Decimal
from .abc import WithdrawalStrategy

# Bengen's Floor-to-Ceiling, as described in McClung's Living Off Your Money

class FloorCeiling(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=.05, floor=.9, ceiling=1.25):
        super().__init__(portfolio, harvest_strategy)

        self.floor = Decimal(floor)
        self.ceiling = Decimal(ceiling)
        self.rate = Decimal(rate)

    def start(self):
        amount = self.rate * self.portfolio.value
        self.initial_amount = amount
        return amount

    def next(self):
        amount = self.rate * self.portfolio.value

        initial_amount_inflation_adjusted = self.initial_amount * self.cumulative_inflation

        floor = initial_amount_inflation_adjusted * self.floor
        ceiling = initial_amount_inflation_adjusted * self.ceiling

        amount = max(amount, floor)
        amount = min(amount, ceiling)

        return amount
