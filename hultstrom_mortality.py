import pandas
import random

# This life table actually comes from
# https://www.kitces.com/joint-life-expectancy-and-mortality-calculator/
# However, upon closer inspection, the numbers don't match up with the
# numbers from the 2004 Period Life Table, so I'm not sure what the source
# is. In general, the numbers here are more grim. e.g. for a 90-year old
# male is says the Death Probability is .181789 but the actual 2004
# Period Life Table says it is only 0.155383

_life = pandas.read_csv('hultstrom-lifetable.csv')

MALE = 0
FEMALE = 1

def survive(age, gender):
  ''' Given an age and a gender, return True if they survive
  to their next birthday. '''

  key = {
    MALE: "Male Death Probability",
    FEMALE : "Female Death Probability"
  }[gender]

  return random.random() > _life.iloc[age][key]
