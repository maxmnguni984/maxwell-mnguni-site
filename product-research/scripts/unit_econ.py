#!/usr/bin/env python3
"""Full-stack unit economics with base, downside and severe-downside scenarios.

    python3 unit_econ.py products/candidate.yaml
    python3 unit_econ.py products/candidate.yaml --breakeven-cac
    python3 unit_econ.py products/candidate.yaml --sensitivity

This replaces the simpler calculator used earlier in the project. Three things
it does that the old one did not, each because a real failure mode was missed:

1. **The full cost stack.** Ex-factory alone is where naive markup maths goes
   wrong. Tooling, packaging, inbound freight, duty, customs entry, warehouse
   receiving, storage, pick and pack, outbound postage, payment fees, platform
   fees, discounting, returns and a warranty allowance all land between the
   factory price and the money kept.

2. **Returns modelled properly.** A return is not just a refund. You lose the
   outbound postage you already paid, you may pay return postage, the payment
   processor may keep its fee, and only some fraction of returned units can be
   resold. Modelling returns as a flat percentage of revenue understates them
   substantially for a physical good.

3. **Scenarios that move together.** A downside case where only one input
   worsens is not a downside case. Real bad outcomes correlate: the factory
   price comes in high AND the defect rate is worse than promised AND returns
   run hot AND the discount needed to convert is deeper.

No network access, no dependencies, standard library only.
"""

import argparse
import math
import os
import sys

# --------------------------------------------------------------------- input

FIELDS = (
    # revenue side
    "retail_price_usd",
    "discount_rate_pct",         # blended discount actually given across orders
    # goods
    "exfactory_usd",
    "tooling_total_usd",         # one-off; amortised over first_order_units
    "first_order_units",
    "packaging_usd",             # retail box + mailer + insert
    # inbound
    "inbound_freight_usd",       # per unit, sea + destination charges
    "duty_rate_pct",             # applied to ex-factory value only
    "customs_entry_total_usd",   # broker + ISF + bond + MPF/HMF, amortised
    "inspection_total_usd",      # pre-shipment inspection, amortised
    # warehouse and outbound
    "receiving_usd",             # per unit
    "storage_usd",               # per unit, amortised over expected hold
    "pick_pack_usd",
    "outbound_postage_usd",
    # money
    "payment_fee_pct",
    "payment_fee_fixed_usd",
    "platform_fee_pct",          # Shopify plan is fixed, but marketplace fees are not
    # losses
    "return_rate_pct",
    "return_postage_paid_by_us_pct",   # share of returns where we pay return shipping
    "return_postage_usd",
    "resellable_after_return_pct",     # share of returned units resold at full value
    "defect_rate_pct",                 # units replaced or refunded outright, no resale
    "chargeback_rate_pct",
    "chargeback_fee_usd",
)

DEFAULTS = {
    "discount_rate_pct": 10.0,
    "tooling_total_usd": 0.0,
    "first_order_units": 500,
    "packaging_usd": 1.00,
    "duty_rate_pct": 0.0,
    "customs_entry_total_usd": 900.0,
    "inspection_total_usd": 300.0,
    "receiving_usd": 0.50,
    "storage_usd": 0.60,
    "pick_pack_usd": 2.75,
    "payment_fee_pct": 2.9,
    "payment_fee_fixed_usd": 0.30,
    "platform_fee_pct": 0.0,
    "return_rate_pct": 8.0,
    "return_postage_paid_by_us_pct": 50.0,
    "resellable_after_return_pct": 60.0,
    "defect_rate_pct": 2.0,
    "chargeback_rate_pct": 0.4,
    "chargeback_fee_usd": 15.0,
}

