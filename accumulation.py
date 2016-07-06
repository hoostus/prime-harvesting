from decimal import Decimal

class AccumulationStrategy():
    def accumulate(self):
        '''
           This must be a co-routine .send(deposit_amount) every year
        '''
        pass

class N_RebalanceAccumulation(AccumulationStrategy):
    # subclasses must override this
    stock_pct = None

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def accumulate(self):
        while True:
            deposit_amount = yield
            self.portfolio.deposit_cash(deposit_amount)

            self.portfolio.sell_stocks(self.portfolio.stocks)
            self.portfolio.sell_bonds(self.portfolio.bonds)

            target_stocks = self.stock_pct * self.portfolio.value
            target_bonds = self.portfolio.value - target_stocks

            self.portfolio.buy_stocks(target_stocks)
            self.portfolio.buy_bonds(target_bonds)

class N_60_RebalanceAccumulation(N_RebalanceAccumulation):
    stock_pct = Decimal('.6')

class N_80_RebalanceAccumulation(N_RebalanceAccumulation):
    stock_pct = Decimal('.8')

class PrimeAccumulation(AccumulationStrategy):
    _stock_ceiling = Decimal('1.2')
    _min_stock_pct = Decimal('.6')

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def accumulate(self):
        while True:
            deposit_amount = yield
            self.portfolio.deposit_cash(deposit_amount)
            self.portfolio.buy_stocks(deposit_amount)

            if self.portfolio.stocks_real_gain < self._stock_ceiling:
                continue
            to_sell = self.portfolio.stocks * (self._stock_ceiling - 1)

            stocks_pct = self.portfolio.stocks / self.portfolio.value
            if stocks_pct <= self._min_stock_pct:
                continue
            max_sell = self.portfolio.value * (stocks_pct - self._min_stock_pct)

            to_sell = min(to_sell, max_sell)
            self.portfolio.sell_stocks(to_sell)
            self.portfolio.buy_bonds(to_sell)

            self.portfolio.reset_stocks_real_gain()
