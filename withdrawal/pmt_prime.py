from decimal import Decimal
from .abc import WithdrawalStrategy
from metrics import pmt

class PMTPrime(WithdrawalStrategy):
    """
    We start with an initial withdrawal rate, which is equal
    to the PMT calculation (with some valuation twist?)

    Each year we adjust that upwards for inflation.
    Then we run the PMT calculation.

    If we are ABOVE the PMT calculation, then we cut to the PMT value.
    If we are BELOW the PMT calculation, then we have Excess Funds.
    We can do two things with the Excess Funds.
    1. Convert to bonds ("prime harvesting")
    2. Increase our standard of living
    """
    def __init__(self, portfolio,
            current_age=65,
            final_age=110,
            discount_rate=.06,
            lifestyle_pct=.25,
            lifestyle_cap=2):
        strategy = self.harvest()
        strategy.send(None)
        super().__init__(portfolio, strategy)

        self.discount_rate = discount_rate
        self.final_age = final_age
        self.current_age = current_age
        self.current_withdrawal = pmt(self.discount_rate, self.final_age - self.current_age, self.portfolio.value)
        self.initial_withdrawal = self.current_withdrawal
        self.lifestyle_pct = Decimal(lifestyle_pct)
        self.target_bonds = portfolio.bonds_pct
        self.max_withdrawal = self.initial_withdrawal * Decimal(lifestyle_cap)

    def _calc(self):
        p_v = pmt(self.discount_rate, self.final_age - self.current_age, self.portfolio.value)

        # React immediately to downward market conditions.
        if p_v < self.current_withdrawal:
            self.current_withdrawal = p_v
        # Only do the harvest if we aren't under water from where we started
        elif p_v < self.initial_withdrawal:
            self.current_withdrawal = p_v
        else:
            excess_funds = p_v - self.current_withdrawal
            lifestyle_creep = excess_funds * self.lifestyle_pct
            self.current_withdrawal = min(lifestyle_creep + self.current_withdrawal, self.max_withdrawal)
        return self.current_withdrawal

    def harvest(self):
        amount = yield
        while True:
            amount_left = amount

            if self.portfolio.bonds_pct > self.target_bonds:
                bonds_excess = (self.portfolio.bonds_pct - self.target_bonds) * self.portfolio.value
                bonds_excess = round(bonds_excess)
                bonds_to_sell = min(amount, bonds_excess)
                self.portfolio.sell_bonds(bonds_to_sell)
                amount_left -= bonds_to_sell
            else:
                bonds_deficit = -(self.portfolio.bonds_pct - self.target_bonds) * self.portfolio.value
                bonds_deficit = round(bonds_deficit)
                self.portfolio.sell_stocks(bonds_deficit)
                self.portfolio.buy_bonds(bonds_deficit)

            bonds_to_sell = amount_left * self.target_bonds
            stocks_to_sell = amount_left - bonds_to_sell
            self.portfolio.sell_bonds(bonds_to_sell)
            self.portfolio.sell_stocks(stocks_to_sell)

            pmt_amount = pmt(self.discount_rate, self.final_age - self.current_age, self.portfolio.value)
            if amount < pmt_amount and amount >= self.initial_withdrawal:
                harvest = pmt_amount - amount
                self.portfolio.buy_bonds(harvest)

            amount = yield self.portfolio.empty_cash()


    def start(self):
        return self.initial_withdrawal

    def next(self):
            # Update our internal state.
            self.current_age += 1
            self.current_withdrawal *= 1 + self.current_inflation
            self.max_withdrawal *= 1 + self.current_inflation
            self.initial_withdrawal *= 1 + self.current_inflation

            if self.current_age < self.final_age:
                withdrawal = self._calc()
            else:
                # We've reached the end of our PMT calculations...
                # What do we do next?
                withdrawal = 0

            return withdrawal
