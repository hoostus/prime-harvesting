from decimal import Decimal
from adt import report, AnnualChange
from mufp import get_extended_mufp
from vpw import vpw_rates
import math
from metrics import pmt

# Things I don't like...
# - Lots of repeated logic
# - The initial withdrawal
# - Adjusting portfolio gains
# - The overall looping logic

class WithdrawalStrategy():
    def __init__(self, portfolio, harvest_strategy, **kwargs):
        self.portfolio = portfolio
        self.harvest = harvest_strategy
        self.cumulative_inflation = Decimal('1.0')

    def withdrawals(self):
        pass

class SimpleFormula(WithdrawalStrategy):
    """
    This comes from Blanchett's 'Simple Formulas to Implement Complex Withdrawal Strategies'
    https://www.onefpa.org/journal/Pages/Simple%20Formulas%20to%20Implement%20Complex%20Withdrawal%20Strategies.aspx
    """
    def __init__(self, portfolio, harvest_strategy, probability_of_success=.95, alpha=0, years=35, **kwargs):
        super().__init__(portfolio, harvest_strategy, **kwargs)

        # the target probability of success (i.e. "I want a 95% chance of succeeding")
        self.pos = probability_of_success

        # the alpha parameters allows you to include advisors fees and adjust
        # the capital market expectations; Blanchett used 10% for equities and
        # 4% for bonds.
        self.alpha = alpha

        # How long we expect the strategy to run for...
        self.years = years

    def rmd(self, years):
        return Decimal(1) / years

    def get_pct(self, years):
        if years < 15:
            # Just like with VPW, we need to add a hack to handle
            # unexpected longevity.
            if years < 2:
                return Decimal('0.5')
            else:
                return self.rmd(years)
        else:
            return self.dynamic(years)

    def dynamic(self, years):
        """
        In the paper Blanchett lists the intercept at 0.195
        and the longevity coeff at 0.3701. But if you use those
        numbers in his formula you get a different result than
        what he discusses in the paper (you get a 3.17% withdrawal rate
        instead of a 3.15% withdrawal rate for the scenario he first
        discusses).

        That confused me because I couldn't figure out why. But Blanchett
        also provides an Excel spreadsheet which implements the formula.
        In the spreadsheet he uses slightly different numbers for intercept
        and longevity. The numbers below come from the spreadsheet.

        Spreadsheet: http://www.davidmblanchett.com/tools
        """
        intercept = 0.19477105724498
        longevity_coeff = .0370089932678766
        equity_coeff = .01255
        probability_coeff = .04471
        alpha_coeff = .507
        equity_percent = self.portfolio.stocks / self.portfolio.value
        return Decimal(intercept
            - (longevity_coeff * math.log(years))
            + (equity_coeff * math.sqrt(equity_percent))
            - (probability_coeff * self.pos)
            + (alpha_coeff * self.alpha))

    def withdrawals(self):
        rate = self.get_pct(self.years)
        withdrawal = rate * self.portfolio.value
        actual_withdrawal = self.harvest.send(withdrawal)
        self.years -= 1

        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            previous_portfolio_amount = self.portfolio.value
            (gains, _, _) = self.portfolio.adjust_returns(change)

            rate = self.get_pct(self.years)
            withdrawal = rate * self.portfolio.value
            actual_withdrawal = self.harvest.send(withdrawal)
            self.years -= 1

            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)


class ConstantWithdrawals(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.04')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate
        self.initial_withdrawal = portfolio.value * rate

    def withdrawals(self):
        withdrawal = self.portfolio.value * self.rate
        actual_withdrawal = self.harvest.send(withdrawal)
        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            previous_portfolio_amount = self.portfolio.value
            (gains, _, _) = self.portfolio.adjust_returns(change)

            self.cumulative_inflation *= (1 + change.inflation)

            withdrawal = self.initial_withdrawal * self.cumulative_inflation
            actual_withdrawal = self.harvest.send(withdrawal)

            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

class VPW(WithdrawalStrategy):
    def calc_withdrawal(portfolio_value, year):
        return vpw_rates[year] * portfolio_value

    def withdrawals(self):
        index = 0
        withdrawal = VPW.calc_withdrawal(self.portfolio.value, index)
        actual_withdrawal = self.harvest.send(withdrawal)

        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        index += 1

        while True:
            (gains, _, _) = self.portfolio.adjust_returns(change)

            if index < len(vpw_rates):
                withdrawal = vpw_rates[index] * self.portfolio.value
            else:
                # VPW ran out of money. You might think this is unfair to VPW.
                # "But someone who is 98 and still alive would replan!"
                # But other strategies aren't allowed to do ad hoc replanning
                # (e.g. constant dollar withdrawals) when things start to look
                # dire. Instead of adding ad hoc replanning to ONE method...
                # we just let it fail.
                withdrawal = 0
            actual_withdrawal = self.harvest.send(withdrawal)

            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

            index += 1

class RetrenchmentRule(WithdrawalStrategy):
    """ Gorden Pye's retrenchment rule is another PMT based solution. """
    def __init__(self, portfolio, harvest_strategy, **kwargs):
        super().__init__(portfolio, harvest_strategy, **kwargs)

        self.discount_rate = .08
        self.final_age = 110

    def withdrawals(self):
        # This assumes you are starting at age 65. There is no good way to
        # use a different starting age here. Something like that really needs
        # to be baked into the superclass. But that would require a bigger
        # refactoring.....
        current_age = 65
        withdrawal = pmt(self.discount_rate, self.final_age - current_age, self.portfolio.value)
        actual_withdrawal = self.harvest.send(withdrawal)
        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            previous_portfolio_amount = self.portfolio.value
            (gains, _, _) = self.portfolio.adjust_returns(change)

            current_age += 1
            if current_age < self.final_age:
                withdrawal = pmt(self.discount_rate, self.final_age - current_age, self.portfolio.value)
            else:
                # We ran out of money and are still alive :(
                withdrawal = 0
            actual_withdrawal = self.harvest.send(withdrawal)
            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)


