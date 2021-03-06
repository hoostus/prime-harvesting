import math
import random
from decimal import Decimal
from adt import AnnualChange
import pandas

def clip(x, min, max):
    return sorted((min, x, max))[1]

class LowYieldsHighValuations:
    """
    This model comes from "Initial Conditions and Optimal
    Retirement Glidepaths" (2015) by Blanchett.

    It is similar to the LowYieldsAutoRegression but it also
    attempts to handle high valuations (that regress towards normal
    valuations)
    """

    a_cape = [
        13.61,
        14.87,
        10.62,
        11.10,
        10.45,
         6.20,
         6.69,
         9.61,
        10.41,
         9.28,
        10.21,
        10.21,
         8.04,
         5.57,
         6.76,
         6.00,
    ]
    a_cape = [n/100 for n in a_cape]

    b_cape = [
        -0.47,
        -0.54,
        -0.28,
        -0.31,
        -0.27,
        -0.01,
        -0.04,
        -0.22,
        -0.28,
        -0.21,
        -0.27,
        -0.27,
        -0.13,
         0.03,
        -0.05,
        0,
    ]
    b_cape = [n/100 for n in b_cape]

    estocks_stdev = [
        17.75,
        17.71,
        17.99,
        17.90,
        17.96,
        18.13,
        18.16,
        18.16,
        18.20,
        18.22,
        18.24,
        18.31,
        18.29,
        18.36,
        18.43,
        18.01,
    ]
    estocks_stdev = [n/100 for n in estocks_stdev]

    def __init__(self, initial_yield=.025, initial_cape = 27):
        self.initial_yield = initial_yield
        self.initial_cape = initial_cape

        self.y_prev = self.initial_yield
        self.year = 0

    def random_year(self):
        y_prev = self.y_prev

        ey = random.normalvariate(0, .0125)
        y_new = 0.225/100 + (0.95 * y_prev) + ey
        y_new = clip(y_new, .01, .10)

        ebond = random.normalvariate(0, .015)
        r_bonds = 0 + (1.0 * y_new) + (-8.0 * (y_new - y_prev)) + ebond
        # Blanchett doesn't provide min/max for r_bonds
        # I'll reuse the min/max from LowYieldsAutoRegression
        r_bonds = clip(r_bonds, -.15, .40)

        ebill = random.normalvariate(0, .01)
        r_bill = -.02 + y_new + 0.75 * (y_new - y_prev) + ebill
        r_bill = clip(r_bill, .01, .10)

        # the tables max out at 15 years...
        lookup_year = min(15, self.year)
        estocks = random.normalvariate(0, self.estocks_stdev[lookup_year])
        r_stocks = self.a_cape[lookup_year] + self.b_cape[lookup_year] * self.initial_cape + estocks
        # Blanchett doesn't provide min/max for r_stocks
        # I'll reuse the min/max from LowYieldsAutoRegression
        r_stocks = clip(r_stocks, -1, 2)

        einflation = random.normalvariate(0, .01)
        r_inflation = 0.0125 + (y_new - y_prev) + 0.5 * r_bill + einflation
        r_inflation = clip(r_inflation, -.05, .10)

        self.y_prev = y_new
        self.year += 1

        return AnnualChange(
            year=self.year,
            stocks=Decimal(r_stocks),
            bonds=Decimal(r_bonds),
            inflation=Decimal(r_inflation)
        )

    def __iter__(self):
        while True:
            yield self.random_year()

