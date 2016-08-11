from decimal import Decimal
import decimal
import operator
import functools
import numpy
import builtins
import math

# numpy can't handle Decimal so we have this helper function
def average(xs):
    return numpy.average([float(x) for x in xs])
def mean(xs):
    return numpy.mean([float(x) for x in xs])
def median(xs):
    return numpy.median([float(x) for x in xs])
def min(xs):
    return builtins.min([float(x) for x in xs])
def max(xs):
    return builtins.max([float(x) for x in xs])

# Yet another helper function to deal with float/Decimal conversion issues :(
# I feel like I should have just used float...
def pmt(rate, nper, pv):
    """ We always assume a future value of $0 and withdrawals at the
    beginning of the period. """

    # We can get passed in some non-sensical numbers. This could be do
    # to a loop that assumes a final age of 110 but the person unexpectedly
    # live to 111. Yes, the higher level loop should handle that but....
    if nper < 1:
        return pv

    n = -numpy.pmt(float(rate), nper, float(pv), 0, 1)
    n = math.floor(n)
    return Decimal(n)


def prod(x):
    return functools.reduce(operator.mul, x, 1)

def hreff(withdrawals, returns, floor=Decimal('.03')):
    ''' Harvesting-Rate Efficiency (HREFF)

    HREFF is defined in Living Off Your Money (2016) by McClung's. It is a variant
    of WER with the addition of a withdrawal floor and penalties when annual
    withdrawals go below that.
    '''

    gamma = 5

    def cew_floor(cashflows):
        epsilon = 30

        def f(x):
            if x <= floor:
                return x - floor
            else:
                return (x -
                (floor /
                    (1 +
                        (epsilon *
                            (x - floor) ** 3)
                    )
                ))

        # by default, python doesn't handle negative numbers and odd-fractional
        # exponents properly. I don't know why. Anyway, this does the right thing.
        def nth_root(x, n):
            return math.copysign(math.pow(abs(x), 1.0/n), x)

        def sigma(x):
            # Decimals can't do fractional powers so
            # convert to a float, which can
            f_x = float(f(x))
            n = nth_root(f_x, gamma)
            return n

        x = average(map(sigma, cashflows))
        x = pow(x, gamma)
        return Decimal(x)/100

    # The above functions expect the percentages to be expressed as 5.6 instead of 0.056
    # so we need to convert back and forth
    return cew_floor([w*100 for w in withdrawals]) / ssr(returns)

def wer(withdrawals, returns, fudge=Decimal('.001')):
    ''' Withdrawal Efficiency Rate

        Given a list-like of withdrawals and a list-like of actual returns over that same
        period, calculate how 'efficient' the withdrawals were.

        The withdrawals list is expected to be "percent of original portfolio size"

        If there are any zeroes in the withdrawals, then the CEW calculation blows up which throws everything
        off. So the 'fudge' is there to ensure there is at least a very small number.

        Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
        by Blanchett, Kowara, Chen
        https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf

    '''
    c = cew([n + fudge for n in withdrawals])
    s = ssr(returns) + fudge
    if c > s:
        from pprint import pprint
        #import pdb;pdb.set_trace()
    #assert c < s, "Found super-optimal solution, which is impossible. CEW = %s. SSR = %s." % (c, s)
    return c / s


def ssr(r):
    ''' Sustainable Spending Rate given a known sequence of returns

        Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
        by Blanchett, Kowara, Chen
        https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf
    '''

    def ssr_seq(r):
        if len(r) == 0: return 1
        else:
            denom = prod(map(lambda x: x + 1, r))
            return (1 / denom) + ssr_seq(r[1:])

    # skip the final year of returns (since you have withdrawn the entire portfolio
    # at the beginning of the year, knowing that you will die this year)
    r_r = list(reversed(r[:-1]))
    return Decimal('1') / ssr_seq(r_r)

def cew(cashflows):
    ''' Constant Equivalent Withdrawals
    Given a sequence of withdrawals, calculate what the constant-equivalent would be.

    Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
    by Blanchett, Kowara, Chen
    https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf

    From a forum discussion (https://www.bogleheads.org/forum/viewtopic.php?f=10&t=120430&start=600#p2940181):

    "Economists seem divided on what is a fair value to use for the coefficient of relative risk aversion.
    Based on my readings many seem to think it is the range 1 to 3 based on people's attitudes towards risk,
    however there are some who look at the asset allocation decisions people actually make that claim it must
    be 10 or more as a result."
    '''

    assert 0 not in cashflows, "Having a zero in the cashflows breaks CEW. 0 found at index %d" % cashflows.index(0)

    # chosen somewhat arbitrarily by Blanchett et al who point out that
    # the final results aren't very sensitive to this number (i.e. changing it to
    # 2 doesn't affect the final numbers very much)
    gamma = Decimal('4.0')

    def sigma(c):
        return pow(c, -gamma) / gamma

    constant_factor = Decimal('1.0') / len(cashflows) * gamma
    base = constant_factor * sum(map(sigma, cashflows))
    return pow(base, -1/gamma)

def gompertz(current_age, live_to, female=True):
    """
    This calculates the probability of survival to age 'live_to',
    conditional on a life at age 'current_age'. female is boolean.

    This comes from Blanchett's paper Simple Formulas for
    Complex Withdrawal Strategies.

    The parameters are based on the Annuity 2000 table, calculated
    by Blancett in his paper, which means they are biased towards healthy
    people with extra longevity.
    """

    if female:
        model_lifespan = 91
        dispersion_coeff = 8.88
    else:
        model_lifespan = 88
        dispersion_coeff = 10.65

    q = math.exp(
            math.exp((current_age - model_lifespan) / dispersion_coeff)
            * (1 - math.exp((live_to - current_age) / dispersion_coeff))
    )
    return q

def probability_of_ruin(return_mean, return_stddev, mortality_rate, withdrawal_pct):
    """
    Milevsky and Robinson's Stochastic Present Value from "A sustainable
    spending rate without simulation" (2005)

    real_return: the real return of the portfolio (e.g. .07)
    std_dev: the volatility of the portfolio (e.g. .20)
    mortality_rate: the rate of dying every year (e.g. .0247)

    You can calculate an implied mortality rate by =log(2)/median_life_span.
    For a 50-year old, assume the median life span is another 28.1 years. Then
    the implied mortality rate =log(2)/28.1 = .0247
    """
    alpha = ((2 * return_mean) + (4 * mortality_rate))
    alpha /= (return_stddev * return_stddev) + mortality_rate
    alpha -= 1

    beta = (return_stddev * return_stddev) + mortality_rate
    beta /= 2

    # given alpha = 2.690880989, beta = 0.03235, mortality_rate = 0.0247, withdrawal_pct = .05
    # this should return 0.267590954
    # gamma.dist(withdrawal_pct, alpha, beta)
    # I can't figure out how to use scipy to emulate this Excel function :(
