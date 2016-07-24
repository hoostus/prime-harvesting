import collections

AnnualChange = collections.namedtuple('AnnualChange', ['year', 'stocks', 'bonds', 'inflation'])
AnnualHarvest = collections.namedtuple('AnnualHarvest', ['change', 'withdrawal'])

YearlyResults = collections.namedtuple('YearlyResults',
    ['returns',
     'withdraw_n', 'withdraw_r', 'withdraw_pct_cur', 'withdraw_pct_orig',
     'portfolio_n', 'portfolio_r', 'portfolio_bonds', 'portfolio_stocks'])

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
