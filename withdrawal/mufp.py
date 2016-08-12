from decimal import Decimal

def get_extended_mufp(years_left):
    assert years_left > 0

    if years_left > 50:
        return Decimal('5.1')
    else:
        return extended_mufp_table[years_left] / 100

# The index is the number of years remaining, so 1 year remaining = 17.7%
extended_mufp_table = [
    None,
    Decimal('17.7'),
    Decimal('17.7'),
    Decimal('17.7'),
    Decimal('14.3'),
    Decimal('14.3'),
    Decimal('13.0'),
    Decimal('13.0'),
    Decimal('13.0'),
    Decimal('11.3'),
    Decimal('11.3'),
    Decimal('10.3'),
    Decimal('10.3'),
    Decimal('9.7'),
    Decimal('9.7'),
    Decimal('9.2'),
    Decimal('8.7'),
    Decimal('8.7'),
    Decimal('8.3'),
    Decimal('7.9'),
    Decimal('7.9'),
    Decimal('7.5'),
    Decimal('7.1'),
    Decimal('6.9'),
    Decimal('6.9'),
    Decimal('6.6'),
    Decimal('6.4'),
    Decimal('6.3'),
    Decimal('6.1'),
    Decimal('6.0'),
    Decimal('5.9'),
    Decimal('5.8'),
    Decimal('5.8'),
    Decimal('5.7'),
    Decimal('5.6'),
    Decimal('5.6'),
    Decimal('5.5'),
    Decimal('5.5'),
    Decimal('5.4'),
    Decimal('5.4'),
    Decimal('5.4'),
    Decimal('5.3'),
    Decimal('5.3'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.2'),
    Decimal('5.1'),
    Decimal('5.1'),
    Decimal('5.1')
    ]
