from decimal import Decimal
from .abc import WithdrawalStrategy

# These are all income smoothing algorithms. That means they shouldn't be
# used directly. Instead they need to wrap another algorithm.

# Note: some withdrawal algorithms ALREADY do income smoothing. These should
# only be used with withdrawal algorithsm that don't provide their own
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
            adjusted = self.last_year * (1 + self.current_inflation)
            amount = max(amount, adjusted * Decimal('.9'))
            amount = min(amount, adjusted * Decimal('1.1'))
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
