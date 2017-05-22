from .abc import HarvestingStrategy
from decimal import Decimal
import numpy
import mortality

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
    def __init__(self, portfolio, starting_age=65, final_age=95):
        self.portfolio = portfolio
        self.current_age = starting_age
        self.final_age = final_age

        # The DMS real rate of return for global equities
        self.rate = Decimal('.054')
        #self.rate = Decimal('.09')

    def harvest(self):
        amount = yield
        while True:
            # In order to get rid of the memory effect, the parameters to PV
            # have to independent of *when* you retire. But they can use current information

            # This is just our life expectancy.
            nper = max(5, 100 - self.current_age)
            #nper = mortality.life_expectancy(self.current_age, None)

            # But let's also subtract out however many years worth of bonds
            # we currently have. This assumes that bonds keep up with inflation
            # which is a dubious proposition...
            #nper -= int(self.portfolio.bonds / amount)

            # Set a minimum years worth of stock. Pretty arbitrarily chosen...
            portfolio_goal = Decimal(-numpy.pv(float(self.rate), nper, float(amount), when='beginning'))

            if self.portfolio.stocks >= portfolio_goal:
                #import pdb;pdb.set_trace()
                #harvest_amount = self.portfolio.stocks - portfolio_goal
                harvest_amount = self.portfolio.stocks / 4
                self.portfolio.sell_stocks(harvest_amount)
                self.portfolio.buy_bonds(harvest_amount)
                #print(self.current_age, " ", harvest_amount.to_integral_value(), " ", self.portfolio.stocks.to_integral_value(), "{%d}" % amount)
            else:
                #print(self.current_age, "[", portfolio_goal.to_integral_value(), "]", self.portfolio.stocks.to_integral_value(), "{%d}" % amount)
                pass

            amount = min(amount, self.portfolio.value)

            amount_bonds = min(amount, self.portfolio.bonds)
            amount_stocks = amount - amount_bonds
            self.portfolio.sell_bonds(amount_bonds)
            self.portfolio.sell_stocks(amount_stocks)
            
            amount = yield self.portfolio.empty_cash()

            self.current_age += 1
