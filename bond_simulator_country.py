import numpy
import pandas
import math

import pandas_datareader.data as web
import datetime
import requests
import requests_cache
import xlrd
import tempfile
import itertools

from bond_simulator import simulate_monthly_turnover

def get_xls(url, **xls_params):
    expire_after = datetime.timedelta(days=3)
    session = requests_cache.CachedSession(cache_name='data-cache', backend='sqlite', expire_after=expire_after)
    r = session.get(url, stream=True)
    with tempfile.NamedTemporaryFile(suffix='.xls') as tmp:
        for chunk in r.iter_content(chunk_size=1024):
            tmp.write(chunk)
        tmp.flush()
        df = pandas.read_excel(tmp.name, engine='xlrd', **xls_params)
    return df

def get_fred(fred_series):
    expire_after = datetime.timedelta(days=3)
    session = requests_cache.CachedSession(cache_name='data-cache', backend='sqlite', expire_after=expire_after)
    
    start = datetime.datetime(1800, 1, 1)
    df = web.DataReader(fred_series, "fred", start, session=session)
    return df

def sim_uk(save=False):
    print('Simulating UK bond returns')

    boe = get_xls('http://www.bankofengland.co.uk/statistics/Documents/yieldcurve/uknom_mend.xlsx',
        index_col=0, skip_rows=3, sheetname='3. spot, short end')
    print(boe.head())

def sim_aus(save=False):
    print('Simulating Australian bond returns')

    rba = get_xls('http://www.rba.gov.au/statistics/tables/xls-hist/f02histhist.xls',
        index_col=0, skiprows=10)

    rate_matrix = pandas.DataFrame(data=math.nan, index=rba.index, columns=numpy.arange(1, 121))
    rate_matrix[2*12] = rba['FCMYGBAG2']
    rate_matrix[3*12] = rba['FCMYGBAG3']
    rate_matrix[5*12] = rba['FCMYGBAG5']
    rate_matrix[10*12] = rba['FCMYGBAG10']

    rate_matrix.interpolate(axis=1, inplace=True)
    rate_matrix.fillna(axis=1, method='backfill', inplace=True)

    rate_matrix = rate_matrix.applymap(lambda x: x / 100)

    sim_results = simulate_monthly_turnover(10, 4, rate_matrix)
    print(sim_results.head())

    if save:
        sim_results.to_csv('bonds-monthly-australia-rba.csv')

def sim_japan(save=False):
    print('Simulating Japan bond returns')
    # All FRED data can be found at https://fred.stlouisfed.org/series/SERIES_NAME
    FRED_SERIES = [
        'INTGSBJPM193N', # 1966-2016 Interest Rates, Government Securities, Government Bonds for Japan
        'INTGSTJPM193N', # 1955-2016 Interest Rates, Government Securities, Treasury Bills for Japan
    ]

    fred = get_fred(FRED_SERIES)

    rate_matrix = pandas.DataFrame(data=math.nan, index=fred.index, columns=numpy.arange(1, 121))
    rate_matrix[3] = fred['INTGSTJPM193N']
    rate_matrix[10*12] = fred['INTGSBJPM193N']

    rate_matrix.interpolate(axis=1, inplace=True)
    rate_matrix.fillna(axis=1, method='backfill', inplace=True)

    rate_matrix = rate_matrix.applymap(lambda x: x / 100)

    sim_results = simulate_monthly_turnover(10, 4, rate_matrix)
    print(sim_results.head())

    if save:
        sim_results.to_csv('bonds-monthly-japan-fred.csv')


if __name__ == '__main__':
    #sim_uk()
    sim_aus(save=False)
    #sim_japan(save=False)