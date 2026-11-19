import numpy as np
import pytest

from credit.default import survival, default_prob, hazard_from_spread, risky_zero


def test_survival_compounds():
    assert survival(0.02, 5) == pytest.approx(np.exp(-0.10))
    assert default_prob(0.02, 5) == pytest.approx(1 - np.exp(-0.10))
    # adding up would say 83%; compounding gives ~56.5%
    assert default_prob(0.1667, 5) == pytest.approx(0.565, abs=0.002)


def test_credit_triangle():
    assert hazard_from_spread(0.012, 0.40) == pytest.approx(0.02)
    assert hazard_from_spread(0.010, 0.20) == pytest.approx(0.0125)


def test_risky_zero():
    S = np.exp(-0.10)
    assert risky_zero(100, 0.04, 0.02, 5, 0.40) == pytest.approx(100 * np.exp(-0.20) * (S + 0.4 * (1 - S)))
    assert risky_zero(100, 0.04, 0.0, 5, 0.40) == pytest.approx(100 * np.exp(-0.20))
    # a spread is roughly just an extra discount rate
    assert risky_zero(100, 0.04, 0.02, 5, 0.40) == pytest.approx(100 * np.exp(-(0.04 + 0.012) * 5), abs=0.5)
