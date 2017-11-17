from decimal import Decimal
from .abc import WithdrawalStrategy
import pandas

# https://earlyretirementnow.com/2017/08/30/the-ultimate-guide-to-safe-withdrawal-rates-part-18-flexibility-CAPE-Based-Rules/

class CAPEPercentage(WithdrawalStrategy):
    BASE_YEAR = 1881

    def __init__(self, portfolio, harvest_strategy, start_year=BASE_YEAR, a=0.01952, b=0.359, c=0.102, d=-0.081):
        assert start_year >= self.BASE_YEAR

        super().__init__(portfolio, harvest_strategy)

        self.df = pandas.read_csv('cape10.csv')
        self.year = start_year

        self.a = Decimal(a)
        self.b = Decimal(b)
        self.c = Decimal(c)
        self.d = Decimal(d)

    def get_cape(self):
        return self.df.iloc[self.year - self.BASE_YEAR]["CAPE10"]

    def get_inv_cape(self):
        return Decimal(1/self.get_cape())# + Decimal('.03')

    def get_10yr_yield(self):
        return 0
    def get_cash_yield(self):
        return 0

    def get_withdrawal_pct(self):
        B = self.b * self.get_inv_cape()
        C = self.c * self.get_10yr_yield()
        D = self.d * self.get_cash_yield()
        return self.a + B + C + D

    def calculate(self):
        return self.get_withdrawal_pct() * self.portfolio.value

    def start(self):
        return self.calculate()

    def next(self):
        self.year += 1
        amount = self.calculate()
        return amount
