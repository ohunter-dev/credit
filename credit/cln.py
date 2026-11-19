# Credit-linked notes.
#
# client pays 100, gets a coupon while the reference name survives.
# survives -> 100 back at the end. defaults -> note stops, client gets the
# recovery. so inside the note the client has SOLD protection on the name.
#
# second risk: it's the issuing bank's debt, so discount everything at
# (rate + the bank's spread).
#
# value = coupon x annuity + principal leg + recovery leg. set value = 1:
#   coupon = (1 - principal - recovery) / annuity
# coupon ~ risk-free rate + bank's spread + reference CDS spread.

from .bonds import discount_factor
from .default import survival
from .cds import risky_annuity


def cln_annuity(r, issuer_spread, lam, years):
    # the CDS risky annuity, discounted at the bank's rate
    return risky_annuity(r + issuer_spread, lam, years)


def cln_principal_leg(r, issuer_spread, lam, years):
    # 100 back at maturity, only if the name made it all the way
    return discount_factor(r + issuer_spread, years) * survival(lam, years)


def cln_recovery_leg(r, issuer_spread, lam, years, recovery):
    # the CDS protection-leg loop from the noteholder's side: they get what's
    # LEFT (R), not the loss (1 - R)
    total = 0.0
    for t in range(1, years + 1):
        p_default_this_year = survival(lam, t - 1) - survival(lam, t)
        total = total + recovery * p_default_this_year * discount_factor(r + issuer_spread, t)
    return total


def cln_fair_coupon(r, issuer_spread, lam, years, recovery):
    A = cln_annuity(r, issuer_spread, lam, years)
    P = cln_principal_leg(r, issuer_spread, lam, years)
    Rec = cln_recovery_leg(r, issuer_spread, lam, years, recovery)
    return (1 - P - Rec) / A
