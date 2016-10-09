from .constant_dollar import ConstantDollar
from .constant_percent import ConstantPercentage
from .arva import ARVA
from .pye import RetrenchmentRule
from .simple import SimpleFormula
from .vpw_new import VPW
from .inverted import InvertedWithdrawals, TiltCapital
from .mcclung import EM, ECM
from .sensible import SensibleWithdrawals
from .smoothing import SteinerSmoothing, LonginvestSmoothing, RollingAverageSmoothing, CAPE10Smoothing
from .pmt_prime import PMTPrime
from .rmd import FeelFree, IRS_RMD
from .stout import Model3
from .vanguard import Vanguard
from .clyatt import Clyatt
from .guyton import Guyton
from .floor_ceiling import FloorCeiling

# Provide an alias from the modern name to the historical name
ConstantWithdrawals = ConstantDollar
