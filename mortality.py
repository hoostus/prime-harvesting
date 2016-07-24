from decimal import Decimal
import pandas
import random

_life = pandas.read_csv('2004-period-life-table.csv')

def _lookup(start_age, current_age, key):
    r0 = _life.iloc[start_age][key]
    r1 = _life.iloc[current_age][key]

    r0 = Decimal(r0.replace(',', ''))
    r1 = Decimal(r1.replace(',', ''))
    return (r0, r1)

def male_mortality(start_age, current_age):
    (r0, r1) = _lookup(start_age, current_age, 'Male Number of Lives')
    return r1 / r0

def female_mortality(start_age, current_age):
    (r0, r1) = _lookup(start_age, current_age, 'Female Number of Lives')
    return r1 / r0

def both_alive(start_age, current_age):
    return male_mortality(start_age, current_age) * female_mortality(start_age, current_age)
def male_only_alive(start_age, current_age):
    return male_mortality(start_age, current_age) * (1 - female_mortality(start_age, current_age))
def female_only_alive(start_age, current_age):
    return female_mortality(start_age, current_age) * (1 - male_mortality(start_age, current_age))
def either_alive(start_age, current_age):
    neither = (1 - male_mortality(start_age, current_age)) * (1 - female_mortality(start_age, current_age))
    return 1 - neither

def die(start_age, current_age):
    if random.random() < either_alive(start_age, current_age):
        return die(start_age, current_age + 1)
    else:
        return current_age

def gen_age():
    return die(65, 65)
