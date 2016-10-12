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
        series = create_distribution(lambda: montecarlo.conservative[50],
                                     balance, 0, iterations=20000,
                                     year_factory=year_factory)
        #print(series.head())

        print('10th=', "${:,}".format(int(series.quantile(.1))))
        print('50th=', "${:,}".format(int(series.quantile(.5))))

        # For a given income what percentile is it in the distribution?
        income = 50000
        print("${:,}= ".format(income), scipy.stats.percentileofscore(series, income))

    run_main()
