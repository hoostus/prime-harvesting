from decimal import Decimal
import pandas

_life = pandas.read_csv('2004-period-life-table.csv')

def _lookup(start_age, current_age, key):
    r0 = _life.iloc[start_age][key]
    r1 = _life.iloc[current_age][key]

    r0 = Decimal(r0.replace(',', ''))
    r1 = Decimal(r1.replace(',', ''))
    return (r0, r1)

def male_mortality(current_age, start_age=65):
    (r0, r1) = _lookup(start_age, current_age, 'Male Number of Lives')
    return r1 / r0

def female_mortality(current_age, start_age=65):
    (r0, r1) = _lookup(start_age, current_age, 'Female Number of Lives')
    return r1 / r0

def both_alive(m_age, f_age):
    return male_mortality(m_age) * female_mortality(f_age)
def male_only_alive(m_age, f_age):
    return male_mortality(m_age) * (1 - female_mortality(f_age))
def female_only_alive(m_age, f_age):
    return female_mortality(f_age) * (1 - male_mortality(m_age))
def either_alive(m_age, f_age):
    neither = (1 - male_mortality(m_age)) * (1 - female_mortality(f_age))
    return 1 - neither

import random
import numpy

def die(i):
    if random.random() < either_alive(i, i):
        return die(i+1)
    else:
        # they didn't live to i, so their final
        # age was i-1
        return i - 1

def gen_age():
    return die(65)
