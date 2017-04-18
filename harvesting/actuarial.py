from .abc import HarvestingStrategy
from decimal import Decimal
import numpy

# Downsides of PrimeHarvesting: the memory effect. Someone who is exactly
# the same as you but retires 1 year later should act the same under
# the strategy.

# Good parts of PrimeHarvesting:

# Consume bonds first. Protect stocks.
# Convert stocks to bonds when they've gained.
# Allow momentum to run some, don't harvest gains too quickly.

# What about LMP? LMP seems to make some sense but...there's no "gradual" to it
# You go from 60/40 to LMP on the day you retire? What about the day before that?
# So is the following really LMPHarvesting?

# Can/should you use the same strategy *before* retirement?

class ActuarialHarvesting:
    def __init__(self, portfolio, starting_age=65, final_age=100):
        self.portfolio = portfolio
        self.current_age = starting_age
        self.final_age = final_age

        # The DMS real rate of return for global equities
        #self.rate = Decimal('.054')
        self.rate = Decimal('.09')

    def harvest(self):
        amount = yield
        while True:
            # In order to get rid of the memory effect, the parameters to PV
            # have to independent of *when* you retire. But they can use current information

            nper = self.final_age - self.current_age
            nper = max(nper, 5)
            portfolio_goal = Decimal(-numpy.pv(float(self.rate), nper, float(amount), when='beginning'))

            if self.portfolio.stocks >= portfolio_goal:
                #import pdb;pdb.set_trace()
                harvest_amount = (self.portfolio.stocks - portfolio_goal)
                self.portfolio.sell_stocks(harvest_amount)
                self.portfolio.buy_bonds(harvest_amount)

            amount = min(amount, self.portfolio.value)

            amount_bonds = min(amount, self.portfolio.bonds)
            amount_stocks = amount - amount_bonds
            self.portfolio.sell_bonds(amount_bonds)
            self.portfolio.sell_stocks(amount_stocks)
            
            amount = yield self.portfolio.empty_cash()

            self.current_age += 1