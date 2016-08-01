from decimal import Decimal
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

def prod(x):
    return functools.reduce(operator.mul, x, 1)

def hreff(withdrawals, returns):
    ''' Harvesting-Rate Efficiency (HREFF)

    HREFF is defined in Living Off Your Money (2016) by McClusky. It is a variant
    of WER with the addition of a withdrawal floor and penalties when annual
    withdrawals go below that.
    '''
    def cew_floor(cashflows, floor=Decimal('0.03')):
        gamma = Decimal('5.0')
        epsilon = 30

        def f(x):
            if x <= floor:
                return x - floor
            else:
                return x - (floor /
                            ( 1 +
                             ( epsilon * pow((x - floor), 3))))


        def sigma(c):
            return pow(f(c), 1/gamma)

        constant_factor = Decimal('1.0') / len(cashflows)
        base = constant_factor * sum(map(sigma, cashflows))
        return pow(base, gamma)

    return cew_floor(withdrawals) / ssr(returns)

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
