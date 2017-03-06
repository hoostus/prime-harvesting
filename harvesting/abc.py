import abc

class HarvestingStrategy(abc.ABC):
    def __init__(self, portfolio):
        self.portfolio = portfolio

    @abc.abstractmethod
    def do_harvest(self, amount):
        raise NotImplementedError("The method not implemented")

    def harvest(self):
        amount = yield
        while True:
            available_amount = min(amount, self.portfolio.value)
            self.do_harvest(available_amount)
            amount = yield self.portfolio.withdraw_cash(amount)
