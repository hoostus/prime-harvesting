from accumulation import N_80_RebalanceAccumulation
from harvesting import PrimeHarvesting
from withdrawal import EM
from portfolio import Portfolio
from adt import YearlyResults
import market

from decimal import Decimal
import pandas
import numpy

def withdrawals(series,
                portfolio=(600_000, 400_000),
                years=40,
                harvesting=PrimeHarvesting,
                withdraw=EM):
    portfolio = Portfolio(portfolio[0], portfolio[1])
    harvest_g = harvesting(portfolio).harvest()
    # You have to send None to a just-started generator.
    harvest_g.send(None)
    withdraw_g = withdraw(portfolio, harvest_g).withdrawals()
    withdraw_g.send(None)

    annual = []

    for _, d in zip(range(years), series):
        data = withdraw_g.send(d)
        annual.append(data)
    return annual

def calc_lens(harvesting, withdraw, years, lens, portfolio=(600_000, 400_000)):
    MARKET = market.Returns_US_1871()
    end_year = 2018 - years + 1
    series = pandas.Series(index=numpy.arange(MARKET.start_year, end_year))

    for start in range(MARKET.start_year, end_year):
        annual_data = withdrawals(MARKET.iter_from(start),
                                           portfolio=portfolio,
                                           years=years,
                                           harvesting=harvesting,
                                           withdraw=withdraw)
        d = lens(annual_data)
        series.loc[start] = d
    return series

# Provide alias to legacy name.
simulate_withdrawals = withdrawals

# Numbers from http://www.wsj.com/articles/how-to-think-about-risk-in-retirement-1417408070
# Withdraw 50,000 the first 5 years and then 21,700 thereafter
# the Risk Portfolio is all stock
# the LMP is TIPS/corporate bonds (Bernstein assumes 1% real returns)
def simulate_lmp(series, portfolio=(750000,250000), years=40, lmp_real_annual=Decimal('.01')):
    count = 0
    annual = []
    cumulative_inflation = 1

    lmp = portfolio[0]
    rp = portfolio[1]

    for (year, stocks, bonds, inflation) in series:
        if count > years:
            break

        if count < 5:
            amount = 50000
        else:
            amount = 21700

        cumulative_inflation *= (1 + inflation)

        amount *= cumulative_inflation

        previous_portfolio_amount = rp + lmp
        rp *= (1 + stocks)
        lmp_gains = lmp_real_annual + inflation
        lmp *= (1 + lmp_gains)

        gains = (rp + lmp) - previous_portfolio_amount

        if amount < lmp:
            lmp -= amount
        else:
            a1 = amount - lmp
            lmp = 0
            if rp > a1:
                rp -= a1
            else:
                amount = rp
                rp = 0

        annual.append(YearlyResults(
            year = 0,
            returns = gains,
            withdraw_n = amount,
            withdraw_r = amount / cumulative_inflation,

            withdraw_pct_cur = amount / (rp + lmp),
            withdraw_pct_orig = (amount / cumulative_inflation) / (portfolio[0] + portfolio[1]),

            portfolio_n = rp + lmp,
            portfolio_r = (rp + lmp) / cumulative_inflation,

            portfolio_bonds = lmp,
            portfolio_stocks = rp
        ))

        count += 1
    return annual

# Accumulation phase of saving for retirement.  Add funds to portfolio at the
# end of every year, never withdrawing from the portfolio.  The amount added
# each year grows with inflation.
def simulate_accumulation(series,
                          portfolio=(0, 0),
                          years=35,
                          annual_inflow=25000,
                          accumulation=N_80_RebalanceAccumulation):
    portfolio = Portfolio(portfolio[0], portfolio[1])
    strategy = accumulation(portfolio).accumulate()
    strategy.send(None)
    annual = []

    for _, change in zip(range(years), series):
        gains, _, _ = portfolio.adjust_returns(change)
        strategy.send(annual_inflow)

        annual.append(YearlyResults(
            year = 0,
            returns = gains,
            withdraw_n = 0,
            withdraw_r = 0,

            withdraw_pct_cur = 0,
            withdraw_pct_orig = 0,

            portfolio_n = portfolio.value,
            portfolio_r = portfolio.real_value,
            portfolio_bonds = portfolio.bonds,
            portfolio_stocks = portfolio.stocks
        ))

        annual_inflow *= 1 + change.inflation
    return annual
