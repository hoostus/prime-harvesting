from decimal import Decimal
from .abc import WithdrawalStrategy

class SensibleWithdrawals(WithdrawalStrategy):
    """ Gummy's Sensible Withdrawals

    The idea is: you get 80% of the inflation-adjusted amount you took
    last year plus a percentage of any gains.

    You can pick any starting withdrawal rate and any percentage of gains.

    McClung used 5% and 31% in his book, so I've mirrored that.

    http://www.gummy-stuff.org/sensible_withdrawals.htm
    """

    def __init__(self, portfolio, harvest_strategy, extra_return_boost=Decimal('.31'), initial_rate=Decimal('.05')):
        super().__init__(portfolio, harvest_strategy)

        self.initial_withdrawal = initial_rate * portfolio.value
        self.extra_return_boost = extra_return_boost
        self.initial_rate = initial_rate

    def start(self):
        withdrawal = self.initial_withdrawal
        self.previous_portfolio_value = self.portfolio.value - withdrawal
        self.previous_withdrawal = withdrawal
        return withdrawal

    def next(self):
        inflation_adjusted_withdrawal_amount = self.previous_withdrawal * (1 + self.current_inflation)
        current_withdrawal_amount = inflation_adjusted_withdrawal_amount * Decimal('.8')

        base_portfolio_value = self.portfolio.value - current_withdrawal_amount
        adjusted_previous_portfolio = self.previous_portfolio_value * (1 + self.current_inflation)
        extra_return = base_portfolio_value - adjusted_previous_portfolio

        if extra_return > 0:
            current_withdrawal_amount += extra_return * self.extra_return_boost

        current_withdrawal_amount = min(current_withdrawal_amount, self.portfolio.value)

        self.previous_withdrawal = current_withdrawal_amount
        self.previous_portfolio_value = self.portfolio.value - current_withdrawal_amount

        return current_withdrawal_amount