# How each input worsens in the downside and severe cases. A multiplier of 1.3
# means "30% worse than base". Costs go up, resale recovery goes down.
DOWNSIDE = {
    "exfactory_usd": 1.25, "inbound_freight_usd": 1.40, "outbound_postage_usd": 1.25,
    "duty_rate_pct": 1.50, "discount_rate_pct": 1.50, "return_rate_pct": 1.75,
    "defect_rate_pct": 2.00, "chargeback_rate_pct": 1.50, "packaging_usd": 1.20,
    "pick_pack_usd": 1.15, "resellable_after_return_pct": 0.70,
}
SEVERE = {
    "exfactory_usd": 1.45, "inbound_freight_usd": 1.90, "outbound_postage_usd": 1.45,
    "duty_rate_pct": 2.20, "discount_rate_pct": 2.00, "return_rate_pct": 2.75,
    "defect_rate_pct": 4.00, "chargeback_rate_pct": 2.50, "packaging_usd": 1.40,
    "pick_pack_usd": 1.30, "resellable_after_return_pct": 0.35,
}

GATE_CONTRIBUTION_USD = 20.0
GATE_MARGIN_PCT = 45.0
GATE_MAX_BE_ROAS = 2.2


def parse_simple_yaml(path):
    """Parse the flat key: value files this project uses. No dependencies."""
    data = {}
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split(" #")[0].rstrip()
            if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
                continue
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if not value:
                continue
            try:
                data[key] = float(value)
            except ValueError:
                data[key] = value
    return data


def apply_scenario(base, multipliers):
    out = dict(base)
    for key, factor in multipliers.items():
        if key in out and isinstance(out[key], (int, float)):
            out[key] = out[key] * factor
    # percentages that must stay bounded
    for key in ("discount_rate_pct", "return_rate_pct", "defect_rate_pct", "chargeback_rate_pct"):
        if key in out:
            out[key] = min(out[key], 95.0)
    if "resellable_after_return_pct" in out:
        out["resellable_after_return_pct"] = max(0.0, min(out["resellable_after_return_pct"], 100.0))
    return out


# ----------------------------------------------------------------- the model

def compute(v):
    """Return the full per-order economics for one scenario."""
    units = max(1.0, float(v["first_order_units"]))

    price = float(v["retail_price_usd"])
    net_price = price * (1 - float(v["discount_rate_pct"]) / 100.0)

    # --- landed cost of one unit ---------------------------------------
    exfactory = float(v["exfactory_usd"])
    tooling = float(v["tooling_total_usd"]) / units
    duty = exfactory * float(v["duty_rate_pct"]) / 100.0
    entry = float(v["customs_entry_total_usd"]) / units
    inspection = float(v["inspection_total_usd"]) / units
    inbound = float(v["inbound_freight_usd"])
    landed = exfactory + tooling + duty + entry + inspection + inbound

    # --- cost to get it to a customer -----------------------------------
    packaging = float(v["packaging_usd"])
    warehouse = float(v["receiving_usd"]) + float(v["storage_usd"]) + float(v["pick_pack_usd"])
    postage = float(v["outbound_postage_usd"])
    fulfilment = packaging + warehouse + postage

    # --- money costs -----------------------------------------------------
    payment_fee = net_price * float(v["payment_fee_pct"]) / 100.0 + float(v["payment_fee_fixed_usd"])
    platform_fee = net_price * float(v["platform_fee_pct"]) / 100.0

    # --- losses ----------------------------------------------------------
    # A return costs: the revenue, the outbound postage already spent, possibly
    # return postage, the payment fee if not refunded, minus whatever value the
    # unit retains if it can be resold.
    r = float(v["return_rate_pct"]) / 100.0
    resell = float(v["resellable_after_return_pct"]) / 100.0
    ret_post_share = float(v["return_postage_paid_by_us_pct"]) / 100.0
    ret_post = float(v.get("return_postage_usd", postage))
    unrecovered_goods = landed * (1 - resell)
    return_loss = r * (postage + ret_post_share * ret_post + payment_fee + unrecovered_goods)

    # A defect is worse than a return: the unit is gone and you ship a
    # replacement or refund without getting anything back.
    d = float(v["defect_rate_pct"]) / 100.0
    defect_loss = d * (landed + postage + packaging)

    cb = float(v["chargeback_rate_pct"]) / 100.0
    chargeback_loss = cb * (net_price + landed + fulfilment + float(v["chargeback_fee_usd"]))

    losses = return_loss + defect_loss + chargeback_loss

    contribution = net_price - landed - fulfilment - payment_fee - platform_fee - losses
    margin_pct = (contribution / net_price * 100.0) if net_price else 0.0

    return {
        "price": price, "net_price": net_price,
        "landed": landed, "exfactory": exfactory, "duty": duty, "inbound": inbound,
        "tooling": tooling, "entry": entry, "inspection": inspection,
        "fulfilment": fulfilment, "packaging": packaging, "warehouse": warehouse, "postage": postage,
        "payment_fee": payment_fee, "platform_fee": platform_fee,
        "return_loss": return_loss, "defect_loss": defect_loss, "chargeback_loss": chargeback_loss,
        "losses": losses,
        "contribution": contribution, "margin_pct": margin_pct,
        "be_cac": contribution,
        "be_roas": (net_price / contribution) if contribution > 0 else None,
        "cash_per_unit": landed,
        "first_order_cash": landed * units,
    }


