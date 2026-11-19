# python -m credit.run
# the four building blocks, one after the other, ending at the CLN.

from .bonds import zero_price, bond_price, protected_note
from .default import hazard_from_spread, default_prob, risky_zero
from .cds import par_spread, risky_annuity, cs01
from .cln import cln_fair_coupon

R, YEARS, REC = 0.04, 5, 0.40
LINE = "=" * 74


def section(title):
    print(f"\n{title}\n" + "-" * 74)


if __name__ == "__main__":
    print(LINE + "\n  Credit pricer: 5 years, risk-free rate 4%, recovery 40%\n" + LINE)

    section("1. Bonds and the capital-protected note (index vol 18%, dividends 2%, margin 1)")
    print(f"  zero-coupon bond, 100 in 5y:       {zero_price(100, R, YEARS):6.2f}")
    print(f"  5% coupon bond:                    {bond_price(100, 0.05, R, YEARS):6.2f}")
    for rate in (0.005, 0.02, 0.04, 0.05):
        b, ob, p = protected_note(rate, YEARS, 0.18, 0.02)
        print(f"  rate {rate:4.1%}:  bond {b:5.1f}   option budget {ob:5.1f}   participation {p:5.0%}")
    _, _, p0 = protected_note(R, YEARS, 0.18, 0.02)
    _, _, p1 = protected_note(R, YEARS, 0.18, 0.02, funding_spread=0.01)
    print(f"  issuer funding spread 0% -> 1%:    participation {p0:.0%} -> {p1:.0%}")

    section("2. Default risk: what the spread implies")
    for label, s in (("0.50% strong", 0.005), ("1.50% solid", 0.015),
                     ("4.00% high yield", 0.04), ("10.0% distressed", 0.10)):
        lam = hazard_from_spread(s, REC)
        print(f"  {label:<17} default rate {lam:6.2%} a yr   5y default {default_prob(lam, YEARS):5.1%}"
              f"   risky zero {risky_zero(100, R, lam, YEARS, REC):6.2f}")

    section("3. CDS: 2% default rate a year")
    lam = 0.02
    ps = par_spread(R, lam, YEARS, REC)
    print(f"  credit triangle lam x (1-R):       {lam * (1 - REC):6.3%}")
    print(f"  full par spread:                   {ps:6.3%}")
    print(f"  risky annuity:                     {risky_annuity(R, lam, YEARS):6.3f}")
    print(f"  CS01 on 10m notional:              {cs01(R, lam, YEARS, 10_000_000):6,.0f} per bp")

    section("4. The CLN: issuing bank spread 0.60%")
    iss, ref = 0.006, 0.012
    c = cln_fair_coupon(R, iss, hazard_from_spread(ref, REC), YEARS, REC)
    print(f"  rate + bank spread + reference CDS = {R:.2%} + {iss:.2%} + {ref:.2%} = {R + iss + ref:.2%}")
    print(f"  full fair coupon (annual):           {c:.2%}")
    for label, s in (("strong bank", 0.006), ("GCC sovereign", 0.010),
                     ("BBB corporate", 0.015), ("high-yield name", 0.040)):
        lam = hazard_from_spread(s, REC)
        print(f"  {label:<16} CDS {s:5.2%} -> coupon {cln_fair_coupon(R, iss, lam, YEARS, REC):6.2%}"
              f"   chance of losing ~60 over 5y {default_prob(lam, YEARS):5.1%}")
    print("  (illustrative spreads, not live quotes)")
    print(LINE)