class LowYieldsAutoRegression:
    """
        This model (and the parameters used) are taken from
        "Low Bond Yields and Safe Portfolio Withdrawal Rates" (2013)
        by Blanchett, Finke, Pfau

        It starts with current low yields and slowly regresses back toward
        "normal" yields (of 5%). The other returns are based on the yield.

        When the paper came out yields were 2.5%, so that is the default.
        You can use something lower if you want. The yield is the Barclays
        Aggregate Bond Index (not just Treasuries!)
    """

    def __init__(self, initial_yield=2.5/100, logging=False):
        self.initial_yield = initial_yield
        self.logging = logging
        if self.logging:
            self.log = pandas.DataFrame(columns=['y_prev', 'y_new', 'rc', 'stocks', 'bonds', 'inflation'], dtype='float')

        self.y_prev = self.initial_yield
        self.year = 0


    # bond yield params
    ay = .269/100
    by = .949

    # cash total return params
    ac = -2.024/100
    bc = .978
    byc = .321

    coeffs = {
        #            ai            byi    bc   by_delta_i  e_std   min  max
        'bonds' : (.920/100,      .446,  .678, -3.714,  5.066/100, -.15, .40),
        'stocks' : (7.951/100,    .593, -.308, -4.221, 19.358/100,  -1,  2),
        'inflation' :(2.983/100, -.554,  .964,  1.012,  2.088/100, -.10, .20)
    }

    def random_year(self):
        y_prev = self.y_prev

        # first determine bond yields based on previous year
        ey = random.normalvariate(0, .009)
        y_new = self.ay + (self.by * y_prev)
        y_new += ey
        y_new = clip(y_new, .01, .10)

        delta_y = (y_new - y_prev)

        # now determine total returns for cash
        ec = random.normalvariate(0, .01)
        rc = self.ac + (self.bc * y_new) + (self.byc * delta_y)
        rc += ec
        rc = clip(rc, 0, .10)

        # now determine return for bonds, stocks, and inflation
        def calc_returns(ai, byi, bc, by_delta_i, e_stddev, min, max):
            ei = random.normalvariate(0, e_stddev)
            n = (
                ai +
                (bc * rc) +
                (byi * y_new) +
                (by_delta_i * delta_y)
            )
            n += ei
            return clip(n, min, max)

        rs = {}
        for k in self.coeffs:
            # Does this generate real or nominal returns for the stocks & bonds?
            rs[k] = calc_returns(*self.coeffs[k])

        if self.logging:
            self.log.loc[self.year] = (y_prev, y_new, rc, rs['stocks'], rs['bonds'], rs['inflation'])

        self.y_prev = y_new
        self.year += 1

        return AnnualChange(
            year=self.year,
            stocks=Decimal(rs['stocks']),
            bonds=Decimal(rs['bonds']),
            inflation=Decimal(rs['inflation'])
        )


    def __iter__(self):
        while True:
            yield self.random_year()

class NormalReturns:
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev
        self.year = 0

    def __iter__(self):
        while True:
            self.year += 1
            yield self.random_year()

    def random_year(self):
        r = random.normalvariate(self.mean, self.stddev)
        r = Decimal(r)
        return AnnualChange(year=self.year, stocks=r, bonds=r, inflation=Decimal(0))

class LogNormalReturns:
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev
        self.year = 0

    def __iter__(self):
        while True:
            self.year += 1
            yield self.random_year()

    def random_year(self):
        r = random.lognormvariate(self.mean, self.stddev) - 1
        r = Decimal(r)
        return AnnualChange(year=self.year, stocks=r, bonds=r, inflation=Decimal(0))

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

