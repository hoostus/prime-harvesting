from .abc import HarvestingStrategy
from decimal import Decimal

class Weiss(HarvestingStrategy):
    def __init__(self, portfolio, stock_pct=Decimal('.6')):
        super().__init__(portfolio)
        self.stock_pct = Decimal(stock_pct)
        self.trigger = Decimal('.05')
        self.year = 1

    def get_annualised_returns(self):
        return (pow(1 + self.trigger, self.year) * self.portfolio.starting_stocks_real)

    def harvest(self):
        amount = yield
        while True:
            # Start by selling bonds.
            bonds_sold = min(amount, self.portfolio.bonds)
            self.portfolio.sell_bonds(bonds_sold)
            amount -= bonds_sold

            # If that wasn't enough then also sell some stocks
            stocks_sold = min(amount, self.portfolio.stocks)
            self.portfolio.sell_stocks(stocks_sold)

            cash_amount = self.portfolio.empty_cash()

            # Check our rebalancing triggers
            if (self.portfolio.stocks_pct < self.stock_pct) or (self.portfolio.bonds == 0) or (self.portfolio.stocks > self.get_annualised_returns()):
                self.portfolio.sell_stocks(self.portfolio.stocks)
                self.portfolio.sell_bonds(self.portfolio.bonds)
                self.portfolio.buy_stocks(self.portfolio.value * self.stock_pct)
                self.portfolio.buy_bonds(self.portfolio.cash)
                assert self.portfolio.cash == 0
            

            amount = yield cash_amount

            self.year += 1