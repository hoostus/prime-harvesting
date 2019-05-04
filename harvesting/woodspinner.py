from .abc import HarvestingStrategy
from decimal import Decimal

# https://www.bogleheads.org/forum/viewtopic.php?f=10&t=269091#p4309134
# https://www.bogleheads.org/forum/viewtopic.php?f=10&t=269091#p4310215

# Bucket-1, 2 years in cash/short-term treas
# Bucket-2, 8 year in intermediate treas
# Bucket-3, equities

# Bucket-1+2 never less than 40% of the portfolio
# Bucket-3 can shift between 40-60%

# Buckets refilled yearly
# "for me the key is that my AA can shift within a band of 40/60 an 60/40"
# During Bear Markets the preference will be to spend down the fixed income side and use any excess capacity of the Fixed Income allocation band to buy equities. 
# During Bull Markets, the preference will be to spend down from the Equity side and use any excess capacity to buy Fixed Income.

class WoodSpinner(HarvestingStrategy):
    _StockCeiling = Decimal('0.6')
    _StockFloor = Decimal('0.4')

    def __init__(self, portfolio):
        super().__init__(portfolio)
        # we need 8% of the portfolio (2 years @ 4%) in cash
        self.portfolio.sell_bonds(self.portfolio.value * Decimal('.08'))
        self.high_water = self.portfolio.stocks_real_gain

    def is_bear(self):
        """ this really needs to account for withdrawals...ugh """
        if self.portfolio.stocks_real_gain > self.high_water:
            self.high_water = self.portfolio.stocks_real_gain

        if self.portfolio.stocks_real_gain <= self.high_water * Decimal('0.8'):
            return True
        else:
            return False

    def do_harvest(self, amount):
        current_amount = amount

        # are we in a bear or a bull?
        if self.is_bear():
            # first withdraw from cash
            cash_amount = min(amount, self.portfolio.cash)
            # don't need to do anything here, the withdrawal actually happens elsewhere
            #self.portfolio.withdraw_cash(cash_amount)
            amount -= cash_amount

            # then withdraw from bonds
            bond_amount = min(amount, self.portfolio.bonds)
            self.portfolio.sell_bonds(bond_amount)
            amount -= bond_amount
        
        # withdraw anything else we need from stocks; if we're not in a
        # bear market this means withdraw everything from stocks
        stock_amount = min(amount, self.portfolio.stocks)
        self.portfolio.sell_stocks(stock_amount)
        amount -= stock_amount

        def get_stock_pct():
            if (self.portfolio.value - current_amount) == 0:
                return 0
            else:
                return (self.portfolio.stocks) / (self.portfolio.value - current_amount)

        # if we have any money left over after withdrawals we can rebalance
        if self.portfolio.value > current_amount:
            # we are over 60/40
            if get_stock_pct() > self._StockCeiling:
                # rebalance into bonds
                stock_target = (self.portfolio.value - current_amount) * self._StockCeiling
                sell_stocks = self.portfolio.stocks - stock_target
                self.portfolio.sell_stocks(sell_stocks)
                self.portfolio.buy_bonds(sell_stocks)

            # if we are under 40/60
            if get_stock_pct() < self._StockFloor:
                # rebalance into stocks...this is slightly tricky
                # because we need to use bonds+cash to do this

                # first use any cash to buy bonds. then we just need
                # to rebalance between stocks + bonds.
                cash = (self.portfolio.cash - current_amount)
                self.portfolio.buy_bonds(cash)

                stock_target = (self.portfolio.value - current_amount) * self._StockFloor
                buy_stocks = stock_target - self.portfolio.stocks
                self.portfolio.sell_bonds(buy_stocks)
                self.portfolio.buy_stocks(buy_stocks)

            # finally, see if we need to refill the cash bucket...
            if (self.portfolio.cash - current_amount) == 0:
                sell_bonds = min(self.portfolio.bonds, 2 * current_amount)
                self.portfolio.sell_bonds(sell_bonds)
