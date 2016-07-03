from decimal import Decimal
from adt import AnnualChange

class Portfolio():
    def __init__(self, stocks, bonds, cash = 0):
        self._stocks = Decimal(stocks)
        self._bonds = Decimal(bonds)
        self._cash = Decimal(cash)
        self._starting_value = Decimal(stocks + bonds + cash)
        self._starting_stocks = Decimal(stocks)
        self._stocks_real_gain = Decimal('1.0')
        self.inflation = Decimal('1.0')

    @property
    def starting_stocks_real(self):
        return self._starting_stocks * self.inflation

    @property
    def starting_value_real(self):
        return self.starting_value * self.inflation

    @property
    def starting_value(self):
        return self._starting_value

    @property
    def stocks_real_gain(self):
        return self._stocks_real_gain

    @property
    def stocks(self):
        return self._stocks

    @property
    def bonds(self):
        return self._bonds

    @property
    def cash(self):
        return self._cash

    @property
    def value(self):
        return self.bonds + self.stocks + self.cash

    @property
    def real_value(self):
        return self.value / self.inflation

    def deposit_cash(self, amount):
        assert amount >= 0 # use withdraw_cash() instead of withdrawals
        self._cash += amount
        return self.cash

    def withdraw_cash(self, amount):
        assert amount <= self._cash
        self._cash -= amount
        return self.cash

    def empty_cash(self):
        x = self.cash
        self._cash = 0
        return x

    def sell_stocks(self, amount):
        assert amount <= self._stocks
        self._stocks -= amount
        self._cash += amount
        return self.cash

    def buy_stocks(self, amount):
        assert amount <= self._cash
        self._stocks += amount
        self._cash -= amount
        return self.cash

    def sell_bonds(self, amount):
        assert amount <= self._bonds
        self._bonds -= amount
        self._cash += amount
        return self.cash

    def buy_bonds(self, amount):
        assert amount <= self._cash
        self._bonds += amount
        self._cash -= amount
        return self.cash

    def adjust_returns(self, change):
        assert isinstance(change, AnnualChange)
        prev_value = self.value
        self._bonds *= 1 + change.bonds
        self._stocks *= 1 + change.stocks
        self._stocks_real_gain *= 1 + (change.stocks - change.inflation)
        self.inflation *= (1 + change.inflation)
        if prev_value != 0:
            gains = (self.value - prev_value) / prev_value
        else:
            gains = 0 # empty portfolio, no percentage gain
        return (gains, prev_value, self.value)

    def reset_stocks_real_gain(self):
        self._stocks_real_gain = Decimal('1.0')
