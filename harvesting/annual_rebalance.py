from .abc import HarvestingStrategy
from decimal import Decimal

class AnnualRebalancing(HarvestingStrategy):
    def __init__(self, portfolio, stock_pct):
        super().__init__(portfolio)
        self.stock_pct = Decimal(stock_pct)

    def harvest(self):
        amount = yield
        while True:
            # first generate some cash
            self.portfolio.sell_stocks(self.portfolio.stocks)
            self.portfolio.sell_bonds(self.portfolio.bonds)

            # We can only take out however much is actually left in the portfolio
            actual_amount = min(self.portfolio.value, amount)

            new_val = self.portfolio.value - actual_amount
            if new_val > 0:
                self.portfolio.buy_stocks(new_val * self.stock_pct)
                self.portfolio.buy_bonds(self.portfolio.cash - actual_amount)

            amount = yield self.portfolio.empty_cash()

def make_rebalancer(stock_pct):
    class Rebalancer(AnnualRebalancing):
        def __init__(self, portfolio):
            super().__init__(portfolio, stock_pct)
    return Rebalancer