class ARVA(WithdrawalStrategy):
    """ This comes from Siegel and Waring's 'Only Spending Rule You'll Ever Need' (2014)
    https://larrysiegeldotorg.files.wordpress.com/2014/09/siegel_waring_only-spending-rule-article-youll-ever-need.pdf

    Which is basically PMT, the same underlying rule as in VPW.

    However, Siegel and Waring have different suggestions about how the discount_rate and "number of years"
    should be calculated, so this has their defaults baked in.
    """
    def __init__(self, portfolio, harvest_strategy, discount_rate=Decimal('.02')):
        # Siegel & Waring seem to suggest the discount rate should be
        # "TIPS interest rate (present-value-weighted average interest rate across the TIPS
        # ladder)" at the start of each year.
        # Currently, we don't support changing the discount_rate every year and use a constant rate
        super().__init__(portfolio, harvest_strategy)

        self.discount_rate = discount_rate

    # every year we need to
    # Siegel & Waring suggest using the average of 120 (the maximum known human life span) and
    # life expectancy based on current age according to the Social Security tables
    # years_remaining = average(120, mean_life_expectancy)
    # -numpy.pmt(discount_rate, years_remaining, portfolio.value, 0, 'start')

    # Siegel & Waring's suggestion to continually update the assumptions make this
    # tricky to model well


# This one is super-simple...just take a constant percentage every
# year. Don't try to index for inflation. So it will vary as the portfolio
# value varies...
class ConstantPercentage(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.04')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate

    def withdrawals(self):
        withdrawal = self.portfolio.value * self.rate
        actual_withdrawal = self.harvest.send(withdrawal)
        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            previous_portfolio_amount = self.portfolio.value
            (gains, _, _) = self.portfolio.adjust_returns(change)

            withdrawal = self.portfolio.value * self.rate
            actual_withdrawal = self.harvest.send(withdrawal)
            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)


class InvertedWithdrawals(WithdrawalStrategy):
    """ Based on "Inverted Withdrawal Rates and the Sequence of Returns Bonus" (Walton, 2016)
    published in Advistor Perspectives[1]

    [1]: https://www.mendeley.com/viewer/?fileId=72897973-b53f-d335-4d49-e46159445e8f&documentId=8c71b8a2-8422-3612-8b24-ecac0c7e2019
    """
    def __init__(self, portfolio, harvest_strategy, rate=Decimal('0.04'), tilt=Decimal('.01')):
        super().__init__(portfolio, harvest_strategy)

        self.rate = rate
        self.tilt = tilt
        self.starting_portfolio_value = portfolio.value

    def withdrawals(self):
        # we start out with the default withdrawal rate.
        # n.b. that this is the ONLY time it is used. Every other
        # time we will use a tilt because we will either be above or
        # below this value
        withdrawal = self.portfolio.value * self.rate
        actual_withdrawal = self.harvest.send(withdrawal)
        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            previous_portfolio_amount = self.portfolio.value
            self.portfolio.adjust_returns(change)
            gains = (self.portfolio.value - previous_portfolio_amount) / previous_portfolio_amount

            self.cumulative_inflation *= (1 + change.inflation)

            # Figure out which tilt we used based on the current (inflation-adjusted)
            # portfolio value
            if (self.portfolio.value / self.cumulative_inflation) < self.starting_portfolio_value:
                withdrawal = self.portfolio.value * (self.rate - self.tilt)
            else:
                withdrawal = self.portfolio.value * (self.rate + self.tilt)

            actual_withdrawal = self.harvest.send(withdrawal)

            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

