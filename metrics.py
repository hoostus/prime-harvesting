from decimal import Decimal
import decimal
import operator
import functools
import numpy
import builtins
import math
from scipy.stats import gamma

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

    # We can never take out more than the portfolio or less than 0.
    n = min([n, pv])
    n = max([n, 0])

    return Decimal(n)

def prod(x):
    return functools.reduce(operator.mul, x, 1)

def hreff_cew_floor(floor, cashflows, epsilon=30, gamma=5):
    """ This is CEW-with-a-floor that McClung defines for use
    in HREFF.

    >>> from decimal import Decimal as D
    >>> ns = [6.1, 5, 4.3, 3.6, 4, 4.6,
    ... 4.5, 5.6, 6.4, 4.1, 4.9, 4.9, 4.3,
    ... 3.5, 3.4, 3.8, 4.3, 5.7, 3.8, 3.5,
    ... 3.5, 3.9, 4.7, 5.6, 5.8, 5.4, 8.2,
    ... 8.9, 8.8, 7.2, 9.2, 8.8, 9.1, 9.8,
    ... 7.7, 8.7, 8.5, 10, 7.3, 7.3]
    >>> float(hreff_cew_floor(D(2), [D(n) for n in ns]))
    5.683344625814626
    """
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
    return Decimal(x)

def hreff(withdrawals, returns, floor=Decimal('.03'), gamma=5):
    ''' Harvesting-Rate Efficiency (HREFF)

    HREFF is defined in Living Off Your Money (2016) by McClung's. It is a variant
    of WER with the addition of a withdrawal floor and penalties when annual
    withdrawals go below that.
    '''

    # The above functions expect the percentages to be expressed as 5.6 instead of 0.056
    # so we need to convert back and forth
    cew = hreff_cew_floor(floor*100, [w*100 for w in withdrawals], gamma=gamma)
    cew /= 100
    return cew / ssr(returns)

def wer(withdrawals, returns, fudge=Decimal('.0001')):
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
    s = ssr([n + fudge for n in returns])
    return c / s


def ssr(r):
    ''' Sustainable Spending Rate given a known sequence of returns

        Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
        by Blanchett, Kowara, Chen (among many other places; they did not invent it)
        https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf

        In http://www.gummy-stuff.org/sensible_withdrawals.htm#MAGIC gummy calls this the Magic Formula

        In "The Perfect Withdrawal Amount" by Suarez, Suarez, and Waltz they point out
        that the SSR is a measure of sequence of return risk. For a given set of returns
        a lower SSR means you had a worse sequence. Early bad returns are multiplied
        more often, reducing the overall SSR.

        >>> ssr([.04] * 30)
        0.05560586455159746
        >>> ssr([-.20, .15, .15, 0, .30] * 6)
        0.061263512947893395
        >>> ssr([])
        1.0
        >>> ssr([.04])
        1.0
    '''

    def ssr_seq(r):
        if len(r) == 0: return 1
        else:
            denom = prod(map(lambda x: x + 1, r))
            return (1 / denom) + ssr_seq(r[1:])

    # skip the final year of returns (since you have withdrawn the entire portfolio
    # at the beginning of the year, knowing that you will die this year)
    r_r = list(reversed(r[:-1]))
    return 1 / ssr_seq(r_r)

def pwa_cumulative_return(returns):
    return functools.reduce(operator.mul, (x+1 for x in returns))

def pwa_sequence_factor(returns):
    return functools.reduce(operator.add,
        (functools.reduce(operator.mul,
            (x+1 for x in returns[y:])) for y in range(len(returns))))

def pwa(start_balance, end_balance, returns):
    '''
    From "The Perfect Withdrawal Amount" by Suarez, Suarez, and Walz (2014)

    This is actually a generalisation of the ssr (above). You can pass in a starting
    amount and a desired finishing amount.

    This corresponds to Equation 3 in their paper.

    Note that unlike ssr, this doesn't return a percentage of the portfolio to withdraw,
    it returns a dollar amount.

    >>> pwa(1000000, 0, [.04] * 30)
    55605.864551597464
    >>> pwa(1000000, 0, [-.20, .15, .15, 0, .30] * 6)
    61263.512947893374
    '''
    return (start_balance * pwa_cumulative_return(returns) - end_balance) / pwa_sequence_factor(returns)

def cew(cashflows, gamma = Decimal('4.0')):
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

    >>> from decimal import Decimal as D
    >>> ns = [6.1, 5, 4.3, 3.6, 4, 4.6,
    ... 4.5, 5.6, 6.4, 4.1, 4.9, 4.9, 4.3,
    ... 3.5, 3.4, 3.8, 4.3, 5.7, 3.8, 3.5,
    ... 3.5, 3.9, 4.7, 5.6, 5.8, 5.4, 8.2,
    ... 8.9, 8.8, 7.2, 9.2, 8.8, 9.1, 9.8,
    ... 7.7, 8.7, 8.5, 10, 7.3, 7.3]
    >>> float(cew([D(n) for n in ns]))
    4.662420649169921
    '''

    #assert 0 not in cashflows, "Having a zero in the cashflows breaks CEW. 0 found at index %d" % cashflows.index(0)

    # The gamma = 4 was
    # chosen somewhat arbitrarily by Blanchett et al who point out that
    # the final results aren't very sensitive to this number (i.e. changing it to
    # 2 doesn't affect the final numbers very much)

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

    >>> gompertz(65, 70)
    0.9603531460340051
    >>> gompertz(65, 70, False)
    0.9332099343866791
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

# I got this from "Alpha, Beta, and Now Gamma" from Blanchett et al
def gompertz_couple(current_age, live_to):
    female = gompertz(current_age, live_to, female=True)
    male = gompertz(current_age, live_to, female=False)

    return male + female - (male * female)
        

def probability_of_ruin(return_mean, return_stddev, life_expectancy, withdrawal_pct):
    """
    Milevsky and Robinson's Stochastic Present Value from "A sustainable
    spending rate without simulation" (2005)

    In "A Gentle Introduction to the Calculus of Retirement Income" Milevsky
    calls this the "risk quotient"

    real_return: the real return of the portfolio (e.g. .07)
    std_dev: the volatility of the portfolio (e.g. .20)
    life_expectancy: the median remaining lifespan. i.e. what 50% of the population
        will live to. (e.g. 23)
    mortality_rate: the rate of dying every year (e.g. .0247)

    >>> probability_of_ruin(.07, .20, 28.1, .05)
    0.26785503502422264
    >>> probability_of_ruin(.0520, .1182, 22.30, .04)
    0.097782639821254749
    >>> probability_of_ruin(.0470, .1382, 22.30, .04)
    0.15435694850153159
    >>> probability_of_ruin(.049, .10, 22.30, .04)
    0.089454318224481758
    """
    mortality_rate = math.log(2) / life_expectancy
    alpha = ((2 * return_mean) + (4 * mortality_rate))
    alpha /= (return_stddev * return_stddev) + mortality_rate
    alpha -= 1

    beta = (return_stddev * return_stddev) + mortality_rate
    beta /= 2

    return gamma.cdf(withdrawal_pct, alpha, scale=beta)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
