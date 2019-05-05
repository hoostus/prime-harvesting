import collections

AnnualChange = collections.namedtuple('AnnualChange', ['year', 'stocks', 'bonds', 'inflation'])
AnnualHarvest = collections.namedtuple('AnnualHarvest', ['change', 'withdrawal'])

PortfolioSnapshot = collections.namedtuple('PortfolioSnapshot',
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

YearlyResults = collections.namedtuple('YearlyResults',
[
    'returns_n',
    'returns_r',
    'withdraw_n',
    'withdraw_r',
    'withdraw_pct_cur',
    'withdraw_pct_orig',
    'portfolio_pre', # beginning of year, before withdrawals
    'portfolio_post', # end of year, after withdrawals & market returns
])
