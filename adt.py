import collections

AnnualChange = collections.namedtuple('AnnualChange', ['year', 'stocks', 'bonds', 'inflation'])
AnnualHarvest = collections.namedtuple('AnnualHarvest', ['change', 'withdrawal'])

# There is one weirdness with this:
# Everything is reported as of the beginning of the year...
# ...except for the returns, which are measured as of the end of the year

PortfolioSnapshot = collection.namedtuple('PortfolioSnapshot',
[
    'value_n',
    'value_r',
    'bonds',
    'stocks',
    'cash',
])

def snapshot_portfolio(portfolio):
    return PortfolioSnapshot(
        value_n = portfolio.value,
        value_r = portfolio.real_value,
        bonds = portfolio.bonds,
        stocks = portfolio.stocks,
        cash = portfolio.cash,
    )

YearlyResults_v2 = collection.namedtuple('YearlyResults_v2',
[
    'returns',
    'withdraw_n',
    'withdraw_r',
    'withdraw_pct_cur',
    'withdraw_pct_orig',
    'portfolio_boy', # beginning of year
    'portfolio_eoy', # end of year
])

YearlyResults = collections.namedtuple('YearlyResults',
    ['returns', # annual return of the portfolio (measured at END of year)
     'withdraw_n', # withdrawal (nominal) at BEGIN of year
     'withdraw_r', # withdrawal (real) at BEGIN of year
     'withdraw_pct_cur', # withdrawal as percent of current portfolio
     'withdraw_pct_orig', # inflation-adjusted withdrawal as percent of original portfolio
     'portfolio_n', # portfolio (nominal) at BEGIN of year
     'portfolio_r', # portfolio (real) at BEGIN of year
     'portfolio_bonds', # dollar amount (nominal) of portfolio in bonds
     'portfolio_stocks' # dollar amount (nominal) of portfolio in stocks
     ])

def report(portfolio, withdrawal, current_gains):
    # If the portfolio has gone to 0 then we need to handle it slightly differently
    # to avoid a division by zero error
    if portfolio.value + withdrawal == 0:
        withdraw_pct_cur = 0
    else:
        withdraw_pct_cur = withdrawal / (portfolio.value + withdrawal)
   
    return YearlyResults(
        returns = current_gains,

        withdraw_n = withdrawal,
        withdraw_r = withdrawal / portfolio.inflation,
        withdraw_pct_cur = withdraw_pct_cur,
        withdraw_pct_orig = (withdrawal / portfolio.inflation) / portfolio.starting_value,

        portfolio_n = portfolio.value,
        portfolio_r = portfolio.real_value,
        portfolio_bonds = portfolio.bonds,
        portfolio_stocks = portfolio.stocks
    )
