import numpy as np
import pytest

from credit.cds import risky_annuity, premium_leg, protection_leg, par_spread

R, LAM, Y, REC = 0.04, 0.02, 5, 0.40
D = lambda t: np.exp(-R * t)
S = lambda t: np.exp(-LAM * t)


def test_legs_by_hand():
    ann = sum(D(t) * S(t) for t in range(1, 6))
    prot = sum((1 - REC) * (S(t - 1) - S(t)) * D(t) for t in range(1, 6))
    assert risky_annuity(R, LAM, Y) == pytest.approx(ann)
    assert premium_leg(0.01, R, LAM, Y) == pytest.approx(0.01 * ann)
    assert protection_leg(R, LAM, Y, REC) == pytest.approx(prot)


def test_par_spread_balances_and_matches_triangle():
    ps = par_spread(R, LAM, Y, REC)
    assert premium_leg(ps, R, LAM, Y) == pytest.approx(protection_leg(R, LAM, Y, REC))
    assert ps == pytest.approx(LAM * (1 - REC), abs=0.001)
