from decimal import Decimal

class HarvestingStrategy():
    def harvest(self, annual_harvest):
        '''
           This is must be a co-routine .send(AnnualHarvest) every year
        '''
        assert isinstance(annual_harvest, AnnualHarvest)

class N_RebalanceHarvesting(HarvestingStrategy):
    # subclasses must override this
    stock_pct = None

    def __init__(self, portfolio):
        super().__init__()
        self.portfolio = portfolio

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
                self.portfolio.buy_bonds(self.portfolio.cash - amount)

            amount = yield self.portfolio.empty_cash()

class N_10_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.1')
class N_20_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.2')
class N_30_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.3')
class N_40_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.4')
class N_50_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.5')
class N_60_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.6')
class N_70_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.7')
class N_80_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.8')
class N_90_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.9')
class N_100_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('1')

class PrimeHarvesting(HarvestingStrategy):
    _stock_ceiling = Decimal('1.2')

    def __init__(self, portfolio):
        super().__init__()
        self.portfolio = portfolio

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
