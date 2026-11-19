import numpy as np
import pytest

from credit.cln import cln_annuity, cln_principal_leg, cln_recovery_leg, cln_fair_coupon

R, ISS, LAM, Y, REC = 0.04, 0.006, 0.02, 5, 0.40
D = lambda t: np.exp(-(R + ISS) * t)
S = lambda t: np.exp(-LAM * t)


def test_legs_by_hand():
    assert cln_annuity(R, ISS, LAM, Y) == pytest.approx(sum(D(t) * S(t) for t in range(1, 6)))
    assert cln_principal_leg(R, ISS, LAM, Y) == pytest.approx(D(5) * S(5))
    assert cln_recovery_leg(R, ISS, LAM, Y, REC) == pytest.approx(0.0333, abs=1e-4)


def test_fair_coupon_prices_to_par():
    c = cln_fair_coupon(R, ISS, LAM, Y, REC)
    value = c * cln_annuity(R, ISS, LAM, Y) + cln_principal_leg(R, ISS, LAM, Y) + cln_recovery_leg(R, ISS, LAM, Y, REC)
    assert value == pytest.approx(1.0)
    # roughly rate + bank spread + reference spread
    assert c == pytest.approx(R + ISS + LAM * (1 - REC), abs=0.003)


def test_riskier_reference_pays_more():
    assert cln_fair_coupon(R, ISS, 0.05, Y, REC) > cln_fair_coupon(R, ISS, 0.01, Y, REC)