# Calculated directly from simba's spreadsheet using 1871-2015 data
# There are 101 elements. The index is the percentage of stocks.
# That is, simba_mean[15] gives you the mean return for a portfolio that is
# 15% S&P 500 and 85% intermediate treasuries.
#
# These are real, not nominal, numbers.
simba_mean = [
    0.024515862,
    0.025074952,
    0.025634041,
    0.026193131,
    0.026752221,
    0.02731131,
    0.0278704,
    0.02842949,
    0.028988579,
    0.029547669,
    0.030106759,
    0.030665848,
    0.031224938,
    0.031784028,
    0.032343117,
    0.032902207,
    0.033461297,
    0.034020386,
    0.034579476,
    0.035138566,
    0.035697655,
    0.036256745,
    0.036815834,
    0.037374924,
    0.037934014,
    0.038493103,
    0.039052193,
    0.039611283,
    0.040170372,
    0.040729462,
    0.041288552,
    0.041847641,
    0.042406731,
    0.042965821,
    0.04352491,
    0.044084,
    0.04464309,
    0.045202179,
    0.045761269,
    0.046320359,
    0.046879448,
    0.047438538,
    0.047997628,
    0.048556717,
    0.049115807,
    0.049674897,
    0.050233986,
    0.050793076,
    0.051352166,
    0.051911255,
    0.052470345,
    0.053029434,
    0.053588524,
    0.054147614,
    0.054706703,
    0.055265793,
    0.055824883,
    0.056383972,
    0.056943062,
    0.057502152,
    0.058061241,
    0.058620331,
    0.059179421,
    0.05973851,
    0.0602976,
    0.06085669,
    0.061415779,
    0.061974869,
    0.062533959,
    0.063093048,
    0.063652138,
    0.064211228,
    0.064770317,
    0.065329407,
    0.065888497,
    0.066447586,
    0.067006676,
    0.067565766,
    0.068124855,
    0.068683945,
    0.069243034,
    0.069802124,
    0.070361214,
    0.070920303,
    0.071479393,
    0.072038483,
    0.072597572,
    0.073156662,
    0.073715752,
    0.074274841,
    0.074833931,
    0.075393021,
    0.07595211,
    0.0765112,
    0.07707029,
    0.077629379,
    0.078188469,
    0.078747559,
    0.079306648,
    0.079865738,
    0.080424828,
]

simba_stddev = [
    0.079155997,
    0.078713748,
    0.078312607,
    0.077953211,
    0.077636139,
    0.077361911,
    0.077130984,
    0.076943748,
    0.076800523,
    0.076701555,
    0.076647016,
    0.076637,
    0.076671526,
    0.076750532,
    0.076873881,
    0.077041362,
    0.077252686,
    0.077507495,
    0.077805362,
    0.078145794,
    0.078528238,
    0.078952084,
    0.079416668,
    0.07992128,
    0.080465167,
    0.081047539,
    0.081667571,
    0.082324414,
    0.083017193,
    0.083745016,
    0.084506978,
    0.085302165,
    0.086129655,
    0.086988528,
    0.087877862,
    0.088796743,
    0.089744264,
    0.090719526,
    0.091721645,
    0.09274975,
    0.093802987,
    0.09488052,
    0.095981528,
    0.097105215,
    0.098250802,
    0.099417532,
    0.10060467,
    0.101811501,
    0.103037333,
    0.104281497,
    0.105543344,
    0.106822248,
    0.108117603,
    0.109428825,
    0.11075535,
    0.112096636,
    0.113452158,
    0.114821413,
    0.116203915,
    0.117599197,
    0.119006809,
    0.120426319,
    0.121857311,
    0.123299386,
    0.124752158,
    0.12621526,
    0.127688335,
    0.129171042,
    0.130663054,
    0.132164055,
    0.133673743,
    0.135191826,
    0.136718025,
    0.138252072,
    0.139793707,
    0.141342682,
    0.142898759,
    0.144461709,
    0.14603131,
    0.14760735,
    0.149189626,
    0.150777941,
    0.152372106,
    0.153971939,
    0.155577266,
    0.157187919,
    0.158803734,
    0.160424557,
    0.162050237,
    0.163680629,
    0.165315594,
    0.166954997,
    0.168598709,
    0.170246606,
    0.171898566,
    0.173554475,
    0.175214219,
    0.176877691,
    0.178544787,
    0.180215406,
    0.181889451,
]

class DMSLogNormalReturns:
    def __init__(self, dms_data):
        self.stocks_mean = dms_data['equities'][0] / 100
        self.stocks_stddev = dms_data['equities'][2] / 100
        self.bonds_mean = dms_data['bonds'][0] / 100
        self.bonds_stddev = dms_data['bonds'][2] / 100
        self.year = 0

    def __iter__(self):
        while True:
            self.year += 1
            yield self.random_year()

    def random_year(self):
        s = random.lognormvariate(self.stocks_mean, self.stocks_stddev) - 1
        s = Decimal(s)

        b = random.lognormvariate(self.bonds_mean, self.bonds_stddev) - 1
        b = Decimal(b)
        return AnnualChange(year=self.year, stocks=s, bonds=b, inflation=Decimal(0))