class EM(WithdrawalStrategy):
    DEFAULT_SCALE_RATE = Decimal('.95')
    DEFAULT_FLOOR_RATE = Decimal('.025')
    DEFAULT_CAP_RATE = Decimal('1.5')
    DEFAULT_INITIAL_WITHDRAWAL_RATE = Decimal('.05')

    def __init__(self, portfolio, harvest_strategy,
                 scale_rate=DEFAULT_SCALE_RATE,
                 floor_rate=DEFAULT_FLOOR_RATE,
                 cap_rate=DEFAULT_CAP_RATE,
                 initial_withdrawal_rate=DEFAULT_INITIAL_WITHDRAWAL_RATE,
                 years_left=40,
                 **kwargs):
        super().__init__(portfolio, harvest_strategy, **kwargs)

        self.scale_rate = scale_rate
        self.floor_rate = floor_rate
        self.cap_rate = cap_rate
        self.initial_withdrawal_rate = initial_withdrawal_rate
        self.years_left = years_left

    def calc_withdrawal(portfolio_value, years_left,
                        scale_rate=DEFAULT_SCALE_RATE,
                        floor_rate=DEFAULT_FLOOR_RATE,
                        cap_rate=DEFAULT_CAP_RATE,
                        initial_withdrawal_rate=DEFAULT_INITIAL_WITHDRAWAL_RATE):
        adjusted_cap_rate = cap_rate * initial_withdrawal_rate
        # first year
        withdrawal = initial_withdrawal_rate * portfolio_value
        inflation_adjusted_withdrawal_amount = withdrawal
        (portfolio_value, inflation) = yield withdrawal

        while True:
            inflation_adjusted_withdrawal_amount = inflation_adjusted_withdrawal_amount * (1 + inflation)

            withdrawal_rate = get_extended_mufp(years_left)
            withdrawal = withdrawal_rate * portfolio_value

            scale_boundary = Decimal('.75') * inflation_adjusted_withdrawal_amount
            if withdrawal > scale_boundary:
                scale_diff = withdrawal - scale_boundary
                scale_ratio = scale_diff / scale_boundary
                if scale_ratio > 1:
                    scale_ratio = Decimal('1.0')
                withdrawal = scale_boundary + (scale_diff * scale_ratio * scale_rate)

            cap_amount = (adjusted_cap_rate / initial_withdrawal_rate) * inflation_adjusted_withdrawal_amount
            withdrawal = min(withdrawal, cap_amount)

            floor_amount = (floor_rate / initial_withdrawal_rate) * inflation_adjusted_withdrawal_amount
            withdrawal = max(withdrawal, floor_amount)

            (portfolio_value, inflation) = yield withdrawal

            years_left -= 1
            # if we go more than 40 years, just keep pretending we're still in the final year....
            if years_left < 1:
                years_left = 1

    def withdrawals(self):
        em = EM.calc_withdrawal(self.portfolio.value, self.years_left)
        withdrawal = em.send(None)
        actual_withdrawal = self.harvest.send(withdrawal)

        change = yield report(self.portfolio, actual_withdrawal, None)
        assert isinstance(change, AnnualChange)

        while True:
            (gains, _, _) = self.portfolio.adjust_returns(change)
            self.cumulative_inflation *= (1 + change.inflation)

            withdrawal = em.send((self.portfolio.value, change.inflation))
            actual_withdrawal = self.harvest.send(withdrawal)
            change = yield report(self.portfolio, actual_withdrawal, gains)
            assert isinstance(change, AnnualChange)

def ECM(portfolio, harvest_strategy):
    return EM(portfolio, harvest_strategy, scale_rate=Decimal('.6'), floor_rate=Decimal('.025'))

# TODO: this class needs to be updated to work like VPW and EM in the
# new style.
class SensibleWithdrawals(WithdrawalStrategy):
    def __init__(self, portfolio, harvest_strategy, extra_return_boost=Decimal('.31'), initial_rate=Decimal('.05')):
        super().__init__(portfolio, harvest_strategy)

        self.initial_withdrawal = initial_rate * portfolio.value
        self.extra_return_boost = extra_return_boost
        self.initial_rate = initial_rate

    def withdrawals(self):
        change = yield
        while True:
            # portfolio growth
            previous_portfolio_amount = self.portfolio.value
            self.portfolio.adjust_returns(change)
            gains = (self.portfolio.value - previous_portfolio_amount) / previous_portfolio_amount

            # start gummy's calculations
            self.cumulative_inflation *= (1 - change.inflation)

            inflation_adjusted_withdrawal_amount = self.initial_withdrawal / self.cumulative_inflation
            current_withdrawal_amount = inflation_adjusted_withdrawal_amount * .8

            base_portfolio_value = self.portfolio.value - current_withdrawal_amount
            previous_portfolio_amount *= (1 + change.inflation)
            extra_return = base_portfolio_value - previous_portfolio_amount

            if extra_return > 0:
                current_withdrawal_amount += extra_return * self.extra_return_boost

            current_withdrawal_amount = min(current_withdrawal_amount, self.portfolio.value)

            self.harvest.harvest(current_withdrawal_amount)

            change = yield YearlyResults(withdraw_n = current_withdrawal_amount,
                             withdraw_r = current_withdrawal_amount * self.cumulative_inflation,
                             withdraw_pct = current_withdrawal_amount / (self.portfolio.value + current_withdrawal_amount),
                             portfolio_n = self.portfolio.value,
                             portfolio_r = self.portfolio.real_value,
                             returns = gains)
            assert isinstance(change, AnnualChange)
