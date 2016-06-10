import operator
import functools
import itertools
import pandas
import collections
import math
from decimal import *
import random

# Set graph styling to common styles
from matplotlib import pyplot as plt
import matplotlib
import seaborn as sns
plt.style.use('seaborn-poster')
matplotlib.rcParams['font.family'] = 'League Spartan'

# So I don't have to keep looking up how to do this...
def f_int(x):
    return format(int(x), ',')
# some matplotlib functions pass in a position, which we don't need
def mf_int(x, pos):
    return f_int(x)
def format_axis_labels_with_commas(axis):
    axis.set_major_formatter(matplotlib.ticker.FuncFormatter(mf_int))
def format_plt_labels_with_commas(plt):
    # I have no idea what the 111 magic number is. It was in a quora post and seems to work.
    axis = plt.get_subplot(111)
    format_axis_labels_with_commas(axis)

# Don't raise exception when we divide by zero
setcontext(ExtendedContext)
#getcontext().prec = 5

def annotate(axis, text, xy, xy_text):
    axis.annotate("${:,}".format(int(text)), xy=xy,
             xytext=xy_text,
             arrowprops=dict(facecolor='black', connectionstyle="arc3,rad=.2"),
             fontsize=14)

def find_smallest(s):
    smallest = min(s)
    index_of = s.index(smallest)
    return(index_of, smallest)

def find_biggest(s):
    biggest = max(s)
    index_of = s.index(biggest)
    return(index_of, biggest)

def annotate_smallest(axis, s, location=None):
    (x, y) = find_smallest(s)
    if location == None:
        location = (x * Decimal('1.1'), y * Decimal('.9'))
        
    annotate(axis, y, (x, y), location)
    
def annotate_biggest(axis, s, location=None):
    (x, y) = find_biggest(s)
    if location == None:
        location = (x * Decimal('0.9'), y * Decimal('1.1'))
        
    annotate(axis, y, (x, y), location)

def plot(s, x_label='', y_label='', y_lim=(), title=''):
    fig, ax1 = plt.subplots()
    ax1.plot(s, 'b')
    ax1.set_ylabel(y_label, color='b')
    ax1.set_ylim(y_lim)
    ax1.set_xlabel(x_label)

    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    plt.title(title)
    plt.show()
    
def plot_two(s1, s2, s1_title='', s2_title='', x_label='', title='', y_lim=()):
    fig, ax1 = plt.subplots()
    ax1.plot(s1, 'b')
    ax1.set_ylabel(s1_title, color='b')
    ax1.set_xlabel(x_label)
    ax1.set_ylim(y_lim)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    format_axis_labels_with_commas(ax1.get_yaxis())

    ax2 = ax1.twinx()
    ax2.plot(s2, 'g')
    ax2.set_ylabel(s2_title, color='g')
    ax2.set_ylim(y_lim)
    for tl in ax2.get_yticklabels():
        tl.set_color('g')
    format_axis_labels_with_commas(ax2.get_yaxis())
    
    plt.xlabel(x_label)
    plt.title(title)
    plt.show()

def prod(x):
    return functools.reduce(operator.mul, x, 1)

class WithdrawalStrategy():
    def __init__(self, portfolio, harvest_strategy):
        self.portfolio = portfolio
        self.harvest = harvest_strategy
        self.cumulative_inflation = Decimal('1.0')

    def withdrawals(self):
        pass

class HarvestingStrategy():
    def harvest(self, annual_harvest):
        '''
           This is must be a co-routine .send(AnnualHarvest) every year
        '''
        assert isinstance(annual_harvest, AnnualHarvest)

class N_RebalanceHarvesting(HarvestingStrategy):
    # subclasses must override this
    stock_pct = None

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def harvest(self):
        amount = yield
        while True:
            # first generate some cash
            self.portfolio.sell_stocks(self.portfolio.stocks)
            self.portfolio.sell_bonds(self.portfolio.bonds)

            new_val = self.portfolio.value - amount
            self.portfolio.buy_stocks(new_val * self.stock_pct)
            self.portfolio.buy_bonds(self.portfolio.cash - amount)

            amount = yield self.portfolio.empty_cash()

class N_50_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.5')
class N_60_RebalanceHarvesting(N_RebalanceHarvesting):
    stock_pct = Decimal('.6')