def gates(r):
    checks = [
        ("contribution >= $%.2f" % GATE_CONTRIBUTION_USD, r["contribution"] >= GATE_CONTRIBUTION_USD),
        ("margin >= %.0f%%" % GATE_MARGIN_PCT, r["margin_pct"] >= GATE_MARGIN_PCT),
        ("break-even ROAS <= %.1f" % GATE_MAX_BE_ROAS,
         r["be_roas"] is not None and 0 < r["be_roas"] <= GATE_MAX_BE_ROAS),
    ]
    return checks, all(ok for _, ok in checks)


# ---------------------------------------------------------------- reporting

def money(x):
    return "n/a" if x is None else "${:,.2f}".format(x)


def report(name, scenarios):
    print("=" * 78)
    print(name)
    print("=" * 78)

    rows = [
        ("Retail price", "price"), ("Net after discount", "net_price"),
        ("  ex-factory", "exfactory"), ("  duty", "duty"), ("  inbound freight", "inbound"),
        ("  tooling amortised", "tooling"), ("  customs entry amortised", "entry"),
        ("  inspection amortised", "inspection"),
        ("LANDED COST", "landed"),
        ("  packaging", "packaging"), ("  warehouse", "warehouse"), ("  outbound postage", "postage"),
        ("FULFILMENT", "fulfilment"),
        ("Payment fee", "payment_fee"), ("Platform fee", "platform_fee"),
        ("  return loss", "return_loss"), ("  defect loss", "defect_loss"),
        ("  chargeback loss", "chargeback_loss"),
        ("LOSSES", "losses"),
    ]
    labels = [s[0] for s in scenarios]
    print("{:<30}".format("") + "".join("{:>15}".format(l) for l in labels))
    print("-" * 78)
    for label, key in rows:
        print("{:<30}".format(label) + "".join("{:>15}".format(money(r[key])) for _, r in scenarios))

    print("-" * 78)
    print("{:<30}".format("CONTRIBUTION")
          + "".join("{:>15}".format(money(r["contribution"])) for _, r in scenarios))
    print("{:<30}".format("Margin %")
          + "".join("{:>15}".format("{:.1f}%".format(r["margin_pct"])) for _, r in scenarios))
    print("{:<30}".format("Break-even CAC")
          + "".join("{:>15}".format(money(r["be_cac"])) for _, r in scenarios))
    print("{:<30}".format("Break-even ROAS")
          + "".join("{:>15}".format("n/a" if r["be_roas"] is None else "{:.2f}".format(r["be_roas"]))
                    for _, r in scenarios))
    print()

    print("GATES (contribution >= $20, margin >= 45%, break-even ROAS <= 2.2)")
    for label, r in scenarios:
        checks, passed = gates(r)
        detail = ", ".join(("ok " if ok else "FAIL ") + c for c, ok in checks)
        print("  {:<12} {}   [{}]".format(label, "PASS" if passed else "FAIL", detail))
    print()

    base = scenarios[0][1]
    print("CASH AND RECOVERY")
    print("  Landed cash per unit          {}".format(money(base["cash_per_unit"])))
    print("  First order cash outlay       {}".format(money(base["first_order_cash"])))
    ordered = base["first_order_cash"] / base["cash_per_unit"] if base["cash_per_unit"] else 0
    for label, r in scenarios:
        prefix = "  Units to recover outlay {:<11}".format("(" + label + ")")
        if r["contribution"] > 0:
            n = math.ceil(base["first_order_cash"] / r["contribution"])
            flag = "" if n <= ordered else "   <-- more than the whole order"
            print("{} {:>6}  of {:.0f} ordered{}".format(prefix, n, ordered, flag))
        else:
            print("{} never, contribution is negative".format(prefix))
    print()


