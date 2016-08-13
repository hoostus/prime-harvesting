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

        # I honestly can't figure out what is right here.
        # Just using lognormvariate directly gives you numbers like 0.93 and 1.26
        # Do you subtract one from that to get the percentage change?
        # Sounds reasonable enough.
        # But then you don't seem to get bad market outcomes nearly often enough.
        # As in, after 10,000 simulated years there are only 16 instances of a 40%
        # decline. Yet in the 20th century we had it happen 3 times in ~100 years.
        r = random.lognormvariate(self.mean, self.stddev) - 1

        # By randomly taking a log here we get 64 out of 10,000 being a 40% decline.
        #r = math.log(random.lognormvariate(self.mean, self.stddev))

        # This math comes from the wikipedia article on LogNormal
        # But...it doesn't generate the kinds of numbers you expect
        """
        mu = math.log(
            self.mean /
            math.sqrt(1 + 
                (self.stddev ** 2)/(self.mean ** 2))
        )
        sigma = math.sqrt(
            1 + (self.stddev ** 2)/(self.mean ** 2)
        )
        r = random.lognormvariate(mu, sigma)
        """

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
# They are an interesting idea but the actual numbers don't seem
# different enough to bother with. The 100-year half life and the
# 10-year half life seem extremely similar

# Pye in "When Should Retirees Retrench?" (2008)
# has a suggestion for increasing the chances of a bear
# market (which makes it closer to the historical reality
# than normal distributions give you)
# Instead of using a constant standard deviation, mix it up.
# "To keep it simple, suppose that each year there is a .75 chance
# that the standard deviation is .08 and a .25 chance that it is .30"
class PyeBearReturns:
    def __init__(self):
        self.mean = .0638

    def random_year(self):
        if random.randint(1, 100) < 75:
            stddev = .08
        else:
            stddev = .30
        r = random.lognormvariate(self.mean, stddev) - 1
        r = Decimal(r)

        return AnnualChange(year=0, stocks=r, bonds=r, inflation=Decimal(0))
