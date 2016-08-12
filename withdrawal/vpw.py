from decimal import Decimal
from .abc import WithdrawalStrategy
from . import vpw_rates

class VPW(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy):
        super().__init__(portfolio, harvest_strategy)

        self.index = 0

    def calc_withdrawal(portfolio_value, year):
        # For now we use 60/40 with a 35 year time span.
        # That's not EXACTLY what the spreadsheet gives you
        # by default (it has 50/50 with 35 years). But it isn't
        # too far off. And lots of other tests assume a 60/40
        # portfolio.
        #
        # It would be better to either
        # - Use the portfolio to look up dynamically
        # - Just implement all of VPW ourselves here instead of
        #   relying on prebaked things from the spreadsheet
        return vpw_rates.s_60_40_35[year] * portfolio_value

    def start(self):
        return VPW.calc_withdrawal(self.portfolio.value, index)

    def next(self):
        index += 1

        if index < len(vpw_rates):
            withdrawal = VPW.calc_withdrawal(self.portfolio.value, index)
        else:
            # VPW ran out of money. You might think this is unfair to VPW.
            # "But someone who is 98 and still alive would replan!"
            # But other strategies aren't allowed to do ad hoc replanning
            # (e.g. constant dollar withdrawals) when things start to look
            # dire. Instead of adding ad hoc replanning to ONE method...
            # we just let it fail.
            withdrawal = 0

        return withdrawal
