from decimal import Decimal
from .abc import WithdrawalStrategy

class FeelFree(WithdrawalStrategy):
    """
        By R. Evan Ingliss

        Take you age, divide by 20. That's your current withdrawal rate.

        From http://www.investmentnews.com/assets/docs/CI105854622.PDF
        Discussed in:
        From http://www.usatoday.com/story/money/columnist/powell/2016/08/11/new-retiree-withdrawal-rate-formula-4-percent/86877234/
        and http://www.investmentnews.com/article/20160622/FREE/160629965/this-simple-retirement-spending-strategy-takes-on-the-4-rule
    """

    def __init__(self, portfolio, harvest_strategy, start_age=65):
        super().__init__(portfolio, harvest_strategy)

        self.current_age = start_age

    def start(self): return self._calc()
    def next(self): return self._calc()

    def _calc(self):
        w = Decimal(self.current_age) / 20
        amount = self.portfolio.value * (w / 100)
        self.current_age += 1
        return amount

class IRS_RMD(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, start_age=65):
        super().__init__(portfolio, harvest_strategy)
        self.current_age = start_age

    def start(self): return self._calc()
    def next(self): return self._calc()

    def _calc(self):
        assert self.current_age >= 65
        lookup = min(self.current_age - 65, 114)
        w = self.rmd_table[lookup]
        amount = self.portfolio.value * w
        self.current_age += 1
        return amount


    # The official IRS table in https://www.irs.gov/pub/irs-tege/uniform_rmd_wksht.pdf
    # only starts at age 70. For ages 65-69 we use the data from Appendix 1 of
    # Sun & Webb's paper, "Can Retirees Base Wealth Withdrawals on the IRS' Required
    # Minimum Distributions?" (2012)
    # This table starts at age 65 and goes to 115.
    rmd_table = [
        Decimal('.0313'),
        Decimal('.0322'),
        Decimal('.0331'),
        Decimal('.0342'),
        Decimal('.0353'),
        1 / Decimal('27.4'), # 70
        1 / Decimal('26.5'),
        1 / Decimal('25.6'),
        1 / Decimal('24.7'),
        1 / Decimal('23.8'),
        1 / Decimal('22.9'), # 75
        1 / Decimal('22.0'),
        1 / Decimal('21.2'),
        1 / Decimal('20.3'),
        1 / Decimal('19.5'),
        1 / Decimal('18.7'), # 80
        1 / Decimal('17.9'),
        1 / Decimal('17.1'),
        1 / Decimal('16.3'),
        1 / Decimal('15.5'),
        1 / Decimal('14.8'), # 85
        1 / Decimal('14.1'),
        1 / Decimal('13.4'),
        1 / Decimal('12.7'),
        1 / Decimal('12.0'),
        1 / Decimal('11.4'), # 90
        1 / Decimal('10.8'),
        1 / Decimal('10.2'),
        1 / Decimal('9.6'),
        1 / Decimal('9.1'),
        1 / Decimal('8.6'), # 95
        1 / Decimal('8.1'),
        1 / Decimal('7.6'),
        1 / Decimal('7.1'),
        1 / Decimal('6.7'),
        1 / Decimal('6.3'), # 100
        1 / Decimal('5.9'),
        1 / Decimal('5.5'),
        1 / Decimal('5.2'),
        1 / Decimal('4.9'),
        1 / Decimal('4.5'), # 105
        1 / Decimal('4.2'),
        1 / Decimal('3.9'),
        1 / Decimal('3.7'),
        1 / Decimal('3.4'),
        1 / Decimal('3.1'), # 110
        1 / Decimal('2.9'),
        1 / Decimal('2.6'),
        1 / Decimal('2.4'),
        1 / Decimal('2.1'),
        1 / Decimal('1.9'), # 115
    ]
