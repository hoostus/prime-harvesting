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
from .ern import CAPEPercentage
from .add import ADD

# Provide an alias from the modern name to the historical name
ConstantWithdrawals = ConstantDollar

from .abc import WithdrawalStrategy

class BankWrapper(WithdrawalStrategy):
    def __init__(self, wrapped_strategy):
        super().__init__(wrapped_strategy.portfolio, wrapped_strategy.harvest)
        self.wrapped_strategy = wrapped_strategy

    def start(self):
        self.starting_withdrawal = self.wrapped_strategy.start()
        return self.starting_withdrawal

    def next(self):
        next_withdrawal = self.wrapped_strategy.next()

        inflation_adjusted_starting = self.portfolio.inflation * self.starting_withdrawal
        current_excess = next_withdrawal - inflation_adjusted_starting

        # if current_excess > 0 and 'set_excess' in self.wrapped_strategy.harvest.dict():
        #     self.wrapped_strategy.harvest.set_excess(current_excess)

        return min(next_withdrawal, inflation_adjusted_starting)

VPWBank = lambda portfolio, harvest_strategy: BankWrapper(VPW(portfolio, harvest_strategy))
VPWBank.__name__ = 'VPWBank'

def make_constantdollar(rate):
    return type('ConstantDollar_%s' % rate, (ConstantDollar,), {
        '__init__' : lambda self, portfolio, harvesting: ConstantDollar.__init__(self, portfolio, harvesting, rate=rate)
    })

def make_vpw(length):
    return type('VPW_%s' % length, (VPW,), {
        '__init__' : lambda self, portfolio, harvesting: VPW.__init__(self, portfolio, harvesting, years_left=length)
    })

