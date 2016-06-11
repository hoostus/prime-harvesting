from decimal import Decimal

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

def wer(withdrawals, returns):
    ''' Withdrawal Efficiency Rate

        Given a list-liek of withdrawals and a list-like of actual returns over that same
        period, calculate how 'efficient' the withdrawals were.

        This is done by calculating the Sustainable

        Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
        by Blanchett, Kowara, Chen
        https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf
    '''

    return cew(withdrawals) / ssr(returns)


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
    # at the beginning of the year,
    # knowing that you will die this year)
    r_r = list(reversed(r[:-1]))
    return Decimal('1') / ssr_seq(r_r)

def cew(cashflows):
    ''' Constant Equivalent Withdrawals
    Given a sequence of withdrawals, calculate what the constant-equivalent would be.

    Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
    by Blanchett, Kowara, Chen
    https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf
    '''

    # chosen somewhat arbitrarily by Blanchett et al point out that
    # the final results aren't very sensitive to this number (i.e. changing it to
    # 2 doesn't affect the final numbers very much)
    gamma = Decimal('4.0')

    def sigma(c):
        return pow(c, -gamma) / gamma

    constant_factor = Decimal('1.0') / len(cashflows) * gamma
    base = constant_factor * sum(map(sigma, cashflows))
    return pow(base, -1/gamma)
