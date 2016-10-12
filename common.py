import itertools
import math
import simulate
import harvesting
import plot

from decimal import setcontext, ExtendedContext
# Don't raise exception when we divide by zero
#setcontext(ExtendedContext)
#getcontext().prec = 5

def compare_prime_vs_rebalancing(series, years=30, title=''):
    (r1, r2) = itertools.tee(series)
    x = simulate.withdrawals(r1, years=years)
    y = simulate.withdrawals(r2, years=years, harvesting=harvesting.N_60_RebalanceHarvesting)

    s1 = [n.withdraw_r for n in x]
    s2 = [n.withdraw_r for n in y]

    ceiling = max(max(s1), max(s2))
    if ceiling < 100000:
        ceiling = int(math.ceil(ceiling / 10000) * 10000)
    else:
        ceiling = int(math.ceil(ceiling / 100000) * 100000)

    plot.plot_two(s1, s2, s1_title='Prime Harvesting', s2_title='Annual Rebalancing',
                       y_lim=[0,ceiling],
                       x_label='Year of Retirement', title=title)
