from .mcclung import PrimeHarvesting, AltPrimeHarvesting
from .annual_rebalance import AnnualRebalancing, make_rebalancer
from .bondsfirst import BondsFirst
from .age_based import AgeBased, AgeBased_100, AgeBased_110, AgeBased_120, Glidepath
from .omeganot import OmegaNot
from .weiss import Weiss
from .actuarial import ActuarialHarvesting

# Alias for legacy class name.
N_60_RebalanceHarvesting = make_rebalancer(.6)
N_60_RebalanceHarvesting.__name__ = '60% Stocks'

N_100_RebalanceHarvesting = make_rebalancer(1)
N_100_RebalanceHarvesting.__name__ = '100% Stocks'

N_35_RebalanceHarvesting = make_rebalancer(.35)
N_35_RebalanceHarvesting.__name__ = '35% Stocks'
