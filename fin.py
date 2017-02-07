import numpy
import scipy.stats

def gen_paths(S0, r, sigma, T, M, I):
    """ Generates Monte Carlo paths for geometric Brownian motion.

    Parameters
    ==========
    S0: float
        initial stock/index value. Irrelevant if you only care about relative returns
    r: float
        constant short rate ("mean return")
    sigma: float
        constant volatility ("standard deviation")
    T: float
        final time horizon (always specify 1.0?)
    M: int
        number of time steps/intervals
    I: int
        number of paths to be simulated

    Returns
    =======
    paths : ndarray, shape (M+1, I)
    """

    dt = float(T) / M
    paths = numpy.zeros((M+1, I), numpy.float64)
    paths[0] = S0
    for t in range(1, M+1):
        rand = numpy.random.standard_normal(I)
        rand = (rand - rand.mean()) / rand.std()
        paths[t] = paths[t - 1] * numpy.exp(( r - 0.5 * sigma ** 2) * dt + sigma * numpy.sqrt(dt) * rand)
    return paths

if __name__ == '__main__':
    S0 = 100.
    r = 0.05
    sigma = 0.2
    T = 1.0
    M = 50
    I = 250000

    paths = gen_paths(S0, r, sigma, T, M, I)

    log_returns = numpy.log(paths[1:] / paths[0:-1])

    # How to apply metrics.ssr or metrics.pwa to this vectorised?
    print(len(log_returns[0]))
