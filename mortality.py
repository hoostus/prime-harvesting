import hultstrom_mortality as h

def gen_age(age=65):
    ''' Generates a final age for a couple (male + female) who are both
    65 years old '''

    return omy(True, True, age)

def omy(husband, wife, age):
    h_omy = h.survive(age, h.MALE)
    w_omy = h.survive(age, h.FEMALE)

    husband = (husband and h_omy)
    wife = (wife and w_omy)

    if husband or wife:
        return omy(husband, wife, age + 1)
    else:
        return age
