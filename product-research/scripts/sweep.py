#!/usr/bin/env python3
"""Two-dimensional band grid: what retail price and ex-factory cost combinations work.

    python3 scripts/sweep.py products/shear.yaml
    python3 scripts/sweep.py products/shear.yaml --retail 59,69,79,89 --exf 6,9,12,16
    python3 scripts/sweep.py products/shear.yaml --units 300,500,1000

A single point estimate hides the question that actually matters, which is not
"does this work at $69 with a $12.50 factory price" but "what is the largest
factory price I can pay at each retail price and still clear a threshold".
That is the number to walk into a negotiation holding.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_econ as ue

MARK = {"A": "A", "B": "b", "NEITHER": "."}


def grid(inputs, retails, exfs, scenario=None):
    out = {}
    for rp in retails:
        for ex in exfs:
            v = dict(inputs)
            v["retail_price_usd"] = rp
            v["exfactory_usd"] = ex
            if scenario:
                v = ue.apply_scenario(v, scenario)
            r = ue.compute(v)
            out[(rp, ex)] = r
    return out


def show(title, g, retails, exfs):
    print(title)
    print("  {:<12}".format("ex-factory") + "".join("{:>9}".format("$%.0f" % rp) for rp in retails))
    print("  " + "-" * (12 + 9 * len(retails)))
    for ex in exfs:
        cells = ""
        for rp in retails:
            r = g[(rp, ex)]
            b = ue.band(r)
            cells += "{:>9}".format("{} {:>5.1f}".format(MARK[b], r["margin_pct"]))
        print("  {:<12}{}".format("$%.2f" % ex, cells))
    print("  A = band A (>=45% and >=$20)   b = band B (35-44.9% and >=$20)   . = below both")
    print()


def max_affordable(inputs, retails, threshold):
    """The inversion: highest ex-factory that still clears a threshold at each price."""
    print("  {:<10}{:>16}{:>16}{:>14}".format("retail", "max ex-factory", "contribution", "as % of net"))
    print("  " + "-" * 56)
    for rp in retails:
        best = None
        ex = 0.50
        while ex <= 60.0:
            v = dict(inputs)
            v["retail_price_usd"] = rp
            v["exfactory_usd"] = ex
            r = ue.compute(v)
            if r["margin_pct"] >= threshold and r["contribution"] >= ue.GATE_CONTRIBUTION_USD:
                best = (ex, r)
            else:
                break
            ex += 0.25
        if best:
            ex, r = best
            print("  {:<10}{:>16}{:>16}{:>14}".format(
                "$%.0f" % rp, "$%.2f" % ex, "$%.2f" % r["contribution"], "%.1f%%" % r["margin_pct"]))
        else:
            print("  {:<10}{:>16}".format("$%.0f" % rp, "none - fails at any cost"))
    print()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--retail", default="59,69,79,89,99")
    ap.add_argument("--exf", default="6,8,10,12,14,16,20")
    ap.add_argument("--units", default="")
    args = ap.parse_args(argv)

    raw, inputs = ue.load(args.spec)
    retails = [float(x) for x in args.retail.split(",")]
    exfs = [float(x) for x in args.exf.split(",")]

    print("=" * 78)
    print(raw.get("name", args.spec))
    print("=" * 78)
    print()

    show("BASE CASE: contribution as % of net revenue", grid(inputs, retails, exfs), retails, exfs)
    show("DOWNSIDE CASE: the same grid where things go wrong",
         grid(inputs, retails, exfs, ue.DOWNSIDE), retails, exfs)

    print("MAXIMUM AFFORDABLE EX-FACTORY at the preferred 45% threshold")
    print("  This is the number to hold in a negotiation. Above it the product fails.")
    max_affordable(inputs, retails, ue.BAND_A_MARGIN_PCT)

    print("MAXIMUM AFFORDABLE EX-FACTORY at the conditional 35% threshold")
    max_affordable(inputs, retails, ue.BAND_B_MARGIN_PCT)

    if args.units:
        print("ORDER QUANTITY: what changes with scale")
        print("  Fixed costs amortise, but cash at risk rises in proportion.")
        print("  {:<10}{:>14}{:>14}{:>12}{:>16}".format(
            "units", "contribution", "as % of net", "band", "upfront cash"))
        print("  " + "-" * 66)
        for u in [float(x) for x in args.units.split(",")]:
            v = dict(inputs)
            v["first_order_units"] = u
            r = ue.compute(v)
            print("  {:<10}{:>14}{:>14}{:>12}{:>16}".format(
                "%.0f" % u, "$%.2f" % r["contribution"], "%.1f%%" % r["margin_pct"],
                ue.band(r), "${:,.0f}".format(r["upfront_cash"])))
        print()
        print("  Note: this holds ex-factory CONSTANT. In reality a larger order also buys")
        print("  a lower factory price, and the first two tiers carry the steepest break")
        print("  (roughly 28% in the sourcing research). That effect is not modelled here")
        print("  because no supplier has quoted a tier table.")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
