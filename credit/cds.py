# Credit default swaps: insurance on a name defaulting.
#
# buyer pays the spread every year while the name is alive (premium leg)
# seller pays (1 - R) if it defaults (protection leg)
# par spread = where the two legs are worth the same today
#
# annual payments, default only at year ends. real CDS pay quarterly and
# trade a fixed coupon plus an upfront, but the maths is the same.

from .bonds import discount_factor
from .default import survival


def risky_annuity(r, lam, years):
    # 1.0 a year, but only while the name's alive: discount x survival, each year
    total = 0.0
    for t in range(1, years + 1):
        total = total + discount_factor(r, t) * survival(lam, t)
    return total


def premium_leg(spread, r, lam, years):
    return spread * risky_annuity(r, lam, years)


def protection_leg(r, lam, years, recovery):
    # paid once, in the year it defaults. chance it defaults IN year t =
    # alive at the start (t - 1) minus alive at the end (t)
    total = 0.0
    for t in range(1, years + 1):
        p_default_this_year = survival(lam, t - 1) - survival(lam, t)
        total = total + (1 - recovery) * p_default_this_year * discount_factor(r, t)
    return total


def par_spread(r, lam, years, recovery):
    # spread x annuity = protection -> spread = protection / annuity.
    # same shape as my autocall's fair coupon: (1 - A) / B, B a risky annuity.
    return protection_leg(r, lam, years, recovery) / risky_annuity(r, lam, years)


def cs01(r, lam, years, notional):
    # value of a 1bp move in the spread. holds the annuity fixed, so it's the
    # small-move number; big moves are smaller because the annuity shrinks.
    return risky_annuity(r, lam, years) * notional / 10_000
