import operator
import functools
import itertools
import pandas
import collections
from decimal import *

# Don't raise exception when we divide by zero
setcontext(ExtendedContext)
#getcontext().prec = 5

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

class RebalanceHarvesting(HarvestingStrategy):
    def __init__(self, portfolio, stock_pct=Decimal('.5')):
        self.portfolio = portfolio
        self.stock_pct = stock_pct

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
       
class EM(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, scale_rate=Decimal('.95'), floor_rate=Decimal('.025'), cap_rate=Decimal('1.5'), years_left=40):
        super().__init__(portfolio, harvest_strategy)
        
        self.scale_rate = scale_rate
        self.floor_rate = floor_rate
        self.cap_rate = cap_rate
        self.initial_withdrawal = None
        self.years_left = years_left
        self.initial_withdrawal = get_extended_mufp(years_left) * portfolio.value
        #print('%d %d' % (self.initial_withdrawal, self.initial_withdrawal * cap_rate))
        
    def withdrawals(self):
        change = yield
        while True:
            (gains, _, _) = self.portfolio.adjust_returns(change)
            self.cumulative_inflation *= (1 + change.inflation)

            withdrawal_rate = get_extended_mufp(self.years_left)
            withdrawal = withdrawal_rate * self.portfolio.value
            
            scale_boundary = Decimal('.75') * (self.initial_withdrawal * self.cumulative_inflation)
            if withdrawal > scale_boundary:
                scale_diff = withdrawal - scale_boundary
                scale_ratio = scale_diff / scale_boundary
                if scale_ratio > 1:
                    scale_ratio = Decimal('1.0')
                withdrawal = scale_boundary + (scale_diff * scale_ratio * self.scale_rate)
                
            cap_amount = self.cap_rate * self.initial_withdrawal * self.cumulative_inflation
            if withdrawal > cap_amount:
                #print('Exceeded cap')
                withdrawal = cap_amount
                
            floor_amount = self.floor_rate * self.initial_withdrawal * self.cumulative_inflation
            if withdrawal < floor_amount:
                #print('Exceeded floor')
                withdrawal = floor_amount
 
            actual_withdrawal = self.harvest.send(withdrawal)
            self.years_left -= 1
            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

def ECM(portfolio, harvest_strategy):
    return EM(portfolio, harvest_strategy, scale_rate=Decimal('.6'), floor_rate=Decimal('.025'))

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
    
        constant_factor = 1.0 / len(cashflows)
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
    return 1 / ssr_seq(r_r)

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
    
    constant_factor = 1.0 / len(cashflows) * gamma
    base = constant_factor * sum(map(sigma, cashflows))
    return pow(base, -1/gamma)

def low_returns(stocks=Decimal('.04'), bonds=Decimal('.02'), inflation=Decimal('.02')):
    return itertools.repeat(AnnualChange(year = 0, stocks = stocks, bonds = bonds, inflation = inflation))

class Returns_US_1871:
    def __init__(self, wrap=False):
        # import US based data from 1871 from the simba backtesting spreadsheet found on bogleheads.org
        # https://www.bogleheads.org/forum/viewtopic.php?p=2753812#p2753812
        self.dataframe = pandas.read_csv('1871_returns.csv')
        self.years_of_data = len(self.dataframe)

        if wrap:
            self.dataframe += self.dataframe

    def __iter__(self):
        return self.iter_from(0)
    
    def get_year(self, index):
        return self.dataframe.iloc[index]['Year']

    def iter_from(self, year, length=None):
        start = year - 1871
        assert start >= 0
        assert start < 2016
        count = 0
        for row in self.dataframe.iloc[start:].iterrows():
            (stocks, bonds, inflation) = (Decimal(row[1][x]) / 100 for x in ("VFINX", "IT Bonds", "CPI-U"))
            yield AnnualChange(
                year = row[1]['Year'],
                stocks = stocks,
                bonds = bonds,
                inflation = inflation
            )
            count += 1
            if length != None and count >= length:
                raise StopIteration
