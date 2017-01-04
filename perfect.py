"""This is based on Suarez et al's "The Perfect Withdrawal Amount" (2014)"""

from decimal import Decimal

import numpy
import pandas

import metrics

def sixty_forty(annual):
    """ We need to convert the AnnualChange to a single number. Assume 60/40 weighting. """
    return (annual.stocks * Decimal('.6')) + (annual.bonds * Decimal('.4'))

def create_distribution(engine_factory, start, end, weight_factory=sixty_forty, year_factory=lambda: 30, iterations=20000):
    """ This creates a distribution of maximum withdrawal rates based on the inputs. """
    series = pandas.Series(index=numpy.arange(0, iterations))

    for i in range(iterations):
        engine = engine_factory()
        returns = [weight_factory(engine.random_year()) for _ in range(year_factory())]
        series.iloc[i] = float(metrics.pwa(start, end, returns))
    return series

def get_rate_at(d):
    q = int(series.quantile(d))
    return (q/balance)

def sim_lots():
    import montecarlo
    import dms
    import scipy.stats
    import itertools

    retirement_lengths = [20, 25, 30, 35, 40, 45, 50, 55, 60]

    return_simulators = [
        (lambda: montecarlo.historical[100], 'Historical 100'),
        (lambda: montecarlo.historical[60], 'Historical 60'),
        (lambda: montecarlo.historical[0], 'Historical 0'),
        (lambda: montecarlo.conservative[100], 'Conservative 100'),
        (lambda: montecarlo.conservative[60], 'Conservative 60'),
        (lambda: montecarlo.conservative[0], 'Conservative 0'),
        (montecarlo.LowYieldsHighValuations, 'Low Yields High Valuations 60/40'),
        (montecarlo.LowYieldsAutoRegression, 'Low Yields 60/40'),
        (lambda: montecarlo.RA_high_vol, 'RA High Vol'),
        (lambda: montecarlo.RA_medium_vol, 'RA Medium Vol'),
        (lambda: montecarlo.RA_low_vol, 'RA Low Vol'),
        (lambda: montecarlo.DMSLogNormalReturns(dms.world), 'DMS World 60/40'),
        ]

    bequests = [0, .25, .50, .75, 1]

    total_sims = len(retirement_lengths) * len(return_simulators) * len(bequests)

    df = pandas.DataFrame(index=numpy.arange(0, total_sims), columns=('length', 'returns', 'bequest', '1-in-200', '1st', '5th', '10th', '50th'))

    i = 0
    for (years, returns, bequest) in itertools.product(retirement_lengths, return_simulators, bequests):
        balance = 1000000
        print(i, total_sims)
        series = create_distribution(returns[0],
            balance,
            Decimal(balance * bequest),
            iterations = 20000,
            year_factory=lambda: years)

        def get_rate_at(d):
            q = int(series.quantile(d))
            return (q/balance)


        df.iloc[i] = (years, returns[1], bequest, get_rate_at(.005), get_rate_at(.01), get_rate_at(.05), get_rate_at(.1), get_rate_at(.5))
        i += 1

        # Save after each row...why not?
        df.to_csv('mega-swr.csv')

def make_table():
    import montecarlo
    import mortality
    import scipy.stats

    df = pandas.DataFrame(index=numpy.arange(30, 61), columns=('1-in-200', '1st', '5th', '10th', '20th', '30th', '40th', '50th', '60th', '70th', '80th', '90th'))

    for i in range(10, 61):
        print('Running', i)
        year_factory = lambda: i
        balance = 1000000
        bequest = 0 #int(balance/10)
        series = create_distribution(lambda: montecarlo.conservative[50],
                                    balance, bequest, iterations=20000,
                                    year_factory=year_factory)

        def get_rate_at(d):
            q = int(series.quantile(d))
            return (q/balance)

        df.loc[i] = {
            '1-in-200' : get_rate_at(.005),
            '1st' : get_rate_at(.01),
            '5th' : get_rate_at(.05),
            '10th' : get_rate_at(.1),
            '20th' : get_rate_at(.2),
            '30th' : get_rate_at(.3),
            '40th' : get_rate_at(.4),
            '50th' : get_rate_at(.5),
            '60th' : get_rate_at(.6),
            '70th' : get_rate_at(.7),
            '80th' : get_rate_at(.8),
            '90th' : get_rate_at(.9),
        }
    df.to_csv('pwa_all.csv')

def run_main():
    """ For command line testing. """
    import montecarlo
    import mortality
    import scipy.stats

    # Using mortality makes it take A LOT longer
    #year_factory = lambda: mortality.gen_lifespan(mortality.DEFAULT_COUPLE)
    year_factory = lambda: 99-41

    #survival_fn = mortality.make_mortality(mortality.ANNUITY_2000)
    #couple = [mortality.Person(age=41, gender=mortality.MALE),
    #          mortality.Person(age=26, gender=mortality.FEMALE)]
    #year_factory = lambda: mortality.gen_lifespan(couple, survival_fn=survival_fn)

    balance = 2473053
    bequest = 0
    series = create_distribution(lambda: montecarlo.conservative[50],
                                    balance, bequest, iterations=20000,
                                    year_factory=year_factory)
    #print(series.head())

    def print_quantile(d):
        q = int(series.quantile(d))
        print('%dth=' % (d * 100), "${:,}".format(q), '(%.2f%%)' % (q/balance*100))

    print_quantile(.01)
    print_quantile(.05)
    print_quantile(.1)
    print_quantile(.2)
    print_quantile(.3)
    print_quantile(.4)
    print_quantile(.5)

    def print_pct(amount):
        print("${:,}= ".format(amount), scipy.stats.percentileofscore(series, amount))

    # For a given income what percentile is it in the distribution?
    print_pct(50000)
    print_pct(75000)
    print_pct(100000)
    print_pct(200000)

if __name__ == '__main__':
    #run_main()
    #make_table()
    sim_lots()

