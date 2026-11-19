# Bonds, and the capital-protected note.
#
# Every structured note is a bond (the bank's promise to pay you back) plus a
# derivative. This file is the bond half.

import numpy as np
from scipy.stats import norm


def discount_factor(r, t):
    # 1.0 paid in t years is worth exp(-r * t) today. 4% for 5 years -> 0.8187
    return np.exp(-r * t)


def zero_price(face, r, t):
    # pays the face value once, at maturity. nothing before.
    return face * discount_factor(r, t)


def bond_price(face, coupon_rate, r, years):
    # annual coupons, face value back with the last one.
    # discount every cashflow to today and add them up.
    total = 0.0
    for t in range(1, years + 1):
        cashflow = face * coupon_rate
        if t == years:
            cashflow = cashflow + face
        total = total + cashflow * discount_factor(r, t)
    return total


def call_price(T, r, q, vol, strike=1.0, spot=1.0):
    # Black-Scholes call, per 1.0 of spot (same as my options repo)
    d1 = (np.log(spot / strike) + (r - q + 0.5 * vol**2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    return spot * np.exp(-q * T) * norm.cdf(d1) - strike * np.exp(-r * T) * norm.cdf(d2)


def protected_note(r, years, vol, q, margin=1.0, funding_spread=0.0):
    # out of the client's 100:
    #   buy a zero that grows into 100 -> the guarantee
    #   keep a margin
    #   spend the rest on calls        -> participation = budget / one call
    # rates do almost all the work: high rate, cheap zero, big option budget.
    #
    # the bank discounts the zero at its OWN borrowing rate (rate + funding
    # spread). weaker bank -> cheaper zero -> more participation. that extra is
    # the client being paid to take the bank's credit risk.
    bond_cost = zero_price(100, r + funding_spread, years)
    option_budget = 100 - bond_cost - margin
    one_call = 100 * call_price(years, r, q, vol)
    participation = option_budget / one_call
    return bond_cost, option_budget, participation
