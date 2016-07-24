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

class N_50_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.5')
class N_60_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.6')
class N_100_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('1')
    

class PrimeHarvesting(HarvestingStrategy):
    _stock_ceiling = Decimal('1.2')

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def stock_increase(self):
        return self.portfolio.stocks / self.portfolio.starting_stocks_real

    def harvest(self):
        amount = yield
        while True:
            if self.stock_increase() > self._stock_ceiling:
                to_sell = self.portfolio.stocks / 5
                self.portfolio.sell_stocks(to_sell)
                self.portfolio.buy_bonds(to_sell)

            bond_amount = min(amount, self.portfolio.bonds)
            self.portfolio.sell_bonds(bond_amount)

            if self.portfolio.cash < amount:
                remainder = amount - self.portfolio.cash
                stock_amount = min(remainder, self.portfolio.stocks)
                self.portfolio.sell_stocks(stock_amount)

            amount = yield self.portfolio.empty_cash()
