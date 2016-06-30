from numpy.random import lognormal
from decimal import Decimal
from adt import AnnualChange

class LogNormalReturns:
    def __init__(self, mean, sigma):
        self.mean = mean
        self.sigma = sigma

    def random_year(self):
        ''' This is the same method name as in market.US_1871_Returns...which
        allows this to be a drop-in replacement for that when simulating data '''
        r = lognormal(self.mean, self.sigma) - 1
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