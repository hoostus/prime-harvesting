from decimal import Decimal
from .abc import WithdrawalStrategy

class InvertedWithdrawals(WithdrawalStrategy):
    """ Based on "Inverted Withdrawal Rates and the Sequence of Returns Bonus" (Walton, 2016)
    published in Advistor Perspectives[1]

    [1]: https://www.mendeley.com/viewer/?fileId=72897973-b53f-d335-4d49-e46159445e8f&documentId=8c71b8a2-8422-3612-8b24-ecac0c7e2019
    """
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.04'), tilt=Decimal('.01')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate
        self.tilt = tilt
        self.starting_portfolio_value = portfolio.value

    def start(self):
        # we start out with the default withdrawal rate.
        # n.b. that this is the ONLY time it is used. Every other
        # time we will use a tilt because we will either be above or
        # below this value
        return self.portfolio.value * self.rate

    def next(self):
        # Figure out which tilt we used based on the current (inflation-adjusted)
        # portfolio value
        if (self.portfolio.value / self.cumulative_inflation) < self.starting_portfolio_value:
            withdrawal = self.portfolio.value * (self.rate - self.tilt)
        else:
            withdrawal = self.portfolio.value * (self.rate + self.tilt)

        return withdrawal
