import abc
from decimal import Decimal
from adt import AnnualChange, PortfolioSnapshot, YearlyResults
import adt

class WithdrawalStrategy(abc.ABC):
    def __init__(self, portfolio, harvest_strategy):
        self.portfolio = portfolio
        self.harvest = harvest_strategy
        self.cumulative_inflation = Decimal('1.0')

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError("The method not implemented")

    @abc.abstractmethod
    def next(self):
        raise NotImplementedError("The method not implemented")

    def withdrawals(self):
        """
        Calling this method creates a generator that can be used to loop.
        See simulate.withdrawals for an example of it in usage.
        """

        # Perform our first withdrawal manually by calling *start*
        # Subsequent iterations will call *next* which can update internal
        # state of the withdrawal strategy.
        
        # first we capture the current state of the portfolio
        portfolio_pre = adt.snapshot_portfolio(self.portfolio)

        # then we calculate our first withdrawal and actually withdraw it from the portfolio
        withdrawal = self.start()
        actual_withdrawal = self.harvest.send(withdrawal)

        # then we ask our controller the send us the first AnnualChange data (inflation, equity returns, etc)
        change = yield

        # Finally we've got everything in place to just iterate happily...
        while True:
            results = self.update_world(change, portfolio_pre, actual_withdrawal)
            change = yield results

            portfolio_pre = adt.snapshot_portfolio(self.portfolio)
            withdrawal = self.next()
            actual_withdrawal = self.harvest.send(withdrawal)

    def update_world(self, change, portfolio_pre, withdrawal):
        assert isinstance(change, AnnualChange)
        assert isinstance(portfolio_pre, PortfolioSnapshot)

        # Because withdrawals happen at the *beginning* of the year, we have to
        # calculate the real withdrawal value *before* we apply the current year's inflation
        withdrawal_deflated = withdrawal / self.cumulative_inflation

        # then we apply that to our portfolio & capture the updated state of the portfolio
        self.current_inflation = change.inflation
        self.cumulative_inflation *= (1 + change.inflation)
        (p_gains, p_val_pre, p_val_post) = self.portfolio.adjust_returns(change)
        portfolio_post = adt.snapshot_portfolio(self.portfolio)

        # Now we can finally report this year's activity to our controller

        # We need to avoid DivisionByZero in cases where the portfolio is exhausted
        if portfolio_pre.value_n == 0:
            withdraw_pct_cur = 0
        else:
            withdraw_pct_cur = withdrawal / portfolio_pre.value_n

        return YearlyResults(
            returns_n = p_gains,
            returns_r = ((1+p_gains) / (1+self.current_inflation)) - 1,
            withdraw_n = withdrawal,
            withdraw_r = withdrawal_deflated,
            withdraw_pct_cur = withdraw_pct_cur,
            withdraw_pct_orig = withdrawal_deflated / self.portfolio.starting_value,
            portfolio_pre = portfolio_pre,
            portfolio_post = portfolio_post
        )