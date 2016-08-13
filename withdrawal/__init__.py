from .constant_dollar import ConstantDollar
from .constant_percent import ConstantPercentage
from .arva import ARVA
from .pye import RetrenchmentRule
from .simple import SimpleFormula
#from .vpw import VPW
from .vpw_new import VPW
from .inverted import InvertedWithdrawals
from .mcclung import EM, ECM
from .sensible import SensibleWithdrawals

# Provide an alias from the modern name to the historical name
ConstantWithdrawals = ConstantDollar
