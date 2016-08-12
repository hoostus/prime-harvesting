from decimal import Decimal
from .abc import WithdrawalStrategy
import math

class SimpleFormula(WithdrawalStrategy):
    """
    This comes from Blanchett's 'Simple Formulas to Implement Complex Withdrawal Strategies'
    https://www.onefpa.org/journal/Pages/Simple%20Formulas%20to%20Implement%20Complex%20Withdrawal%20Strategies.aspx
    """
    def __init__(self, portfolio, harvest_strategy, probability_of_success=.95, alpha=0, years=35):
        super().__init__(portfolio, harvest_strategy)

        # the target probability of success (i.e. "I want a 95% chance of succeeding")
        self.pos = probability_of_success

        # the alpha parameters allows you to include advisors fees and adjust
        # the capital market expectations; Blanchett used 10% for equities and
        # 4% for bonds.
        self.alpha = alpha

        # How long we expect the strategy to run for...
        self.years = years

    def _calc(self):
        rate = self.get_pct(self.years)
        return rate * self.portfolio.value

    def start(self):
        return self._calc()

    def next(self):
        # Update our internal state.
        self.years -= 1

        return self._calc()

    def rmd(self, years):
        return Decimal(1) / years

    def get_pct(self, years):
        if years < 1:
            # We failed :(
            return 0
        if years < 15:
            return self.rmd(years)
        else:
            return self.dynamic(years)

    def dynamic(self, years):
        """
        In the paper Blanchett lists the intercept at 0.195
        and the longevity coeff at 0.3701. But if you use those
        numbers in his formula you get a different result than
        what he discusses in the paper (you get a 3.17% withdrawal rate
        instead of a 3.15% withdrawal rate for the scenario he first
        discusses).

        That confused me because I couldn't figure out why. But Blanchett
        also provides an Excel spreadsheet which implements the formula.
        In the spreadsheet he uses slightly different numbers for intercept
        and longevity. The numbers below come from the spreadsheet.

        Spreadsheet: http://www.davidmblanchett.com/tools
        """
        intercept = 0.19477105724498
        longevity_coeff = .0370089932678766
        equity_coeff = .01255
        probability_coeff = .04471
        alpha_coeff = .507
        equity_percent = self.portfolio.stocks / self.portfolio.value
        return Decimal(intercept
            - (longevity_coeff * math.log(years))
            + (equity_coeff * math.sqrt(equity_percent))
            - (probability_coeff * self.pos)
            + (alpha_coeff * self.alpha))
