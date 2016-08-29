from .mcclung import PrimeHarvesting, AltPrimeHarvesting
from .annual_rebalance import AnnualRebalancing, make_rebalancer

# Alias for legacy class name.
N_60_RebalanceHarvesting = make_rebalancer(.6)
