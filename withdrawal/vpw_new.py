from decimal import Decimal
from metrics import pmt
from .abc import WithdrawalStrategy

class VPW(WithdrawalStrategy):
    # From the VPW spreadsheet. These are taken from
    # the Credit Suisse 2016 Global Returns Yearbook for global
    # stocks and global bonds historical rates from 1900-2015
    STOCK_GROWTH_RATE = Decimal('.05')
    BOND_GROWTH_RATE = Decimal('.018')

    def __init__(self, portfolio, harvest_strategy, years_left=35, replan=False):
        super().__init__(portfolio, harvest_strategy)

        self.years_left = years_left
        self.stock_growth_rate = VPW.STOCK_GROWTH_RATE
        self.bond_growth_rate = VPW.BOND_GROWTH_RATE

        self.replan = replan

    def _calc(self):
        rate = (self.portfolio.stocks_pct * self.stock_growth_rate
                + self.portfolio.bonds_pct * self.bond_growth_rate)
        return pmt(rate, self.years_left, self.portfolio.value)

    def start(self): return self._calc()

    def next(self):
        self.years_left -= 1

        if self.replan:
            if self.years_left < 15:
                self.years_left += 5

        return self._calc()

