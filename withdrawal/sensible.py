from decimal import Decimal
from .abc import WithdrawalStrategy

class SensibleWithdrawals(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, extra_return_boost=Decimal('.31'), initial_rate=Decimal('.05')):
        super().__init__(portfolio, harvest_strategy)

        self.initial_withdrawal = initial_rate * portfolio.value
        self.extra_return_boost = extra_return_boost
        self.initial_rate = initial_rate

    def start(self):
        return self.initial_withdrawal

    def next(self):
        inflation_adjusted_withdrawal_amount = self.initial_withdrawal / self.cumulative_inflation
        current_withdrawal_amount = inflation_adjusted_withdrawal_amount * .8

        base_portfolio_value = self.portfolio.value - current_withdrawal_amount
        previous_portfolio_amount *= (1 + change.inflation)
        extra_return = base_portfolio_value - previous_portfolio_amount

        if extra_return > 0:
            current_withdrawal_amount += extra_return * self.extra_return_boost

        current_withdrawal_amount = min(current_withdrawal_amount, self.portfolio.value)

        return current_withdrawal_amount
