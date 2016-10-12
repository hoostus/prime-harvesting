"""This is based on Suarez et al's "The Perfect Withdrawal Amount" (2014)"""

from decimal import Decimal

import numpy
import pandas

import metrics


def create_distribution(engine_factory, start, end, year_factory=lambda: 30, iterations=20000):
    """ This creates a distribution of maximum withdrawal rates based on the inputs. """
    series = pandas.Series(index=numpy.arange(0, iterations))
    def weight(annual):
        """ We need to convert the AnnualChange to a single number. Assume 60/40 weighting. """
        return (annual.stocks * Decimal('.6')) + (annual.bonds * Decimal('.4'))

    for i in range(iterations):
        engine = engine_factory()
        returns = [weight(engine.random_year()) for _ in range(year_factory())]
        series.iloc[i] = float(metrics.pwa(start, end, returns))
    return series

if __name__ == '__main__':
    def run_main():
        """ For command line testing. """
        import montecarlo
        import mortality
        import scipy.stats

        # Using mortality makes it take A LOT longer
        year_factory = lambda: mortality.gen_lifespan(mortality.DEFAULT_COUPLE)
        year_factory = lambda: 45

        balance = 2473053
        bequest = 500000
        series = create_distribution(lambda: montecarlo.LowYieldsHighValuations(),
                                     balance, bequest, iterations=20000,
                                     year_factory=year_factory)
        #print(series.head())

        print('10th=', "${:,}".format(int(series.quantile(.1))))
        print('20th=', "${:,}".format(int(series.quantile(.2))))
        print('30th=', "${:,}".format(int(series.quantile(.3))))
        print('40th=', "${:,}".format(int(series.quantile(.4))))
        print('50th=', "${:,}".format(int(series.quantile(.5))))

        def print_pct(amount):
            print("${:,}= ".format(amount), scipy.stats.percentileofscore(series, amount))

        # For a given income what percentile is it in the distribution?
        print_pct(50000)
        print_pct(75000)
        print_pct(100000)

    run_main()