def sensitivity(base_inputs):
    print("SENSITIVITY: what single change breaks the base case?")
    print("-" * 78)
    base = compute(base_inputs)
    _, base_ok = gates(base)
    print("  base: contribution {} margin {:.1f}%  [{}]".format(
        money(base["contribution"]), base["margin_pct"], "PASS" if base_ok else "FAIL"))
    print()
    knobs = [
        ("ex-factory", "exfactory_usd", [1.1, 1.25, 1.5, 2.0]),
        ("outbound postage", "outbound_postage_usd", [1.25, 1.5, 2.0, 3.0]),
        ("duty rate", "duty_rate_pct", [1.5, 2.0, 3.0]),
        ("return rate", "return_rate_pct", [1.5, 2.0, 3.0]),
        ("discount given", "discount_rate_pct", [1.5, 2.0, 3.0]),
        ("defect rate", "defect_rate_pct", [2.0, 4.0, 8.0]),
    ]
    for label, key, factors in knobs:
        if key not in base_inputs:
            continue
        breaking = None
        for f in factors:
            trial = dict(base_inputs)
            trial[key] = base_inputs[key] * f
            _, ok = gates(compute(trial))
            if not ok:
                breaking = f
                break
        if breaking:
            print("  {:<20} breaks the gates at {:.0f}% of base ({:.2f}x)"
                  .format(label, breaking * 100, breaking))
        else:
            print("  {:<20} survives every tested increase".format(label))
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Full-stack unit economics with downside scenarios.")
    parser.add_argument("spec", help="path to a product spec file")
    parser.add_argument("--sensitivity", action="store_true", help="show what single change breaks it")
    parser.add_argument("--breakeven-cac", action="store_true",
                        help="print only the break-even CAC line, for scripting")
    args = parser.parse_args(argv)

    if not os.path.exists(args.spec):
        sys.exit("no such spec file: {}".format(args.spec))

    raw = parse_simple_yaml(args.spec)
    name = raw.get("name", os.path.basename(args.spec))

    inputs = dict(DEFAULTS)
    for key in FIELDS:
        if key in raw:
            inputs[key] = raw[key]
    missing = [k for k in ("retail_price_usd", "exfactory_usd", "inbound_freight_usd",
                           "outbound_postage_usd") if k not in inputs]
    if missing:
        sys.exit("spec is missing required field(s): {}".format(", ".join(missing)))
    inputs.setdefault("return_postage_usd", inputs["outbound_postage_usd"])

    scenarios = [
        ("base", compute(inputs)),
        ("downside", compute(apply_scenario(inputs, DOWNSIDE))),
        ("severe", compute(apply_scenario(inputs, SEVERE))),
    ]

    if args.breakeven_cac:
        for label, r in scenarios:
            print("{}\t{}".format(label, money(r["be_cac"])))
        return 0

    report(name, scenarios)
    if args.sensitivity:
        sensitivity(inputs)

    unverified = raw.get("unverified_inputs")
    if unverified:
        print("UNVERIFIED INPUTS declared in the spec:")
        print("  {}".format(unverified))
        print("  Every figure above inherits that uncertainty.")
        print()

    _, base_ok = gates(scenarios[0][1])
    _, down_ok = gates(scenarios[1][1])
    if base_ok and down_ok:
        print("READ: clears the gates in both base and downside. Strongest possible result here.")
    elif base_ok:
        print("READ: clears in base but FAILS in downside. The business depends on nothing going wrong.")
    else:
        print("READ: fails the gates in the base case. Do not proceed on these numbers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