class PrimeHarvesting(HarvestingStrategy):
    _stock_ceiling = Decimal('1.2')

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def stock_increase(self):
        return self.portfolio.stocks / self.portfolio.starting_stocks_real

    def harvest(self):
        amount = yield
        while True:
            if self.stock_increase() > self._stock_ceiling:
                to_sell = self.portfolio.stocks / 5
                self.portfolio.sell_stocks(to_sell)
                self.portfolio.buy_bonds(to_sell)

            bond_amount = min(amount, self.portfolio.bonds)
            self.portfolio.sell_bonds(bond_amount)

            if self.portfolio.cash < amount:
                remainder = amount - self.portfolio.cash
                stock_amount = min(remainder, self.portfolio.stocks)
                self.portfolio.sell_stocks(stock_amount)

            amount = yield self.portfolio.empty_cash()

# TODO: this class needs to be updated to work like VPW and EM in the
# new style.
class ConstantWithdrawals(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.05')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate
        self.initial_withdrawal = portfolio.value * rate

    def withdrawals(self):
        change = yield
        while True:
            previous_portfolio_amount = self.portfolio.value
            self.portfolio.adjust_returns(change)
            gains = (self.portfolio.value - previous_portfolio_amount) / previous_portfolio_amount

            self.cumulative_inflation *= (1 + change.inflation)

            withdrawal = self.initial_withdrawal * self.cumulative_inflation
            actual_withdrawal = self.harvest.send(withdrawal)

            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

def get_extended_mufp(years_left):
    assert years_left > 0

    if years_left > 50:
        return Decimal('5.1')
    else:
        return extended_mufp_table[years_left] / 100

# The index is the number of years remaining, so 1 year remaining = 17.7%
extended_mufp_table = [
    None,
    Decimal('17.7'),
    Decimal('17.7'),
    Decimal('17.7'),
    Decimal('14.3'),
    Decimal('14.3'),
    Decimal('13.0'),
    Decimal('13.0'),
    Decimal('13.0'),
    Decimal('11.3'),
    Decimal('11.3'),
    Decimal('10.3'),
    Decimal('10.3'),
    Decimal('9.7'),
    Decimal('9.7'),
    Decimal('9.2'),
    Decimal('8.7'),
    Decimal('8.7'),
    Decimal('8.3'),
    Decimal('7.9'),
    Decimal('7.9'),
    Decimal('7.5'),
    Decimal('7.1'),
    Decimal('6.9'),
    Decimal('6.9'),
    Decimal('6.6'),
    Decimal('6.4'),
    Decimal('6.3'),
    Decimal('6.1'),
    Decimal('6.0'),
    Decimal('5.9'),
    Decimal('5.8'),
    Decimal('5.8'),
    Decimal('5.7'),
    Decimal('5.6'),
    Decimal('5.6'),
    Decimal('5.5'),
    Decimal('5.5'),
    Decimal('5.4'),
    Decimal('5.4'),
    Decimal('5.4'),
    Decimal('5.3'),
    Decimal('5.3'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.1'),
    Decimal('5.1'),
    Decimal('5.1')
    ]

class VPW(WithdrawalStrategy):
    def calc_withdrawal(portfolio_value, year):
        return vpw_rates[year] * portfolio_value

    def withdrawals(self):
        index = 0
        withdrawal = VPW.calc_withdrawal(self.portfolio.value, index)
        actual_withdrawal = self.harvest.send(withdrawal)

        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        index += 1

        while True:
            (gains, _, _) = self.portfolio.adjust_returns(change)

            withdrawal = vpw_rates[index] * self.portfolio.value
            actual_withdrawal = self.harvest.send(withdrawal)

            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)
            
            index += 1

class EM(WithdrawalStrategy):
    DEFAULT_SCALE_RATE = Decimal('.95')
    DEFAULT_FLOOR_RATE = Decimal('.025')
    DEFAULT_CAP_RATE = Decimal('1.5')
    DEFAULT_INITIAL_WITHDRAWAL_RATE = Decimal('.05')

    def __init__(self, portfolio, harvest_strategy,
                 scale_rate=DEFAULT_SCALE_RATE,
                 floor_rate=DEFAULT_FLOOR_RATE,
                 cap_rate=DEFAULT_CAP_RATE,
                 initial_withdrawal_rate=DEFAULT_INITIAL_WITHDRAWAL_RATE,
                 years_left=40):
        super().__init__(portfolio, harvest_strategy)

        self.scale_rate = scale_rate
        self.floor_rate = floor_rate
        self.cap_rate = cap_rate
        self.initial_withdrawal_rate = initial_withdrawal_rate
        self.years_left = years_left

    def calc_withdrawal(portfolio_value, years_left,
                        scale_rate=DEFAULT_SCALE_RATE,
                        floor_rate=DEFAULT_FLOOR_RATE,
                        cap_rate=DEFAULT_CAP_RATE,
                        initial_withdrawal_rate=DEFAULT_INITIAL_WITHDRAWAL_RATE):
        # first year
        withdrawal = initial_withdrawal_rate * portfolio_value
        inflation_adjusted_withdrawal_amount = withdrawal
        (portfolio_value, inflation) = yield withdrawal
                
        while True:
            inflation_adjusted_withdrawal_amount = withdrawal * (1 + inflation)
            
            withdrawal_rate = get_extended_mufp(years_left)
            withdrawal = withdrawal_rate * portfolio_value
            
            scale_boundary = Decimal('.75') * inflation_adjusted_withdrawal_amount
            if withdrawal > scale_boundary:
                scale_diff = withdrawal - scale_boundary
                scale_ratio = scale_diff / scale_boundary
                if scale_ratio > 1:
                    scale_ratio = Decimal('1.0')
                withdrawal = scale_boundary + (scale_diff * scale_ratio * scale_rate)
            
            cap_amount = (cap_rate / initial_withdrawal_rate) * inflation_adjusted_withdrawal_amount
            withdrawal = min(withdrawal, cap_amount)
                
            floor_amount = (floor_rate / initial_withdrawal_rate) * inflation_adjusted_withdrawal_amount
            withdrawal = max(withdrawal, floor_amount)
            
            (portfolio_value, inflation) = yield withdrawal
            
            years_left -= 1
            # if we go more than 40 years, just keep pretending we're still in the final year....
            if years_left < 1:
                years_left = 1

    def withdrawals(self):
        em = EM.calc_withdrawal(self.portfolio.value, self.years_left)
        withdrawal = em.send(None)
        actual_withdrawal = self.harvest.send(withdrawal)

        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)
            
        while True:
            (gains, _, _) = self.portfolio.adjust_returns(change)
            self.cumulative_inflation *= (1 + change.inflation)
            
            withdrawal = em.send((self.portfolio.value, change.inflation))                            
            actual_withdrawal = self.harvest.send(withdrawal)
            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

