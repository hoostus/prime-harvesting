import pandas
import random
import collections

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
HULSTROM = 'mortality/hultstrom-lifetable.csv'

# This is *actual* 2004 life table. (I think.)
# The top level index is at http://www.cdc.gov/nchs/products/life_tables.htm
NVSS_2004 = 'mortality/2004-life-table.csv'
# And an updated 2011 version
NVSS_2011 = 'mortality/2011-life-table.csv'

# The Annuity 2000 life table is different yet again. (It will give even longer
# life spans than the 2004 life table.) The difference is because Annuity 2000
# applies a 10% "loading factor" to try to account for the fact that people who
# buy annuities live longer than people who don't. This is probably the best
# one to use for most testing.
#
# The source was randomly Googled.
ANNUITY_2000 = 'mortality/annuity-2000.csv'

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

Person = collections.namedtuple("Person", "age gender")

def gen_lifespan(people, survival_fn=None):
    """ People is a an array of Persons which are just a tuple of age and gender
    [ (age, gender), (age, gender), ...]

    This allows us to check for same-sex couples,
    couples with different ages, and so on easily
    """
    if not survival_fn:
        survival_fn = make_mortality(ANNUITY_2000)
    def g(year, people, survival_fn):
        if len(people) == 0:
            return year
        else:
            new_people = [person for person in people if survival_fn(person.age + year, person.gender)]
            return g(year+1, new_people, survival_fn)

    return g(0, people, survival_fn)

DEFAULT_COUPLE = [Person(age=65, gender=MALE), Person(age=63, gender=FEMALE)]
SINGLE_MALE = [Person(age=65, gender=MALE)]

def make_mortality_rate(source=ANNUITY_2000):
    life = pandas.read_csv(source)

    def f(age, gender):
        key = {
            MALE: "Male Death Probability",
            FEMALE : "Female Death Probability"
        }[gender]

        return life.iloc[age][key]

    return f

def life_expectancy(male_age, female_age):
    """
        Passing in None instead of an age calculates single life
        expectancy
    """
    life = pandas.read_csv(ANNUITY_2000)

    def alive_at_age(gender, age):
        key = {
            MALE: "Male Lives",
            FEMALE : "Female Lives"
        }[gender]

        return life.iloc[age][key]

    def T(gender, age):
        """ Sum up all of the years lived by people alive in this cohort """
        sum = 0
        for i in range(116-age):
            sum += alive_at_age(gender, age + i)
        return sum

    if male_age and female_age:
        raise NotImplementedError
        # Doing this is wrong. This just creates a blended population.
        # I looked at what aacalc does and...it seems too complex. There must be a simpler solution to this.
        #return (T(MALE, male_age) + T(FEMALE, female_age)) / (alive_at_age(MALE, male_age) + alive_at_age(FEMALE, female_age))
    elif male_age:
        return T(MALE, male_age) / alive_at_age(MALE, male_age)
    else:
        return T(FEMALE, female_age) / alive_at_age(FEMALE, female_age)
