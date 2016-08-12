from decimal import Decimal
from .abc import WithdrawalStrategy

# This is the standard used in 4% safe withdrawal rates. Take a percentage
# when you first start and then just adjust for inflation every year
class ConstantDollar(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.04')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate
        self.initial_withdrawal = portfolio.value * rate

    def start(self):
        return self.initial_withdrawal

    def next(self):
        return self.initial_withdrawal * self.cumulative_inflation
