import numpy as np
import pytest

from credit.bonds import discount_factor, zero_price, bond_price, protected_note, call_price


def test_discounting_by_hand():
    assert discount_factor(0.04, 5) == pytest.approx(np.exp(-0.20))
    assert zero_price(100, 0.04, 5) == pytest.approx(81.873, abs=1e-3)


def test_coupon_bond():
    expected = sum(5 * np.exp(-0.04 * t) for t in range(1, 6)) + 100 * np.exp(-0.20)
    assert bond_price(100, 0.05, 0.04, 5) == pytest.approx(expected)


def test_protected_note():
    b, ob, p = protected_note(0.04, 5, 0.18, 0.02)
    assert b == pytest.approx(100 * np.exp(-0.20))
    assert ob == pytest.approx(100 - b - 1.0)
    assert p == pytest.approx(ob / (100 * call_price(5, 0.04, 0.02, 0.18)))


def test_rates_and_funding_drive_participation():
    assert protected_note(0.005, 5, 0.18, 0.02)[2] < protected_note(0.04, 5, 0.18, 0.02)[2]
    assert protected_note(0.04, 5, 0.18, 0.02, funding_spread=0.01)[2] > protected_note(0.04, 5, 0.18, 0.02)[2]
