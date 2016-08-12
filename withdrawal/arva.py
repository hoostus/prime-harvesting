from decimal import Decimal
from .abc import WithdrawalStrategy

# TODO: This is incomplete.

class ARVA(WithdrawalStrategy):
    """ This comes from Siegel and Waring's 'Only Spending Rule You'll Ever Need' (2014)
    https://larrysiegeldotorg.files.wordpress.com/2014/09/siegel_waring_only-spending-rule-article-youll-ever-need.pdf

    Which is basically PMT, the same underlying rule as in VPW.

    However, Siegel and Waring have different suggestions about how the discount_rate and "number of years"
    should be calculated, so this has their defaults baked in.
    """
    def __init__(self, portfolio, harvest_strategy, discount_rate=Decimal('.02')):
        # Siegel & Waring seem to suggest the discount rate should be
        # "TIPS interest rate (present-value-weighted average interest rate across the TIPS
        # ladder)" at the start of each year.
        # Currently, we don't support changing the discount_rate every year and use a constant rate
        super().__init__(portfolio, harvest_strategy)

        self.discount_rate = discount_rate

    # every year we need to
    # Siegel & Waring suggest using the average of 120 (the maximum known human life span) and
    # life expectancy based on current age according to the Social Security tables
    # years_remaining = average(120, mean_life_expectancy)
    # -numpy.pmt(discount_rate, years_remaining, portfolio.value, 0, 'start')

    # Siegel & Waring's suggestion to continually update the assumptions make this
    # tricky to model well
