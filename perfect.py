# This is based on Suarez et al's "The Perfect Withdrawal Amount" (2014)

import metrics
from decimal import Decimal
import pandas
import numpy
import mortality

def create_distribution(engine_factory, start, end, year_factory=lambda: 30, iterations=20000):
    series = pandas.Series(index=numpy.arange(0, iterations))
    def weight(annual):
        return (annual.stocks * Decimal('.6')) + (annual.bonds * Decimal('.4'))

    for i in range(iterations):
        e = engine_factory()
        r = [weight(e.random_year()) for _ in range(year_factory())]
        series.iloc[i] = float(metrics.pwa(start, end, r))
    return series

if __name__ == '__main__':
    import montecarlo
    import scipy.stats

    balance = 2473053
    series = create_distribution(lambda: montecarlo.conservative[50],
        balance, 0,
        iterations=20000, year_factory=lambda: 45)
    #print(series.head())

    # Using mortality makes it take A LOT longer
    #year_factory=lambda: mortality.gen_lifespan(mortality.DEFAULT_COUPLE))

    print('10th=', "${:,}".format(int(series.quantile(.1))))
    print('50th=', "${:,}".format(int(series.quantile(.5))))

    # For a given income what percentile is it in the distribution?
    income = 50000
    print("${:,}= ".format(income), scipy.stats.percentileofscore(series, income))