def ECM(portfolio, harvest_strategy):
    return EM(portfolio, harvest_strategy, scale_rate=Decimal('.6'), floor_rate=Decimal('.025'))

# TODO: this class needs to be updated to work like VPW and EM in the
# new style.
class SensibleWithdrawals(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, extra_return_boost=Decimal('.31'), initial_rate=Decimal('.05')):
        super().__init__(portfolio, harvest_strategy)

        self.initial_withdrawal = initial_rate * portfolio.value
        self.extra_return_boost = extra_return_boost
        self.initial_rate = initial_rate

    def withdrawals(self):
        change = yield
        while True:
            # portfolio growth
            previous_portfolio_amount = self.portfolio.value
            self.portfolio.adjust_returns(change)
            gains = (self.portfolio.value - previous_portfolio_amount) / previous_portfolio_amount

            # start gummy's calculations
            self.cumulative_inflation *= (1 - change.inflation)

            inflation_adjusted_withdrawal_amount = self.initial_withdrawal / self.cumulative_inflation
            current_withdrawal_amount = inflation_adjusted_withdrawal_amount * .8

            base_portfolio_value = self.portfolio.value - current_withdrawal_amount
            previous_portfolio_amount *= (1 + change.inflation)
            extra_return = base_portfolio_value - previous_portfolio_amount

            if extra_return > 0:
                current_withdrawal_amount += extra_return * self.extra_return_boost

            current_withdrawal_amount = min(current_withdrawal_amount, self.portfolio.value)

            self.harvest.harvest(current_withdrawal_amount)

            change = yield YearlyResults(withdraw_n = current_withdrawal_amount,
                             withdraw_r = current_withdrawal_amount * self.cumulative_inflation,
                             withdraw_pct = current_withdrawal_amount / (self.portfolio.value + current_withdrawal_amount),
                             portfolio_n = self.portfolio.value,
                             portfolio_r = self.portfolio.real_value,
                             returns = gains)
            assert isinstance(change, AnnualChange)


