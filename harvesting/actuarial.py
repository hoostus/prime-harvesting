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

class ActuarialHarvesting(HarvestingStrategy):
    def __init__(self, portfolio, starting_age=65, final_age=100):
        super().__init__(portfolio)
        self.current_age = starting_age
        self.final_age = final_age

    def harvest(self):
        amount = yield
        while True:
            # In order to get rid of the memory effect, the parameters to PV
            # have to independent of *when* you retire. But they can use current information

            # Just using a constant rate, like the historical rate of return
            # on equities feels wrong.
            # Use the Constant 10 Year Treasury Yield? (as a discount rate of something "safe"?)
            # Use E/P? (As a proxy for forecasting future stock returns?)
            # What to do about real, diversified portfolios?
            rate = .05
            nper = self.final_age - self.current_age
            portfolio_goal = numpy.pv(rate, nper, float(amount), when='beginning')

            if self.portfolio.stocks >= portfolio_goal:
                # Dividing the NPER by 4 is pretty arbitrary...
                harvest_amount = numpy.pv(rate, nper/4, float(amount), when='beginning')
                harvest_amount = min(harvest_amount, self.portfolio.stocks)
                self.portfolio.sell_stocks(harvest_amount)
                self.portfolio.buy_bonds(harvest_amount)

            amount = max(amount, self.portfolio.value)
            self.portfolio.sell_bonds(amount)
            
            amount = yield self.portfolio.empty_cash()

            self.age += 1