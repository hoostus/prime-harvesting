from decimal import Decimal
from .abc import WithdrawalStrategy
from collections import deque
from metrics import mean
import pandas

# These are all income smoothing algorithms. That means they shouldn't be
# used directly. Instead they need to wrap another algorithm.

# Note: some withdrawal algorithms ALREADY do income smoothing. These should
# only be used with withdrawal algorithms that don't provide their own
# smoothing.

class SteinerSmoothing(WithdrawalStrategy):
    """ Ken Steiner's suggestion is to CPI adjust last year's withdrawal
    and then see if it fall that is within +/- 10% of the current withdrawl
    amount. If not, then lower/raise it to smooth spending.

    http://howmuchcaniaffordtospendinretirement.webs.com/Better_Systematic_Withdrawal_Strategy_03062014.pdf
    """

    def __init__(self, real_withdrawal_strategy):
        super().__init__(real_withdrawal_strategy.portfolio,
            real_withdrawal_strategy.harvest)

        self.strategy = real_withdrawal_strategy
        self.last_year = None

    def start(self):
        amount = self.strategy.start()
        self.last_year = amount
        return amount

    def next(self):
        amount = self.strategy.next()
        if self.last_year:
            low_corridor = amount * Decimal('.9')
            high_corridor = amount * Decimal('1.1')
            adjusted = self.last_year * (1 + self.current_inflation)
            if low_corridor < adjusted < high_corridor:
                amount = adjusted
            elif adjusted > high_corridor:
                amount = high_corridor
            else:
                amount = low_corridor
        self.last_year = amount
        return amount

class LonginvestSmoothing(WithdrawalStrategy):
    """
    https://www.bogleheads.org/forum/viewtopic.php?t=160073&start=50#p2418714
    """
    def __init__(self, real_withdrawal_strategy):
        super().__init__(real_withdrawal_strategy.portfolio,
            real_withdrawal_strategy.harvest)

        self.strategy = real_withdrawal_strategy
        self.last_year = None
        self.trigger = Decimal('1.3')
        self.adjustment = Decimal('.1')

    def start(self):
        amount = self.strategy.start()
        self.last_year = amount
        return amount

    def next(self):
        amount = self.strategy.next()
        if self.last_year:
            if amount > self.last_year:
                amount = max(amount / self.trigger,
                    self.last_year + (amount - self.last_year) * self.adjustment)
            else:
                amount = min(amount * self.trigger,
                    self.last_year - (self.last_year - amount) * self.adjustment)
        self.last_year = amount
        return amount

class RollingAverageSmoothing(WithdrawalStrategy):
    """ Take a rolling average of the last N years """
    def __init__(self, real_withdrawal_strategy, n=3):
        super().__init__(real_withdrawal_strategy.portfolio,
            real_withdrawal_strategy.harvest)

        self.strategy = real_withdrawal_strategy
        self.lookback = deque(maxlen=n)

    def start(self):
        amount = self.strategy.start()
        self.lookback.append(amount)
        return amount

    def next(self):
        amount = self.strategy.next()
        self.lookback.append(amount)
        return Decimal(mean(self.lookback))

class CAPE10Smoothing(WithdrawalStrategy):
    """ This only works for a PMT system. We change the discount rate
    every year based on 1/CAPE10. """

    BASE_YEAR = 1881

    def __init__(self, start_year, real_withdrawal_strategy):
        assert type(real_withdrawal_strategy).__name__ == 'VPW'
        assert start_year >= self.BASE_YEAR
        super().__init__(real_withdrawal_strategy.portfolio,
            real_withdrawal_strategy.harvest)

        self.strategy = real_withdrawal_strategy
        self.df = pandas.read_csv('cape10.csv')
        self.year = start_year

    def get_cape(self):
        return self.df.iloc[self.year - self.BASE_YEAR]["CAPE10"]

    def get_inv_cape(self):
        return Decimal(1/self.get_cape())# + Decimal('.03')

    def start(self):
        self.strategy.stock_growth_rate = self.get_inv_cape()
        amount = self.strategy.start()
        return amount

    def next(self):
        self.year += 1
        self.strategy.stock_growth_rate = self.get_inv_cape()
        amount = self.strategy.next()
        return amount
