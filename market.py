from decimal import Decimal
import itertools
from adt import AnnualChange

def constant_returns(stocks=Decimal('.04'), bonds=Decimal('.02'), inflation=Decimal('.02')):
    return itertools.repeat(AnnualChange(year = 0, stocks = stocks, bonds = bonds, inflation = inflation))
def nirp_returns():
    return constant_returns(stocks=Decimal('.02'), bonds=Decimal('-.01'), inflation=Decimal('.02'))
def zirp_returns():
    return constant_returns(stocks=Decimal('.04'), bonds=Decimal('0'), inflation=Decimal('.02'))

def big_drop(after=10):
    # 20 years of ZIRP to exhaust bonds under Prime Harvesting
    for i in range(after):
        yield AnnualChange(year=0, stocks=Decimal('.04'), bonds=Decimal('0'), inflation=Decimal('.02'))

    # big drop of stocks to allow rebalacing to "buy stocks cheap"
    yield AnnualChange(year=0, stocks=Decimal('-.25'), bonds=Decimal('0'), inflation=Decimal('.02'))

    # now we just have normal (but not amazing) returns.....
    while True:
        yield AnnualChange(year=0, stocks=Decimal('.08'), bonds=Decimal('.04'), inflation=Decimal('.03'))


class Returns_US_1871:
    def __init__(self, wrap=False):
        # import US based data from 1871 from the simba backtesting spreadsheet found on bogleheads.org
        # https://www.bogleheads.org/forum/viewtopic.php?p=2753812#p2753812
        self.dataframe = pandas.read_csv('1871_returns.csv')
        self.years_of_data = len(self.dataframe)

        if wrap:
            self.dataframe += self.dataframe

    def __iter__(self):
        return self.iter_from(1871)

    def get_year(self, index):
        return self.dataframe.iloc[index]['Year']

    def shuffle(self):
        index = list(self.dataframe.index)
        random.shuffle(index)
        self.dataframe = self.dataframe.ix[index]
        self.dataframe.reset_index()
        return self

    def random_year(self):
        i = random.randint(0, len(self.dataframe) - 1)
        return self.fmt(self.dataframe.iloc[i])

    def fmt(self, row):
        (stocks, bonds, inflation) = (Decimal(row[x]) / 100 for x in ("VFINX", "IT Bonds", "CPI-U"))
        return AnnualChange(
                year = row['Year'],
                stocks = stocks,
                bonds = bonds,
                inflation = inflation
        )

    def iter_from(self, year, length=None):
        start = year - 1871
        assert start >= 0
        assert start < 2016
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length != None and count >= length:
                raise StopIteration
