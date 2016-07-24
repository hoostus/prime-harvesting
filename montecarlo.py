import math
import random
from decimal import Decimal
from adt import AnnualChange

class LogNormalReturns:
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def random_year(self):
        ''' This is the same method name as in market.US_1871_Returns...which
        allows this to be a drop-in replacement for that when simulating data '''
        
        r = math.log(random.lognormvariate(self.mean, self.stddev))
        r = Decimal(r)

        return AnnualChange(year=0, stocks=r, bonds=r, inflation=Decimal(0))

# Numbers come from Blanchett et al. (2012)
# Index is the percentage of equities
historical = {
    0:  LogNormalReturns(.0231, .0483),
    10: LogNormalReturns(.0289, .0494),
    20: LogNormalReturns(.0342, .0572),
    30: LogNormalReturns(.0392, .0696),
    40: LogNormalReturns(.0438, .0845),
    50: LogNormalReturns(.0481, .1009),
    60: LogNormalReturns(.0520, .1182),
    70: LogNormalReturns(.0555, .1360),
    80: LogNormalReturns(.0586, .1542),
    90: LogNormalReturns(.0614, .1727),
    100:LogNormalReturns(.0638, .1915)
}
# From the paper..."For conservative forecasting purposes,
# the portfolio return was reduced by 50 bps and standard
# deviations were increased by 200 bps
conservative = {
    0:  LogNormalReturns(.0181, .0683),
    10: LogNormalReturns(.0239, .0694),
    20: LogNormalReturns(.0292, .0772),
    30: LogNormalReturns(.0342, .0896),
    40: LogNormalReturns(.0388, .1045),
    50: LogNormalReturns(.0431, .1209),
    60: LogNormalReturns(.0470, .1382),
    70: LogNormalReturns(.0505, .1560),
    80: LogNormalReturns(.0536, .1742),
    90: LogNormalReturns(.0564, .1927),
    100:LogNormalReturns(.0588, .2115)
}

# From "Inverted Withdrawals and the Sequence of Returns Bonus" (Walton 2016) he quotes numbers
# from Research Associates
RA_high_vol = LogNormalReturns(.059, .13)
RA_medium_vol = LogNormalReturns(.049, .10)
RA_low_vol = LogNormalReturns(.033, .065)

# gordoni's "weighted historical returns"
# https://www.bogleheads.org/forum/viewtopic.php?f=10&t=193615
weighted_historical = """
                 arith stdev  stderr  geom
fixed 1970-2015  7.38% 16.93% 2.50%  5.91%
fixed 1927-2015  8.64% 19.51% 2.07%  6.78%
fixed 1872-2015  8.41% 18.19% 1.52%  6.78%
half-life 10     8.09% 16.28% 2.97%  6.62%
half-life 20     8.16% 17.03% 2.20%  6.63%
half-life 30     8.23% 17.49% 1.89%  6.66%
half-life 40     8.28% 17.73% 1.74%  6.67%
half-life 50     8.31% 17.86% 1.67%  6.69%
half-life 60     8.32% 17.94% 1.63%  6.70%
half-life 70     8.34% 17.98% 1.60%  6.71%
half-life 80     8.35% 18.01% 1.58%  6.71%
half-life 90     8.35% 18.03% 1.57%  6.72%
half-life 100    8.36% 18.05% 1.56%  6.72%
"""
