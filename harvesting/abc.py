import abc

class HarvestingStrategy(abc.ABC):
    def __init__(self, portfolio):
        self.portfolio = portfolio

    @abc.abstractmethod
    def harvest(self, amount):
        raise NotImplementedError("The method not implemented")
