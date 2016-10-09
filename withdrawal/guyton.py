from decimal import Decimal
from .abc import WithdrawalStrategy

# From Guyton & Klinger's "Decision Rules and Maximum Initial Withdrawal Rates"

class Guyton(WithdrawalStrategy):
    MAX_INFLATION_ADJUSTMENT = Decimal('.06')
    def __init__(self, portfolio, harvest_strategy, initial_rate=.05, start_age=65):
        super().__init__(portfolio, harvest_strategy)

        self.initial_rate = Decimal(initial_rate)
        self.current_age = 65

    def start(self):
        amount = self.portfolio.value * self.initial_rate
        self.previous_withdrawal_amount = amount
        self.previous_portfolio_value = self.portfolio.value - amount
        return amount

    def next(self):
        # If the portfolio has been exhausted, let's skip all
        # calculations below, some of which can result in ZeroDivisionError
        if self.portfolio.value == 0: return 0

        current_amount = self.previous_withdrawal_amount
        current_rate = current_amount / self.portfolio.value

        # Prosperity Rule
        if current_rate < (self.initial_rate * Decimal('.8')):
            current_amount *= Decimal('1.1')
            current_rate = current_amount / self.portfolio.value

        # Withdrawal Decision Rule 2 + Inflation Rule
        total_return = self.portfolio.value - self.previous_portfolio_value
        if (total_return > 0) or (current_rate < self.initial_rate):
            max_inflation = min(self.current_inflation, self.MAX_INFLATION_ADJUSTMENT)
            current_amount *= (1 + max_inflation)
            current_rate = current_amount / self.portfolio.value

        # Capital Preservation Rule
        # This rule is only supposed to apply in the early years of retirement.
        # G-K say to stop using it when there are <15 years of retirement left.
        # They analyse a 40 year retirement, so they intended to use this for the
        # first 25 years. That is, ages 65-90.
        # I'll do some hard coding here and just say "use this if you are under 90"
        if (self.current_age <= 91) and (current_rate > (self.initial_rate * Decimal('1.2'))):
            current_amount *= Decimal('.9')

        self.current_age += 1
        self.previous_withdrawal_amount = current_amount
        self.previous_portfolio_value = self.portfolio.value - current_amount
        return current_amount
        
