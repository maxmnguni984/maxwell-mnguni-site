#!/usr/bin/env python3
"""The inversion for dropshipping: what can you afford to pay, delivered?

    python3 scripts/ds_sweep.py --retail 59,69,79,89,99,129

Rather than guessing a supplier price and asking whether it works, this solves
for the largest TOTAL DELIVERED COST (supplier unit price + shipping to the
customer + import duty + per-parcel clearance fee) that still clears each
threshold at each retail price.

That number is the one to carry into supplier research, because it is the line
above which no supplier is worth talking to, whatever else is true about them.

Closed form. With recovery on returns at zero, which is the honest default for
China-direct because a returned unit sits at a US address and shipping it back
costs more than it is worth:

    contribution = net - D(1 + defect_rate) - support - fees - refund - chargeback

so, setting contribution = threshold x net,

    D = [ net(1 - threshold) - support - fees - refund - chargeback ] / (1 + defect_rate)
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dropship_econ as de


def max_delivered(retail, threshold, v):
    disc = float(v["discount_rate_pct"]) / 100.0
    net = retail * (1 - disc) + float(v["shipping_charged_usd"])
    pay = net * float(v["payment_fee_pct"]) / 100.0 + float(v["payment_fee_fixed_usd"])
    plat = net * float(v["platform_fee_pct"]) / 100.0
    r = float(v["return_rate_pct"]) / 100.0
    refund = r * (net + pay + float(v["return_shipping_paid_by_us_usd"]))
    cb = float(v["chargeback_rate_pct"]) / 100.0
    chargeback = cb * (net + float(v["chargeback_fee_usd"]))
    d = float(v["defect_rate_pct"]) / 100.0
    support = float(v["support_usd"])
    numer = net * (1 - threshold / 100.0) - support - pay - plat - refund - chargeback
    D = numer / (1 + d)
    return net, max(D, 0.0), (D >= 0)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--retail", default="59,69,79,89,99,129,149")
    ap.add_argument("--discount", type=float, default=10.0)
    ap.add_argument("--returns", type=float, default=None)
    ap.add_argument("--scenario", default="base", choices=["base", "downside", "severe"])
    args = ap.parse_args(argv)

    v = dict(de.DEFAULTS)
    v["discount_rate_pct"] = args.discount
    if args.returns is not None:
        v["return_rate_pct"] = args.returns
    if args.scenario == "downside":
        v = de.apply_scenario(v, de.DOWNSIDE)
    elif args.scenario == "severe":
        v = de.apply_scenario(v, de.SEVERE)

    retails = [float(x) for x in args.retail.split(",")]

    print("MAXIMUM TOTAL DELIVERED COST PER ORDER  ({} case)".format(args.scenario))
    print("  delivered = supplier unit price + shipping to customer + duty + clearance fee")
    print("  assumptions: {:.0f}% discount, {:.1f}% returns recovering nothing, {:.1f}% defects,"
          .format(float(v["discount_rate_pct"]), float(v["return_rate_pct"]), float(v["defect_rate_pct"])))
    print("               {:.2f}% chargebacks, {} support, {:.1f}% + {} payment fee"
          .format(float(v["chargeback_rate_pct"]), de.m(float(v["support_usd"])),
                  float(v["payment_fee_pct"]), de.m(float(v["payment_fee_fixed_usd"]))))
    print()
    print("  {:<10}{:>12}{:>22}{:>22}".format("retail", "net revenue", "max delivered @45%", "max delivered @35%"))
    print("  " + "-" * 66)
    for rp in retails:
        net, da, oka = max_delivered(rp, de.BAND_A_MARGIN_PCT, v)
        _, db, okb = max_delivered(rp, de.BAND_B_MARGIN_PCT, v)
        # also enforce the absolute $20 contribution floor
        note = ""
        if net * de.BAND_A_MARGIN_PCT / 100.0 < de.GATE_CONTRIBUTION_USD:
            note = "  <- 45% of net is under the $20 floor"
        print("  {:<10}{:>12}{:>22}{:>22}{}".format(
            "$%.0f" % rp, de.m(net),
            de.m(da) if oka else "impossible",
            de.m(db) if okb else "impossible", note))
    print()
    print("  Read it as a hard ceiling. A supplier whose delivered cost is above the")
    print("  relevant column cannot work at that retail price, whatever else is true.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
