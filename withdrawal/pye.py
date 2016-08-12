from decimal import Decimal
from .abc import WithdrawalStrategy
from metrics import pmt

class RetrenchmentRule(WithdrawalStrategy):
    """ Gorden Pye's retrenchment rule is another PMT based solution. """
    def __init__(self, portfolio, harvest_strategy, current_age=65):
        super().__init__(portfolio, harvest_strategy)

        self.discount_rate = .08
        self.final_age = 110

        self.current_age = current_age

    def _calc(self):
        return pmt(self.discount_rate, self.final_age - self.current_age, self.portfolio.value)

    def start(self):
        return self._calc()

    def next(self):
            # Update our internal state.
            self.current_age += 1

            if self.current_age < self.final_age:
                withdrawal = self._calc()
            else:
                # We ran out of money and are still alive :(
                withdrawal = 0

            return withdrawal
