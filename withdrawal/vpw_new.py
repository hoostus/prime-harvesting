from decimal import Decimal
from metrics import pmt
from .abc import WithdrawalStrategy

class VPW(WithdrawalStrategy):
    # From the VPW spreadsheet. These are taken from
    # the Credit Suisse 2016 Global Returns Yearbook for global
    # stocks and global bonds historical rates from 1900-2015
    STOCK_GROWTH_RATE = Decimal('.05')
    BOND_GROWTH_RATE = Decimal('.018')

    def __init__(self, portfolio, harvest_strategy, years_left=35):
        super().__init__(portfolio, harvest_strategy)

        self.years_left = years_left

    def _calc(self):
        rate = (self.portfolio.stocks_pct * VPW.STOCK_GROWTH_RATE
                + self.portfolio.bonds_pct * VPW.BOND_GROWTH_RATE)
        return pmt(rate, self.years_left, self.portfolio.value)

    def start(self): return self._calc()

    def next(self):
        self.years_left -= 1

        return self._calc()