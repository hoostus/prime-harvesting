from harvesting import PrimeHarvesting
from withdrawal import EM
from portfolio import Portfolio
from decimal import Decimal
from adt import YearlyResults

def simulate_withdrawals(series,
                            portfolio=(600000, 400000),
                            years=40,
                            harvesting=PrimeHarvesting,
                            withdraw=EM):
    portfolio = Portfolio(portfolio[0], portfolio[1])
    strategy = harvesting(portfolio).harvest()
    strategy.send(None)
    withdrawal_strategy = withdraw(portfolio, strategy).withdrawals()
    annual = []

    # Withdrawals happen at the start of the year, so the first time
    # we don't have any performance data to send them....
    data = withdrawal_strategy.send(None)
    annual.append(data)
    years -= 1

    for _, d in zip(range(years), series):
        data = withdrawal_strategy.send(d)
        annual.append(data)
    return annual

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
