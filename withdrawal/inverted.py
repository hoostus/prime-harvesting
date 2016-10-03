from decimal import Decimal
from .abc import WithdrawalStrategy
from metrics import pmt
from numpy import pv

class TiltCapital(WithdrawalStrategy):
    """ Based on "A New Framework for Comparing Withdrawl Strategies" (Walton)
    https://www.mendeley.com/viewer/?fileId=37a5a165-6904-e6e1-4418-f5a67c647a49&documentId=8c9d14ed-8c25-343a-9866-0ae13f1b0264
    """
    def __init__(self, portfolio, harvest_strategy, start_age=65, rate=Decimal('.03525'), tilt=Decimal('-.33')):
        """ A positive tilt prefers capital stability
        A negative tilt prefers income stability
        """
        super().__init__(portfolio, harvest_strategy)

        self.tilt = tilt
        self.starting_portfolio_value = portfolio.value
        self.current_age = start_age
        self.rate = rate
        self.final_age = 120
        self.desired_payment = self.portfolio.value * Decimal('.04')

    def _calc(self):
        amount = pmt(self.rate, self.final_age - self.current_age, self.portfolio.value)
        desired_pmt = self.desired_payment * self.cumulative_inflation
        desired_value = pv(float(self.rate), self.final_age - self.current_age, float(-desired_pmt), when='begin')
        desired_value = Decimal(desired_value)
        tilt = (self.portfolio.value / desired_value) ** self.tilt
        return amount * tilt

    def start(self):
        amount = self._calc()
        self.current_age += 1
        return amount

    def next(self):
        amount = self._calc()
        self.current_age += 1
        return amount

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
