# These are primarily intended to be used with simulate.calc_lens

import metrics
import pandas
import decimal
from decimal import Decimal as D

def calc_pwa0(annual_data):
    return metrics.pwa(1, 0, [n.returns_r for n in annual_data])

def calc_pwa1(annual_data):
    return metrics.pwa(1, 1, [n.returns_r for n in annual_data])

def calc_success(annual_data):
    # it is success if the last withdrawal is the same as the first withdrawal...otherwise
    # we must have cut spending somewhere along the line
    # We have to put in a $1 fudge factor for floating point weirdness...
    last_wd = annual_data[-1].withdraw_r
    first_wd = annual_data[0].withdraw_r
    return last_wd >= (first_wd - 1)

def calc_shortfall_years(annual):
    df = pandas.DataFrame(annual)
    # subtract $1 to deal with floating point weirdness (sometimes $40 turns into $39.9999)
    failed = df[df['withdraw_r'] < df['withdraw_r'][0] - 1]
    s_y = len(failed)
    return s_y

def calc_years_sustained(annual):
    df = pandas.DataFrame(annual)
    # subtract $1 to deal with floating point weirdness (sometimes $40 turns into $39.9999)
    failed = df[df['withdraw_r'] < df['withdraw_r'][0] - 1]
    s_y = len(failed)
    
    if s_y:
        return -s_y
    else:
        b_t = df.tail(1)['portfolio_post'].item().value_r
        b_y = b_t / df['withdraw_r'][0]
        return b_y
    
def calc_ulcer(annual):
    df = pandas.DataFrame(annual)
    vals = df['portfolio_pre'].get_values()
    ulcer = metrics.ulcer([p.value_r for p in vals])
    return ulcer

def calc_bond_pct(annual):
    df = pandas.DataFrame(annual)
    with decimal.localcontext(decimal.ExtendedContext) as context:
        vals = df['portfolio_pre'].get_values()
        # this arrives as an ndarray but pandas wants a real list
        p = pandas.DataFrame(data=list(vals))
        bonds_pct = p['bonds'] / p['value_n']
    return bonds_pct.mean()

def calc_hreff(annual, floor=D('.04')):
    df = pandas.DataFrame(annual)
    withdrawals = df['withdraw_pct_orig'].tolist()
    returns = df['returns_r'].tolist()
    return metrics.hreff(withdrawals, returns, floor=floor)

def calc_max_wd(annual):
    df = pandas.DataFrame(annual)
    return df['withdraw_pct_cur'].max()

def calc_cew(annual):
    df = pandas.DataFrame(annual)
    return metrics.cew(df['withdraw_r'].tolist())

def calc_dras(series, years):
    L = years

    # how many had shortfall years?
    failures = series[series < 0]
    successes = series[series >= 0]
    p_fail = len(failures) / len(series)        
    
    s_y = failures.mean()
    b_y = successes.mean()
    e_ys = (p_fail * (L + s_y)) + ((1 - p_fail) * (L + b_y))
    # semi-deviation with respect to length of retirement
    ssd_l_ys = (p_fail * s_y * s_y) ** 1/2
    
    d_ras = e_ys / ssd_l_ys
    return d_ras
    
def calc_coverage_ratio(annual, years):
    s_y = calc_years_sustained(annual)
    L = years
    c = s_y / L

    def u(c, risk_aversion=D('0.9999'), penalty_coeff=D(10)):
        c = D(c)
        if c >= 1:
            numerator = (c ** (1 - risk_aversion)) - 1
            denominator = 1 - risk_aversion
            return numerator / denominator
        else:
            numerator = (1 ** (1 - risk_aversion)) - 1
            denominator = 1 - risk_aversion
            penalty = penalty_coeff * (1 - c)
            return (numerator / denominator) - penalty

    return u(c)
