from decimal import Decimal
from .abc import WithdrawalStrategy
from .mufp import get_extended_mufp

class EM(WithdrawalStrategy):
    DEFAULT_SCALE_RATE = Decimal('.95')
    DEFAULT_FLOOR_RATE = Decimal('.025')
    DEFAULT_CAP_RATE = Decimal('1.5')
    DEFAULT_INITIAL_WITHDRAWAL_RATE = Decimal('.05')

    def __init__(self, portfolio, harvest_strategy,
                 scale_rate=DEFAULT_SCALE_RATE,
                 floor_rate=DEFAULT_FLOOR_RATE,
                 cap_rate=DEFAULT_CAP_RATE,
                 initial_withdrawal_rate=DEFAULT_INITIAL_WITHDRAWAL_RATE,
                 years_left=40):
        super().__init__(portfolio, harvest_strategy)

        self.scale_rate = scale_rate
        self.floor_rate = floor_rate
        self.cap_rate = cap_rate
        self.initial_withdrawal_rate = initial_withdrawal_rate
        self.adjusted_cap_rate = cap_rate * initial_withdrawal_rate
        self.years_left = years_left

    def start(self):
        withdrawal = self.initial_withdrawal_rate * self.portfolio.value
        # Store this for later because we will need it in
        # future iterations
        self.last_year_withdrawal = withdrawal

        return withdrawal

    def next(self):
        # Update internal state now that another year has passed
        # If we go more than 40 years, just keep pretending we're still in the final year.
        self.years_left = max(1, self.years_left - 1)

        inflation_adjusted_withdrawal_amount = self.last_year_withdrawal * (1 + self.current_inflation)

        withdrawal_rate = get_extended_mufp(self.years_left)
        withdrawal = withdrawal_rate * self.portfolio.value

        scale_boundary = Decimal('.75') * inflation_adjusted_withdrawal_amount
        if withdrawal > scale_boundary:
            scale_diff = withdrawal - scale_boundary
            scale_ratio = scale_diff / scale_boundary
            if scale_ratio > 1:
                scale_ratio = Decimal('1.0')
            withdrawal = scale_boundary + (scale_diff * scale_ratio * self.scale_rate)

        cap_amount = (self.adjusted_cap_rate / self.initial_withdrawal_rate) * inflation_adjusted_withdrawal_amount
        withdrawal = min(withdrawal, cap_amount)

        floor_amount = (self.floor_rate / self.initial_withdrawal_rate) * inflation_adjusted_withdrawal_amount
        withdrawal = max(withdrawal, floor_amount)

        return withdrawal

def ECM(portfolio, harvest_strategy):
    return EM(portfolio, harvest_strategy, scale_rate=Decimal('.6'), floor_rate=Decimal('.025'))

# TODO: This is still a work in progress.
class DeltaPrime(WithdrawalStrategy):
    def __init__(self, portfolio, initial_withdrawal_rate=Decimal('.05')):
        super().__init__(portfolio, harvest_strategy)

        self.initial_withdrawal_rate = initial_withdrawal_rate
        self.initial_withdrawal = self.initial_withdrawal_rate * self.portfolio.value

    def start(self):
        return self.initial_withdrawal

    def next(self):
        current_withdrawal_amount = self.initial_withdrawal_rate * self.portfolio.value
        inflation_adjusted_withdrawal_amount = self.initial_withdrawal / self.cumulative_inflation

        if current_withdrawal_amount < (inflation_adjusted_withdrawal_amount * Decimal('.9')):
            current_withdrawal_rate = inflation_adjusted_withdrawal_amount / self.portfolio.value
            scalar = Decimal('1.14') - (Decimal('3.38') * current_withdrawal_rate)
            if scalar < Decimal('.05'):
                scalar = Decimal('.05')
            current_withdrawal_amount = scalar * inflation_adjusted_withdrawal_amount

        baseline_years_left = self.portfolio.value / inflation_adjusted_withdrawal_amount
