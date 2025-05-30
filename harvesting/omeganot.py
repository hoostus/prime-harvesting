from .abc import HarvestingStrategy
from decimal import Decimal

class OmegaNot(HarvestingStrategy):
    def __init__(self, portfolio, ceiling=Decimal('1')):
            super().__init__(portfolio)
            self._stock_ceiling = ceiling
            self.__name__ = 'OmegaNot (ceiling=%s)' % ceiling

    def stock_increase(self):
        return self.portfolio.stocks / self.portfolio.starting_stocks_real

    def calc_to_sell(self):
        return self.portfolio.stocks - self.portfolio.starting_stocks_real

    def do_harvest(self, amount):
        # If stocks have appreciated above their
        # initial (inflation-adjusted) starting value
        # then sell the excess
        if self.stock_increase() > self._stock_ceiling:
            to_sell = self.calc_to_sell()
            stocks_sold = min(amount, to_sell)
            self.portfolio.sell_stocks(stocks_sold)
            amount -= stocks_sold

        # If that wasn't enough to fully cover the withdrawal
        # then also sell some bonds
        bonds_sold = min(amount, self.portfolio.bonds)
        self.portfolio.sell_bonds(bonds_sold)
        amount -= bonds_sold

        # And if we've also run out of bonds then start selling
        # stocks as well.
        stocks_sold = min(amount, self.portfolio.stocks)
        self.portfolio.sell_stocks(stocks_sold)
