import pandas
import random

MALE = 0
FEMALE = 1

def gen_age(survival_function, age=65):
    ''' Generates a final age for a couple (male + female) who are both
    65 years old '''

    return omy(True, True, age, survival_function)

def omy(husband, wife, age, survive):
    h_omy = survive(age, MALE)
    w_omy = survive(age, FEMALE)

    husband = (husband and h_omy)
    wife = (wife and w_omy)

    if husband or wife:
        return omy(husband, wife, age + 1, survive)
    else:
        return age

# This life table actually comes from
# https://www.kitces.com/joint-life-expectancy-and-mortality-calculator/
# However, upon closer inspection, the numbers don't match up with the
# numbers from the 2004 Period Life Table, so I'm not sure what the source
# is. In general, the numbers here are more grim. e.g. for a 90-year old
# male is says the Death Probability is .181789 but the actual 2004
# Period Life Table says it is only 0.155383
HULSTROM = 'hultstrom-lifetable.csv'

# This is *actual* 2004 life table. (I think.)
# The top level index is at http://www.cdc.gov/nchs/products/life_tables.htm
NVSS_2004 = '2004-life-table.csv'
# And an updated 2011 version
NVSS_2011 = '2011-life-table.csv'

# The Annuity 2000 life table is different yet again. (It will give even longer
# life spans than the 2004 life table.) The difference is because Annuity 2000
# applies a 10% "loading factor" to try to account for the fact that people who
# buy annuities live longer than people who don't. This is probably the best
# one to use for most testing.
#
# The source was randomly Googled.
ANNUITY_2000 = 'annuity-2000.csv'

def make_mortality(csv_filename):
    life = pandas.read_csv(csv_filename)

    def survive(age, gender):
      ''' Given an age and a gender, return True if they survive
      to their next birthday. '''

      key = {
        MALE: "Male Death Probability",
        FEMALE : "Female Death Probability"
      }[gender]

      return random.random() > life.iloc[age][key]

    return survive