AnnualChange = collections.namedtuple('AnnualChange', ['year', 'stocks', 'bonds', 'inflation'])
AnnualHarvest = collections.namedtuple('AnnualHarvest', ['change', 'withdrawal'])

YearlyResults = collections.namedtuple('YearlyResults',
    ['returns',
     'withdraw_n', 'withdraw_r', 'withdraw_pct_cur', 'withdraw_pct_orig',
     'portfolio_n', 'portfolio_r', 'portfolio_bonds', 'portfolio_stocks'])

def report(portfolio, withdrawal, current_gains):
    return YearlyResults(
        returns = current_gains,
        withdraw_n = withdrawal,
        withdraw_r = withdrawal / portfolio.inflation,

        withdraw_pct_cur = withdrawal / portfolio.value,
        withdraw_pct_orig = (withdrawal / portfolio.inflation) / portfolio.starting_value,

        portfolio_n = portfolio.value,
        portfolio_r = portfolio.real_value,
        portfolio_bonds = portfolio.bonds,
        portfolio_stocks = portfolio.stocks
    )

def extract_living(list_of_yearly_results):
    ''' This provides a list of results to compare to the tables in the book Living Off Your Money'''
    return list(map(lambda x: x.withdraw_pct_orig, list_of_yearly_results))

class Portfolio():
    def __init__(self, stocks, bonds, cash = 0):
        self._stocks = Decimal(stocks)
        self._bonds = Decimal(bonds)
        self._cash = Decimal(cash)
        self._starting_value = Decimal(stocks + bonds + cash)
        self._starting_stocks = Decimal(stocks)
        self.inflation = Decimal('1.0')

    @property
    def starting_stocks_real(self):
        return self._starting_stocks * self.inflation

    @property
    def starting_value_real(self):
        return self.starting_value * self.inflation

    @property
    def starting_value(self):
        return self._starting_value

    @property
    def stocks(self):
        return self._stocks

    @property
    def bonds(self):
        return self._bonds

    @property
    def cash(self):
        return self._cash

    @property
    def value(self):
        return self.bonds + self.stocks + self.cash

    @property
    def real_value(self):
        return self.value / self.inflation

    def withdraw_cash(self, amount):
        assert amount <= self._cash
        self._cash -= amount
        return self.cash

    def empty_cash(self):
        x = self.cash
        self._cash = 0
        return x

    def sell_stocks(self, amount):
        assert amount <= self._stocks
        self._stocks -= amount
        self._cash += amount
        return self.cash

    def buy_stocks(self, amount):
        assert amount <= self._cash
        self._stocks += amount
        self._cash -= amount
        return self.cash

    def sell_bonds(self, amount):
        assert amount <= self._bonds
        self._bonds -= amount
        self._cash += amount
        return self.cash

    def buy_bonds(self, amount):
        assert amount <= self._cash
        self._bonds += amount
        self._cash -= amount
        return self.cash

    def adjust_returns(self, change):
        assert isinstance(change, AnnualChange)
        prev_value = self.value
        self._bonds *= 1 + change.bonds
        self._stocks *= 1 + change.stocks
        self.inflation *= (1 + change.inflation)
        gains = (self.value - prev_value) / prev_value
        return (gains, prev_value, self.value)

def hreff(withdrawals, returns):
    ''' Harvesting-Rate Efficiency (HREFF)

    HREFF is defined in Living Off Your Money (2016) by McClusky. It is a variant
    of WER with the addition of a withdrawal floor and penalties when annual
    withdrawals go below that.
    '''
    def cew_floor(cashflows, floor=Decimal('0.03')):
        gamma = Decimal('5.0')
        epsilon = 30

        def f(x):
            if x <= floor:
                return x - floor
            else:
                return x - (floor /
                            ( 1 +
                             ( epsilon * pow((x - floor), 3))))


        def sigma(c):
            return pow(f(c), 1/gamma)

        constant_factor = Decimal('1.0') / len(cashflows)
        base = constant_factor * sum(map(sigma, cashflows))
        return pow(base, gamma)

    return n(withdrawals) / ssr(returns)

def wer(withdrawals, returns):
    ''' Withdrawal Efficiency Rate

        Given a list-liek of withdrawals and a list-like of actual returns over that same
        period, calculate how 'efficient' the withdrawals were.

        This is done by calculating the Sustainable

        Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
        by Blanchett, Kowara, Chen
        https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf
    '''

    return cew(withdrawals) / ssr(returns)


