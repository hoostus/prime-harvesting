from .mcclung import PrimeHarvesting, AltPrimeHarvesting
from .annual_rebalance import AnnualRebalancing
from .bondsfirst import BondsFirst
from .age_based import AgeBased, AgeBased_100, AgeBased_110, AgeBased_120, Glidepath, InverseGlidepath, ParameterGlidepath
from .omeganot import OmegaNot
from .weiss import Weiss
from .actuarial import ActuarialHarvesting
from .woodspinner import WoodSpinner

def make_omeganot(stock_ceiling):
    return type('OmegaNot_%s' % int((stock_ceiling*100)), (OmegaNot,), {
        '__init__' : lambda self, portfolio: OmegaNot.__init__(self, portfolio, ceiling=stock_ceiling)
        })

def make_rebalancer(stock_pct):
    return type('AnnualRebalancer_%s' % int((stock_pct*100)), (AnnualRebalancing,), {
        '__init__' : lambda self, portfolio: AnnualRebalancing.__init__(self, portfolio, stock_pct)
        })

# Alias for legacy class name.
N_0_RebalanceHarvesting = make_rebalancer(0)
N_35_RebalanceHarvesting = make_rebalancer(.35)
N_60_RebalanceHarvesting = make_rebalancer(.6)
N_80_RebalanceHarvesting = make_rebalancer(.8)
N_100_RebalanceHarvesting = make_rebalancer(1)


