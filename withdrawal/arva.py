from decimal import Decimal
from .abc import WithdrawalStrategy
from metrics import average, pmt

class ARVA(WithdrawalStrategy):
    """ This comes from Siegel and Waring's 'Only Spending Rule You'll Ever Need' (2014)
    https://larrysiegeldotorg.files.wordpress.com/2014/09/siegel_waring_only-spending-rule-article-youll-ever-need.pdf

    Which is basically PMT, the same underlying rule as in VPW.

    However, Siegel and Waring have different suggestions about how the discount_rate and "number of years"
    should be calculated, so this has their defaults baked in.
    """

    MAX_AGE = 120

    def __init__(self, portfolio, harvest_strategy, start_age=65, discount_rate=Decimal('.02')):
        super().__init__(portfolio, harvest_strategy)

        self.discount_rate = discount_rate
        self.current_age = start_age

    def _calc(self):
        # Siegel & Waring suggest the discount rate should be
        # "TIPS interest rate (present-value-weighted average interest rate across the TIPS
        # ladder)" at the start of each year.
        # Currently, we don't support changing the discount_rate every year and use a constant rate
        rate = self.discount_rate

        # Siegel & Waring suggest using the average of 120 (the maximum known human life span) and
        # life expectancy based on current age according to the Social Security tables.
        years_left = average([ARVA.MAX_AGE, get_life_expectancy(self.current_age)]) 
        return pmt(rate, years_left, self.portfolio.value)

    def start(self): return self._calc()

    def next(self):
        self.current_age += 1

        return self._calc()

def get_life_expectancy(age):
    if age > 100:
        age = 100
    return life_expectancy[age]

# This is probably Good Enough(tm).
# I am hard coding the life expectancy for a Male according to the
# 2011 Life table from the NVSS (included in sources)
life_expectancy = [
    76.3,
    75.8,
    74.8,
    73.9,
    72.9,
    71.9,
    70.9,
    69.9,
    68.9,
    67.9,
    66.9,
    65.9,
    64.9,
    64.0,
    63.0,
    62.0,
    61.0,
    60.0,
    59.1,
    58.1,
    57.2,
    56.2,
    55.3,
    54.4,
    53.5,
    52.5,
    51.6,
    50.7,
    49.7,
    48.8,
    47.9,
    46.9,
    46.0,
    45.1,
    44.1,
    43.2,
    42.3,
    41.4,
    40.4,
    39.5,
    38.6,
    37.7,
    36.7,
    35.8,
    34.9,
    34.0,
    33.1,
    32.3,
    31.4,
    30.5,
    29.7,
    28.8,
    28.0,
    27.1,
    26.3,
    25.5,
    24.7,
    23.9,
    23.1,
    22.3,
    21.6,
    20.8,
    20.0,
    19.3,
    18.5,
    17.8,
    17.1,
    16.4,
    15.7,
    15.0,
    14.3,
    13.6,
    13.0,
    12.3,
    11.7,
    11.1,
    10.5,
    9.9,
    9.3,
    8.8,
    8.2,
    7.7,
    7.2,
    6.7,
    6.3,
    5.9,
    5.5,
    5.1,
    4.7,
    4.4,
    4.1,
    3.8,
    3.5,
    3.3,
    3.1,
    2.9,
    2.7,
    2.5,
    2.3,
    2.2,
    2.1, # 100 and over stays at 2.1
]

