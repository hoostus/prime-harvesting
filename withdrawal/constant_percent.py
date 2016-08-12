from decimal import Decimal
from .abc import WithdrawalStrategy

# This one is super-simple...just take a constant percentage every
# year. Don't try to index for inflation. So it will vary as the portfolio
# value varies...
class ConstantPercentage(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.05')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate

    def _calc(self):
        return self.portfolio.value * self.rate

    def start(self):
        return self._calc()

    def next(self):
        return self._calc()
