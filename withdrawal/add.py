from decimal import Decimal
from .abc import WithdrawalStrategy
from metrics import average, pmt
from collections import deque
from metrics import mean

# This ignores the Reserve stuff for now.

class ADD(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy,
            withdrawal_rate=Decimal('0.05'),
            maximum_increase=Decimal('1.05'),
            reserve_max_withdrawal=Decimal('0.20'),
            floor=Decimal('0.95'),
            smoothed_years=5
            ):
        super().__init__(portfolio, harvest_strategy)

        self.past_portfolio_values = deque(maxlen=smoothed_years)

        self.withdrawal_rate = withdrawal_rate
        self.maximum_increase = maximum_increase
        self.reserve_max_withdrawal = reserve_max_withdrawal
        self.floor = floor


    def start(self):
        self.past_portfolio_values.append(self.portfolio.value)
        withdrawal = self.withdrawal_rate * self.portfolio.value

        self.minimum = withdrawal
        self.last_year = withdrawal

        return withdrawal

    def next(self):
        self.past_portfolio_values.append(self.portfolio.value)

        average_portfolio_value = Decimal(mean(self.past_portfolio_values))
        smoothed_portfolio_value = average_portfolio_value * Decimal('1.1')

        withdrawal = self.withdrawal_rate * average_portfolio_value
        ceilinged = min(withdrawal, self.last_year * self.maximum_increase)
        floored = max(ceilinged, self.minimum * self.floor)

        self.last_year = floored
        if floored < self.minimum:
            self.minimum = floored

        return floored