def ssr(r):
    ''' Sustainable Spending Rate given a known sequence of returns

        Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
        by Blanchett, Kowara, Chen
        https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf
    '''

    def ssr_seq(r):
        if len(r) == 0: return 1
        else:
            denom = prod(map(lambda x: x + 1, r))
            return (1 / denom) + ssr_seq(r[1:])

    # skip the final year of returns (since you have withdrawn the entire portfolio
    # at the beginning of the year,
    # knowing that you will die this year)
    r_r = list(reversed(r[:-1]))
    return Decimal('1') / ssr_seq(r_r)

def cew(cashflows):
    ''' Constant Equivalent Withdrawals
    Given a sequence of withdrawals, calculate what the constant-equivalent would be.

    Described in Optimal Withdrawal Strategy for Retirement Income Portfolios (2012)
    by Blanchett, Kowara, Chen
    https://corporate.morningstar.com/us/documents/ResearchPapers/OptimalWithdrawalStrategyRetirementIncomePortfolios.pdf
    '''

    # chosen somewhat arbitrarily by Blanchett et al point out that
    # the final results aren't very sensitive to this number (i.e. changing it to
    # 2 doesn't affect the final numbers very much)
    gamma = Decimal('4.0')

    def sigma(c):
        return pow(c, -gamma) / gamma

    constant_factor = Decimal('1.0') / len(cashflows) * gamma
    base = constant_factor * sum(map(sigma, cashflows))
    return pow(base, -1/gamma)

def constant_returns(stocks=Decimal('.04'), bonds=Decimal('.02'), inflation=Decimal('.02')):
    return itertools.repeat(AnnualChange(year = 0, stocks = stocks, bonds = bonds, inflation = inflation))
def nirp_returns():
    return constant_returns(stocks=Decimal('.02'), bonds=Decimal('-.01'), inflation=Decimal('.02'))
def zirp_returns():
    return constant_returns(stocks=Decimal('.04'), bonds=Decimal('0'), inflation=Decimal('.02'))
    
def compare_prime_vs_rebalancing(series, years=30, title=''):
    (r1, r2) = itertools.tee(series)
    x = simulate_withdrawals(r1, years=years)
    y = simulate_withdrawals(r2, years=years, harvesting=N_60_RebalanceHarvesting)

    s1 = [n.withdraw_r for n in x]
    s2 = [n.withdraw_r for n in y]
    
    ceiling = max(max(s1), max(s2))
    if ceiling < 100000:
        ceiling = int(math.ceil(ceiling / 10000) * 10000)
    else:
        ceiling = int(math.ceil(ceiling / 100000) * 100000)
    
    plot_two(s1, s2, s1_title='Prime Harvesting', s2_title='Annual Rebalancing',
                       y_lim=[0,ceiling],
                       x_label='Year of Retirement', title=title)

def big_drop(after=10):
    # 20 years of ZIRP to exhaust bonds under Prime Harvesting
    for i in range(after):
        yield AnnualChange(year=0, stocks=Decimal('.04'), bonds=Decimal('0'), inflation=Decimal('.02'))

    # big drop of stocks to allow rebalacing to "buy stocks cheap"
    yield AnnualChange(year=0, stocks=Decimal('-.25'), bonds=Decimal('0'), inflation=Decimal('.02'))

    # now we just have normal (but not amazing) returns.....
    while True:
        yield AnnualChange(year=0, stocks=Decimal('.08'), bonds=Decimal('.04'), inflation=Decimal('.03'))

def simulate_withdrawals(series,
                            portfolio=(600000, 400000),
                            years=40,
                            harvesting=PrimeHarvesting,
                            withdraw=EM):
    portfolio = Portfolio(portfolio[0], portfolio[1])
    strategy = harvesting(portfolio).harvest()
    strategy.send(None)
    withdrawal_strategy = withdraw(portfolio, strategy).withdrawals()
    annual = []

    # Withdrawals happen at the start of the year, so the first time
    # we don't have any performance data to send them....
    data = withdrawal_strategy.send(None)
    annual.append(data)
    years -= 1

    for _, d in zip(range(years), series):
        data = withdrawal_strategy.send(d)
        annual.append(data)
    return annual

