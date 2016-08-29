from .abc import HarvestingStrategy
from decimal import Decimal

class PrimeHarvesting(HarvestingStrategy):
    _stock_ceiling = Decimal('1.2')

    def stock_increase(self):
        return self.portfolio.stocks / self.portfolio.starting_stocks_real

    def calc_to_sell(self):
        return self.portfolio.stocks / 5

    def harvest(self):
        amount = yield
        while True:
            if self.stock_increase() > self._stock_ceiling:
                to_sell = self.calc_to_sell()
                self.portfolio.sell_stocks(to_sell)
                self.portfolio.buy_bonds(to_sell)

            bond_amount = min(amount, self.portfolio.bonds)
            self.portfolio.sell_bonds(bond_amount)

            if self.portfolio.cash < amount:
                remainder = amount - self.portfolio.cash
                stock_amount = min(remainder, self.portfolio.stocks)
                self.portfolio.sell_stocks(stock_amount)

            amount = yield self.portfolio.empty_cash()

class AltPrimeHarvesting(PrimeHarvesting):
    def __init__(self, portfolio):
        super().__init__(portfolio)
        self.initial_stock_pct = portfolio.stocks_pct

    def calc_to_sell(self):
        stock_target = self.portfolio.value * self.initial_stock_pct
        # How can we get to a point where the "up 20%" rule says we should be
        # Selling stocks but the "don't sell below your original stock pct" rule
        # says not to sell stocks?
        # But it is mathematically possible..
        return max(0, self.portfolio.stocks - stock_target)
