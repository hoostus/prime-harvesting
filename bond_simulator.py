import numpy
import pandas
import functools
import operator

def iterate_fund(ladder, yield_curve, max_maturity):
    ladder.reduce_maturities()
    ladder.generate_payments()
    sold_bonds = ladder.sell_bonds(yield_curve)

    # Only buy a new bond if we actually sold one...
    if sold_bonds:
        ladder.buy_bond(yield_curve[max_maturity-1], max_maturity)
    
    # This happens *after* we sell the shortest bond and buy a new long one
    # (at least, that's what longinvest does...)
    nav = ladder.get_nav(yield_curve)

    return (ladder, nav)

class Bond:
    def __init__(self, face_value, yield_pct, maturity):
        self.face_value = face_value
        self.yield_pct = yield_pct
        self.maturity = maturity
        
    def __repr__(self):
        return ('Maturity: %d | Yield: %.2f%% | Face Value: $%.2f' % (self.maturity, self.yield_pct * 100, self.face_value))

    def gen_payment(self):
        return self.face_value * self.yield_pct
    
    def value(self, rates):
        value = numpy.pv(rates[self.maturity - 1], self.maturity, (self.face_value * self.yield_pct), self.face_value)
        return -value
    
class BondLadder:
    def __init__(self, min_maturity, max_maturity):
        self.min_maturity = min_maturity
        self.max_maturity = max_maturity
        self.cash = 0
        
        self.ladder = set()
        
    def print_all(self):
        for bond in sorted(self.ladder, key=lambda b: b.maturity):
            print(bond)
            
    def print_all_values(self, rates):
        for bond in sorted(self.ladder, key=lambda b: b.maturity):
            print(bond.value(rates))

    def maturity(self):
        """ This is average maturity, weighted by face value """
        m = functools.reduce(operator.add, [x.maturity * x.face_value for x in self.ladder])
        fv = functools.reduce(operator.add, [x.face_value for x in self.ladder])
        return m / fv

    def buy_bond(self, rate, maturity):
        b = Bond(self.cash, rate, maturity)
        self.add_bond(b)
        self.cash = 0
        return b
        
    def get_nav(self, rates):
        return self.cash + sum((b.value(rates) for b in self.ladder))

    def generate_payments(self):
        payments = sum((b.gen_payment() for b in self.ladder))
        print(f'Payments: {payments}')
        self.cash += payments
        
    def __repr__(self):
        return ('%d-%d Ladder { Num Bonds: %d. }' % (self.max_maturity, self.min_maturity, len(self.ladder)))
        
    def add_bond(self, bond):
        #assert bond.maturity <= self.max_maturity
        #assert bond.maturity >= self.min_maturity
        self.ladder.add(bond)
    
    def reduce_maturities(self):
        for bond in self.ladder:
            bond.maturity -= 1

    def sell_bonds(self, rates):
        to_sell = filter(lambda bond: bond.maturity < self.min_maturity, self.ladder)
        to_sell = list(to_sell)
        self.ladder = self.ladder.difference(to_sell)
        self.cash += sum((b.value(rates) for b in to_sell))
        return to_sell

def bootstrap(yield_curve, max_bonds, min_maturity):
    ladder = BondLadder(min_maturity, max_bonds)
    #starting_face_value = 50 # chosen arbitrarily (to match longinvest)
    start_nav = 10_000
    num_bonds = max_bonds - min_maturity
    starting_face_value = start_nav / num_bonds

    for j in range(min_maturity, max_bonds+1):
        bond_yield = yield_curve[max_bonds-1]
        face_value = pow(1 + bond_yield, j-min_maturity) * starting_face_value
        b = Bond(face_value, bond_yield, j)
        ladder.add_bond(b)
    ladder.print_all_values(yield_curve)
    return ladder

def loop(ladder, rates, max_maturity):
    df = pandas.DataFrame(columns=['NAV', 'Change', 'Maturity'])

    # The first iterations have fake data with duplicate years
    # But that's okay because we overwrite them with later data
    # (since they all have the same year)
    for (year, current_rates) in rates:
        if year.year > 1951: break
        m = ladder.maturity()
        # This is a hack to handle switching between monthly & yearly
        # simulations. It assumes we never have a maturity more than this
        if m > 30:
            m /= 12
        (ladder, nav) = iterate_fund(ladder, current_rates.tolist(), max_maturity)
        df.loc[year] = {'NAV' : nav, 'Change' : None, 'Maturity': m}

    calculate_returns(df)
    return df

def calculate_returns(df):
    change = df / df.shift(1) - 1
    df['Change'] = change.shift(-1)
    return df

def simulate_turnover(max_maturity, min_maturity, rates):
    """
    rate is expected to be a pandas dataframe with one column per year
    up to max maturity columns (10 years == 10 columns)
    """
    initial_yields = rates.iloc[0].tolist()
    yields = rates.iterrows()
    #initial_yields = rates['1970'].values.tolist()[0]
    #yields = rates['1970':].iterrows()
    ladder = bootstrap(initial_yields, max_maturity, min_maturity)
    return loop(ladder, yields, max_maturity)
