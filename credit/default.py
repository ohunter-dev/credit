# Default risk.
#
# lam (hazard rate): chance of defaulting in any one year, if it hasn't yet
# survival:          chance it HASN'T defaulted by year t = exp(-lam * t)
# recovery:          what you get back per 1.0 if it does. convention: 40%
#
# credit triangle: spread ~ lam x (1 - R). the spread pays for the expected
# loss each year: how often it happens x how much you lose when it does.

import numpy as np

from .bonds import discount_factor


def survival(lam, t):
    # compounds, it doesn't add up: you can only default once, so each year's
    # chance only applies to the names still alive
    return np.exp(-lam * t)


def default_prob(lam, t):
    return 1 - survival(lam, t)


def hazard_from_spread(spread, recovery):
    # the triangle turned round: 1.2% spread, 40% recovery -> ~2% a year.
    # this is the market-implied (pricing) rate, not a forecast. spreads carry
    # a risk premium, so it usually sits above historical default rates.
    return spread / (1 - recovery)


def risky_zero(face, r, lam, t, recovery):
    # two outcomes at maturity: survives -> face, defaults -> face x R.
    # average them, then discount. (recovery paid at maturity: a simplification)
    S = survival(lam, t)
    return face * discount_factor(r, t) * (S + recovery * (1 - S))
