# python -m credit.plots -> docs/credit_panels.png
# left: what rates do to a capital-protected note. right: what the reference
# name's spread does to a CLN coupon, and to the chance of losing ~60.

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .bonds import protected_note
from .default import hazard_from_spread, default_prob
from .cln import cln_fair_coupon

ACCENT, LOSS, HOLD = "#1F6FD0", "#B5332A", "#C08109"
SURFACE, INK, SECOND, GRID = "#FCFCFB", "#1A1A19", "#5A6570", "#E3E6E4"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": SECOND, "xtick.color": SECOND, "ytick.color": SECOND,
    "axes.edgecolor": GRID, "grid.color": GRID, "font.size": 9.5, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 22, "figure.dpi": 130,
})


def tidy(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y")
    ax.set_axisbelow(True)


def make(outdir=None):
    outdir = outdir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    os.makedirs(outdir, exist_ok=True)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.6, 4.6))
    fig.subplots_adjust(wspace=0.32, left=0.07, right=0.93, top=0.82, bottom=0.16)

    rates = np.linspace(0.0, 0.06, 25)
    parts = [protected_note(r, 5, 0.18, 0.02)[2] * 100 for r in rates]
    a1.plot(rates * 100, parts, lw=2, color=ACCENT)
    a1.axhline(0, color=SECOND, lw=0.8)
    a1.annotate("near 0%: bond + margin cost more\nthan 100, the note can't be built",
                (0.15, 0), textcoords="offset points", xytext=(30, 22), fontsize=8, color=SECOND)
    tidy(a1)
    a1.set_title("Capital-protected note: rates decide the product")
    a1.text(0, 1.03, "5y, 100% protected, vol 18%, dividends 2%, margin 1",
            transform=a1.transAxes, fontsize=8, color=SECOND)
    a1.set_xlabel("risk-free rate (%)")
    a1.set_ylabel("participation in the index rise (%)")

    spreads = np.linspace(0.002, 0.05, 30)
    lams = [hazard_from_spread(s, 0.40) for s in spreads]
    coupons = [cln_fair_coupon(0.04, 0.006, l, 5, 0.40) * 100 for l in lams]
    losses = [default_prob(l, 5) * 100 for l in lams]
    a2.plot(spreads * 100, coupons, lw=2, color=ACCENT, label="fair coupon")
    tidy(a2)
    a2.set_title("CLN: a higher coupon is a higher chance of loss")
    a2.text(0, 1.03, "5y, rate 4%, issuing bank spread 0.60%, recovery 40%",
            transform=a2.transAxes, fontsize=8, color=SECOND)
    a2.set_xlabel("reference name's CDS spread (%)")
    a2.set_ylabel("fair coupon (% a year)", color=ACCENT)
    b2 = a2.twinx()
    b2.plot(spreads * 100, losses, lw=2, color=LOSS, ls="--")
    a2.plot([], [], lw=2, color=LOSS, ls="--", label="chance of default, 5y")
    a2.legend(frameon=False, loc="upper left", fontsize=8.5)
    b2.set_ylabel("chance of default within 5 years (%)", color=LOSS)
    for side in ("top",):
        b2.spines[side].set_visible(False)

    fig.text(0.07, 0.01, "Default probabilities are market-implied (pricing), not forecasts. "
             "Annual payments, flat curves, recovery paid at default year end.",
             fontsize=7.8, color=SECOND)
    path = os.path.join(outdir, "credit_panels.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(f"figure -> {make()}")
