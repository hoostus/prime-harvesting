from decimal import Decimal
import pandas
import math

_vpw = pandas.read_csv('vpw.csv')
# Keep them all as strings, instead of converting to floats
# Since we prefer Decimal...
for i in range(1, 41):
    _vpw[['Y%d' % i]] = _vpw[['Y%d' % i]].astype(str)

def _lookup(type, year):
    labels = [d[0] for d in _vpw.values]
    i = labels.index(type)

    row = _vpw.iloc[i]
    assert(row[0] == type)
    # row is 0-based but year is 1-based so we can just use it
    # directly like this....
    v = row[year]

    # handle the NaNs from pandas. In practice we only hit them
    # if we've exhausted the entire portfolio. So we should start
    # withdrawing 0% after that....
    if v == 'nan':
        return Decimal(0)
    else:
        return Decimal(v)

s_60_40_30 = [_lookup('60/40 30 years', n) for n in range(1, 41)]
s_60_40_35 = [_lookup('60/40 35 years', n) for n in range(1, 41)]

s_50_50_40 = [_lookup('50/50 40 years', n) for n in range(1, 41)]
s_60_40_40 = [_lookup('60/40 40 years', n) for n in range(1, 41)]
s_70_30_40 = [_lookup('70/30 40 years', n) for n in range(1, 41)]
s_80_20_40 = [_lookup('80/20 40 years', n) for n in range(1, 41)]

vpw_rates = s_60_40_40
