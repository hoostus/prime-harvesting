from decimal import Decimal
from .abc import WithdrawalStrategy

class SensibleWithdrawals(WithdrawalStrategy):
    """ Gummy's Sensible Withdrawals

    The 'sensible' idea is you set a floor and only get to withdraw
    above that if the market was good last year.

    gummy doesn't really tell you what to pick for the starting rate,
    the floor, or how much of the profits you get to take.

    But he mentions 5%, 3%, 25%, so we'll use those for default
    parameters

    http://www.gummy-stuff.org/sensible_withdrawals.htm
    """

    def __init__(self, portfolio, harvest_strategy, extra_return_boost=Decimal('.25'), initial_rate=Decimal('.04'), min_rate=Decimal('.03')):
        super().__init__(portfolio, harvest_strategy)

        self.floor = min_rate * portfolio.value
        self.extra_return_boost = extra_return_boost
        self.initial_rate = initial_rate

    def start(self):
        withdrawal = self.initial_rate * self.portfolio.value
        self.previous_portfolio_value = self.portfolio.value - withdrawal
        return withdrawal

    def next(self):
        current_withdrawal_amount = self.floor * (1 + self.current_inflation)

        base_portfolio_value = self.portfolio.value - current_withdrawal_amount
        adjusted_previous_portfolio = self.previous_portfolio_value * (1 + self.current_inflation)
        extra_return = base_portfolio_value - adjusted_previous_portfolio

        if extra_return > 0:
            current_withdrawal_amount += extra_return * self.extra_return_boost

        current_withdrawal_amount = min(current_withdrawal_amount, self.portfolio.value)
        self.previous_portfolio_value = self.portfolio.value - current_withdrawal_amount

        return current_withdrawal_amount
