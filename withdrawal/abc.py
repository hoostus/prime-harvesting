import abc
from decimal import Decimal
from adt import report, AnnualChange

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
        withdrawal = self.start()

        actual_withdrawal = self.harvest.send(withdrawal)
        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            # Update the world.
            self.current_inflation = change.inflation
            self.cumulative_inflation *= (1 + change.inflation)
            previous_portfolio_amount = self.portfolio.value
            (gains, _, _) = self.portfolio.adjust_returns(change)

            # Now we can make our next withdrawal.
            withdrawal = self.next()

            actual_withdrawal = self.harvest.send(withdrawal)
            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)