# Numbers from http://www.wsj.com/articles/how-to-think-about-risk-in-retirement-1417408070
# Withdraw 50,000 the first 5 years and then 21,700 thereafter
# the Risk Portfolio is all stock
# the LMP is TIPS/corporate bonds (Bernstein assumes 1% real returns)
def simulate_lmp(series, portfolio=(750000,250000), years=40, lmp_real_annual=Decimal('.01')):
    count = 0
    annual = []
    cumulative_inflation = 1

    lmp = portfolio[0]
    rp = portfolio[1]

    for (year, stocks, bonds, inflation) in series:
        if count > years:
            break

        if count < 5:
            amount = 50000
        else:
            amount = 21700

        cumulative_inflation *= (1 + inflation)

        amount *= cumulative_inflation

        previous_portfolio_amount = rp + lmp
        rp *= (1 + stocks)
        lmp_gains = lmp_real_annual + inflation
        lmp *= (1 + lmp_gains)

        gains = (rp + lmp) - previous_portfolio_amount

        if amount < lmp:
            lmp -= amount
        else:
            a1 = amount - lmp
            lmp = 0
            if rp > a1:
                rp -= a1
            else:
                amount = rp
                rp = 0

        annual.append(YearlyResults(
            returns = gains,
            withdraw_n = amount,
            withdraw_r = amount / cumulative_inflation,

            withdraw_pct_cur = amount / (rp + lmp),
            withdraw_pct_orig = (amount / cumulative_inflation) / (portfolio[0] + portfolio[1]),

            portfolio_n = rp + lmp,
            portfolio_r = (rp + lmp) / cumulative_inflation,

            portfolio_bonds = lmp,
            portfolio_stocks = rp
        ))

        count += 1
    return annual

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

# based on http://www.ssa.gov/OACT/STATS/table4c6.html Period Life Table, 2009
# https://drive.google.com/open?id=0Bx-R9jPONgMgX0ktTUVFbVU0TEU
lifetable_for_women = [
	0.010298, # 65
	0.011281,
	0.012370,
	0.013572,
	0.014908,
	0.016440, # 70
	0.018162,
	0.020019,
	0.022003,
	0.024173,
	0.026706, # 75
	0.029603,
	0.032718,
	0.036034,
	0.039683,
	0.043899, # 80
	0.048807,
	0.054374,
	0.060661,
	0.067751,
	0.075729, # 85
	0.084673,
	0.094645,
	0.105694,
	0.117853,
	0.131146, # 90
	0.145585,
	0.161175,
	0.177910,
	0.195774,
	0.213849, # 95
    0.231865,
    0.249525,
    0.266514,
    0.282504,
    0.299455, # 100
    0.317422, 
    0.336467,
    0.356655, 
    0.378055, 
    0.400738, # 105
    0.424782, 
    0.450269, 
    0.477285, 
    0.505922, 
    0.536278, # 110
    0.568454, 
    0.602561, 
    0.638715, 
    0.677038, 
    0.717660, # 115
    0.760720, 
    0.806363, 
    0.851378,
    0.893947 # 119 
]

# starting at age 65, 40-year span, based on 60% domestic stocks, 40% domestic bonds
vpw_rates = map(lambda x: x/100, [
    Decimal('4.7'),
    Decimal('4.7'),
    Decimal('4.8'),
    Decimal('4.9'),
    Decimal('4.9'),
    Decimal('5.0'),
    Decimal('5.1'),
    Decimal('5.1'),
    Decimal('5.2'),
    Decimal('5.3'),
    Decimal('5.4'),
    Decimal('5.5'),
    Decimal('5.6'),
    Decimal('5.7'),
    Decimal('5.9'),
    Decimal('6.0'),
    Decimal('6.2'),
    Decimal('6.3'),
    Decimal('6.5'),
    Decimal('6.7'),
    Decimal('6.9'),
    Decimal('7.2'),
    Decimal('7.5'),
    Decimal('7.8'),
    Decimal('8.1'),
    Decimal('8.5'),
    Decimal('9.0'),
    Decimal('9.5'),
    Decimal('10.1'),
    Decimal('10.9'),
    Decimal('11.7'),
    Decimal('12.8'),
    Decimal('14.2'),
    Decimal('15.9'),
    Decimal('18.2'),
    Decimal('21.5'),
    Decimal('26.4'),
    Decimal('34.6'),
    Decimal('50.9'),
    Decimal('100.0'),

    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
    Decimal('0'),
])
vpw_rates = list(vpw_rates)