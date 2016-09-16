from .constant_dollar import ConstantDollar
from .constant_percent import ConstantPercentage
from .arva import ARVA
from .pye import RetrenchmentRule
from .simple import SimpleFormula
from .vpw_new import VPW
from .inverted import InvertedWithdrawals
from .mcclung import EM, ECM
from .sensible import SensibleWithdrawals
from .smoothing import SteinerSmoothing, LonginvestSmoothing, RollingAverageSmoothing, CAPE10Smoothing
from.pmt_prime import PMTPrime

# Provide an alias from the modern name to the historical name
ConstantWithdrawals = ConstantDollar
