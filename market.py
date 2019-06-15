from decimal import Decimal
import itertools
import pandas
import collections
from adt import AnnualChange
import random

def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


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

class PortfolioCharts_1927:
    """ All of the other code only deals with stocks and bonds. Rewriting all
    of it to deal with arbitrary asset classes is not appealing at the moment.
    I also don't know of an actual use case for it. So we'll do a bit of a hack.
    You need to pass in a Weights tuple that tells this how to weight the returns
    of the various subclasses. That means the asset allocation is fixed and can't
    vary over time. But it also means I don't have to rewrite everything right now. """
    asset_classes = [x + y for x in ("LC", "MC", "SC") for y in ("B", "G", "V")]
    Weights = namedtuple_with_defaults("Weights", asset_classes, default_values=[0] * len(asset_classes))

    def __init__(self, weights):
        self.dataframe = pandas.read_csv('stock-index-calculator-20160620-v2.csv')
        self.years_of_data = len(self.dataframe)
        self.weights = weights

    def fmt(self, row):
        stock_performance = [row[x] * self.weights._asdict()[x] for x in self.asset_classes]
        stock_performance = sum(stock_performance)
        return AnnualChange(
                year=row['Year'],
                stocks=Decimal(stock_performance) / 100,
                bonds=Decimal(row['IT Bonds']) / 100,
                inflation=Decimal(row['CPI-U']) / 100
        )

    def random_year(self):
        i = random.randint(0, len(self.dataframe) - 1)
        return self.fmt(self.dataframe.iloc[i])

    def get_year(self, year):
        i = random.randint(0, len(self.dataframe) - 1)
        return self.fmt(self.dataframe.iloc[year-1927])


    def iter_from(self, year, length=None):
        start = year - 1927
        assert start >= 0
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length != None and count >= length:
                raise StopIteration

class JST:
    """ The Jordà-Schularick-Taylor Macrohistory Database stata file containing
        country data from "The Return of Everything"
        http://www.macrohistory.net/data/
    """ 
    def __init__(self, country):
        df = pandas.read_stata('JSTdatasetR4.dta')
        # the year comes through as a float for some reason...coerce back to int
        df['year'] = df['year'].astype(int)
        df = df[df['iso'] == country]
        df = df[['year', 'iso', 'eq_tr', 'bond_tr']]
        df = df.dropna()

        self.start_year = df['year'].min()
        self.last_year = df['year'].max()

        self.data = df

    def __len__(self):
        return len(self.data)

    def fmt(self, row):
        # the database only provides the consumer price index level, not the
        # annual change. I don't feel like going back and calculating it.
        return AnnualChange(
            year=row.year,
            stocks=row.eq_tr,
            bonds=row.bond_tr,
            inflation=0
        )

    def iter_from(self, year, length=None):
        assert year >= self.start_year
        if length:
            assert (year+length) <= self.last_year

        count = 0
        for row in self.data[self.data['year'] >= year].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length != None and count >= length:
                return

class UK1900:
    def __init__(self, wrap=False):
        self.start_year = 1900
        self.dataframe = pandas.read_csv('uk1900.csv', index_col=0, parse_dates=True)

        if wrap:
            self.dataframe += self.dataframe

    def __len__(self):
        return len(self.dataframe)

    def random_year(self):
        i = random.randint(0, len(self.dataframe) - 1)
        return self.fmt(self.dataframe.iloc[i])

    def fmt(self, row):
        (stocks, bonds, inflation) = (Decimal(row[x]) for x in ("Real Equity", "Real Gilt", "Inflation"))

        return AnnualChange(
                year=row.name.year,
                stocks=stocks + inflation,
                bonds=bonds + inflation,
                inflation=inflation
        )

    def iter_from(self, year, length=None):
        start = year - 1900
        assert start >= 0
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length != None and count >= length:
                return

class US_1871_Monthly:
    def __init__(self):
        self.data = pandas.read_csv('US_1871_Monthly.csv', index_col=0, parse_dates=True)

    def fmt(self, row):
        return AnnualChange(
            year=row.name.year,
            stocks=Decimal(row['S&P %']),
            bonds=Decimal(row['Bond %']),
            inflation=0 # it is already reported in real terms
        )

    def iter_from(self, date, length=None):
        count = 0
        for row in self.data.loc[date:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length and count >= length:
                raise StopIteration


class Japan_1957:
    def __init__(self):
        self.start_year = 1957
        self.dataframe = pandas.read_csv('japan-1957-2016.csv',
                    index_col=0,
                    dtype={'Date': int,
                            'CPI Japan': object,
                            'Spliced Bond': object,
                            'NIKKEI225' : object},
                    converters={'CPI Japan': Decimal,
                                 'Spliced Bond' : Decimal,
                                 'NIKKEI225' : Decimal})

    def __len__(self):
        return len(self.dataframe)

    def random_year(self):
        i = random.randint(0, len(self.dataframe) - 1)
        return self.fmt(self.dataframe.iloc[i])

    def fmt(self, row):
        return AnnualChange(
                year=row.name,
                stocks=row['NIKKEI225'],
                bonds=row['Spliced Bond'],
                inflation=row['CPI Japan']
        )

    def iter_from(self, year, length=None):
        start = year - 1957
        assert start >= 0
        assert start < 2016
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length and count >= length:
                return


class Japan_1975:
    def __init__(self):
        self.dataframe = pandas.read_csv('japan-1975-2016.csv',
                    index_col=0,
                    dtype={'Year': int,
                            'CPI': object,
                            'IT Bond': object,
                            'Equities' : object},
                    converters={'CPI': Decimal,
                                 'IT Bond' : Decimal,
                                 'Equities' : Decimal})

    def fmt(self, row):
        return AnnualChange(
                year=row.name,
                stocks=row['Equities'],
                bonds=row['IT Bond'],
                inflation=row['CPI']
        )

    def iter_from(self, year, length=None):
        start = year - 1975
        assert start >= 0
        assert start < 2016
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length and count >= length:
                return


class Returns_US_1871:
    def __init__(self, wrap=False):
        # import US based data from 1871 from the simba backtesting
        # spreadsheet found on bogleheads.org
        # https://www.bogleheads.org/forum/viewtopic.php?p=2753812#p2753812
        self.start_year = 1871
        self.dataframe = pandas.read_csv('1871_returns.csv')
        self.years_of_data = len(self.dataframe)

        if wrap:
            self.dataframe += self.dataframe

    def __len__(self):
        return len(self.dataframe)

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
                year=row['Year'],
                stocks=stocks,
                bonds=bonds,
                inflation=inflation
        )

    def iter_from(self, year, length=None):
        start = year - 1871
        assert start >= 0
        assert start < 2016
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            yield self.fmt(row[1])
            count += 1
            if length and count >= length:
                return
