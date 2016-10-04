# From Stout & Mitchell (2006), "Dynamic Retirement Withdrawal Planning"

from decimal import Decimal
from .abc import WithdrawalStrategy
from metrics import pmt
import mortality
import numpy

class Model3(WithdrawalStrategy):
    """ This is a PMT-based method with a set of controls.
    up_threshold: how far your portfolio needs to differ from the "optimal amount" before you
        adjust to a higher withdrawal rate.

        'In isolation, the upward threshold has the greater impact on the probability of ruin,
        suggesting that upward thresholds would be the first control to install in reducing
        the probability of ruin. Upward thresholds of deviation above 1.4, however,
        yield only modest reductions in the probability of ruin as higher upward
        thresholds decrease the probability of ruin at a decreasing rate.'

        Note: an upward threshold of 1.4 means the portfolio needs to increase by
        1 + 1.4 = 2.4 its original value. That is, more than double.

    down_threshold: how far your portfolio needs to differ before you
        adjust to a higher withdrawal rate. If this is less than 0 then you delay reacting to bad news.
        If this is greater than 0, it means you "overreact" and keep a buffer.

    upward_rate_adjustment: how much of the upward adjustment to use: All of it? Only part?

    downward_rate_adjustment: how much of the downward adjustment to use

    ceiling_rate: the maximum withdrawal percentage. Stout & Mitchell say this
        doesn't really have any effect, since only super successful portfolios
        ever hit it.

    floor_rate: the minimum withdrawal percentage. Set it as low as you can tolerate.

    The "optimal portfolio size" is the present value required to maintain your
    current withdrawal rate until your expected death.

    With the defaults: When your current portfolio is 1.4x the "optimal" portfolio,
    you adjust the rate upwards; but you only get 20% of the upward adjustment.
    When you drop below the "optimal" portfolio, you make the downward adjustment
    immediately and fully.

    This means you are conservative: react immediately to bad news, take your time
    reacting to good news and don't take all of the upside.
    """
    def __init__(self, portfolio, harvest_strategy,
                    up_threshold = 1.4,
                    down_threshold = 0.0,
                    upward_rate_adjustment = .2,
                    downward_rate_adjustment = 1,
                    ceiling_rate = .4,
                    floor_rate = .03,
                    start_age = 65):
        super().__init__(portfolio, harvest_strategy)

        self.up_threshold = Decimal(up_threshold)
        self.down_threshold = Decimal(down_threshold)
        self.upward_rate_adjustment = Decimal(upward_rate_adjustment)
        self.downward_rate_adjustment = Decimal(downward_rate_adjustment)
        self.ceiling_rate = Decimal(ceiling_rate)
        self.floor_rate = Decimal(floor_rate)
        self.current_age = start_age

        # It isn't entirely clear but Stout & Mitchell seem to start with this
        self.current_rate = Decimal('.045')

    def get_life_expectancy(self):
        return mortality.life_expectancy(None, self.current_age)

    def get_rate(self):
        # To fully mimic Stout & Mitchell this should calculate
        # "the average portfolio rate of return that
        # has been historically realized, Avg r, in overlapping periods of time equal
        # to the retiree’s expected remaining life". That is, when you have 22
        # years left, use the average rate of return over 22-year periods. Then
        # the next year, when you have 21 years left, use the average over 21-year
        # periods.
        # But for now I'll just pick a fixed number
        return Decimal('.0322')

    def get_required_portfolio(self):
        amount = self.current_rate * self.portfolio.value
        pv = numpy.pv(float(self.get_rate()), self.get_life_expectancy(), float(-amount), when='beginning')
        return Decimal(pv)

    def _calc(self):
        if self.portfolio.value >= (1 + self.up_threshold) * self.get_required_portfolio():
            new_amount = pmt(self.get_rate(), self.get_life_expectancy(), self.portfolio.value)
            new_rate = new_amount / self.portfolio.value
            self.current_rate += (new_rate - self.current_rate) * self.upward_rate_adjustment
            self.current_rate = min(self.current_rate, self.ceiling_rate)
        if self.portfolio.value < (1 + self.down_threshold) * self.get_required_portfolio():
            new_amount = pmt(self.get_rate(), self.get_life_expectancy(), self.portfolio.value)
            new_rate = new_amount / self.portfolio.value
            self.current_rate -= (self.current_rate - new_rate) * self.downward_rate_adjustment
            self.current_rate = max(self.current_rate, self.floor_rate)

        amount = self.current_rate * self.portfolio.value
        self.current_age += 1
        return amount

    def start(self): return self._calc()
    def next(self): return self._calc()
