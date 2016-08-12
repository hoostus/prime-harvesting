from decimal import Decimal
from .abc import WithdrawalStrategy

# This one is super-simple...just take a constant percentage every
# year. Don't try to index for inflation. So it will vary as the portfolio
# value varies...
class ConstantPercentage(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.04')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate

    def start(self):
        self.portfolio.value * self.rate

    def next(self):
        self.portfolio.value * self.rate
