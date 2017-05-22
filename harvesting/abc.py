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
            # Skip the harvesting if there's nothing to harvest.
            # This way we don't require every harvesting to handle the 0
            # edge case (even though they probably are fine?)
            if available_amount > 0:
                self.do_harvest(available_amount)
            amount = yield self.portfolio.withdraw_cash(available_amount)
