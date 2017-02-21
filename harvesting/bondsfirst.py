from .abc import HarvestingStrategy
from decimal import Decimal

class BondsFirst(HarvestingStrategy):
    def __init__(self, portfolio):
        super().__init__(portfolio)

    def harvest(self):
        amount = yield
        while True:
            # Sell bonds first
            if self.portfolio.bonds > 0:
                bond_amount = min(amount, self.portfolio.bonds)
                self.portfolio.sell_bonds(bond_amount)
                amount -= bond_amount


            # We can only take out however much is actually left in the portfolio
            actual_amount = min(self.portfolio.value, amount)
            
            self.portfolio.sell_stocks(actual_amount)

            amount = yield self.portfolio.empty_cash()
