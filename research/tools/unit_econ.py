#!/usr/bin/env python3
"""Deterministic unit-economics calculator for the product-research system.

Standard library only. The economics agent supplies inputs and interprets the
output; it must not do this arithmetic in prose.

Usage:
    python3 unit_econ.py --demo
    python3 unit_econ.py --self-test
    python3 unit_econ.py --input inputs.json [--out economics/P-....json]

Input JSON (all money in USD, per order of one unit):

{
  "product_id": "P-2026-09-16-003",
  "price": 39.99,
  "unit_cost":     {"pessimistic": 9.50, "base": 7.80, "optimistic": 6.90},
  "ship_cost":     {"pessimistic": 6.00, "base": 4.50, "optimistic": 3.80},
  "duty_rate":     {"pessimistic": 0.25, "base": 0.15, "optimistic": 0.00},
  "refund_rate":   {"pessimistic": 0.12, "base": 0.06, "optimistic": 0.03},
  "discount_rate": {"pessimistic": 0.15, "base": 0.10, "optimistic": 0.05},
  "chargeback_rate": {"pessimistic": 0.015, "base": 0.007, "optimistic": 0.003},
  "packaging_cost": {"pessimistic": 1.50, "base": 1.00, "optimistic": 0.50},
  "payment_pct": 0.029,
  "payment_fixed": 0.30,
  "chargeback_fee": 15.00,
  "fixed_monthly": 55.00,
  "duty_basis": "declared_value",
  "labels": {"price": "ESTIMATE", "unit_cost": "FACT", "duty_rate": "ASSUMPTION"}
}

Any scenario map may be given as a single number, which is then used for all
three scenarios. Rates are decimals, not percentages.

Model, per order:

  net_price       = price * (1 - discount_rate)
  duty            = duty_rate * duty_basis_value      (declared value or cost)
  payment_fee     = net_price * payment_pct + payment_fixed
  refund_loss     = refund_rate * (net_price + unit_cost + ship_cost + duty)
  chargeback_loss = chargeback_rate * (net_price + chargeback_fee)
  contribution    = net_price - unit_cost - ship_cost - duty - packaging
                    - payment_fee - refund_loss - chargeback_loss

  break_even_cac  = contribution                (spend per order to break even)
  break_even_roas = net_price / contribution    (undefined if contribution <= 0)
  orders_to_cover_fixed = ceil(fixed_monthly / contribution)

Refund loss assumes the customer is refunded the net price and the unit is not
recovered, so cost, shipping and duty are lost too. That is the conservative
reading for cross-border dropshipping and is stated as an assumption in the
output.
"""

import argparse
import json
import math
import sys

SCENARIOS = ("pessimistic", "base", "optimistic")

SCENARIO_FIELDS = (
    "unit_cost",
    "ship_cost",
    "duty_rate",
    "refund_rate",
    "discount_rate",
    "chargeback_rate",
    "packaging_cost",
)

DEFAULTS = {
    "payment_pct": 0.029,
    "payment_fixed": 0.30,
    "chargeback_fee": 15.00,
    "fixed_monthly": 55.00,
    "duty_basis": "declared_value",
}

ASSUMPTION_NOTES = [
    "Payment fees default to Shopify Payments US online card rates (2.9% + $0.30). Verify against your own plan.",
    "Refund loss assumes the unit is not recovered: net price, unit cost, shipping and duty are all lost.",
    "Chargeback loss assumes the net price is lost plus a fixed dispute fee.",
    "US duty-free de minimis treatment ended for all countries on 2025-08-29 (Executive Order 14324) and the suspension was made indefinite in 2026, so every imported parcel is treated as dutiable. Set duty_rate to 0 only for a supplier quote that is explicitly DDP (duty paid), and say so.",
    "Duty is applied to the declared value by default; set duty_basis to 'cost' to apply it to unit cost plus shipping instead.",
    "Fixed monthly cost defaults to $55: Shopify plan plus domain amortised. Replace with your real figure.",
]


def _round(x):
    return round(x + 0.0, 4)


def _scenario_value(raw, scenario, field):
    """Accept either a per-scenario map or a single number."""
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, dict):
        if scenario not in raw:
            raise ValueError("field '%s' is missing scenario '%s'" % (field, scenario))
        value = raw[scenario]
        if not isinstance(value, (int, float)):
            raise ValueError("field '%s' scenario '%s' is not a number" % (field, scenario))
        return float(value)
    raise ValueError("field '%s' must be a number or a scenario map" % field)


def compute_scenario(inputs, scenario):
    price = float(inputs["price"])
    v = {f: _scenario_value(inputs[f], scenario, f) for f in SCENARIO_FIELDS}

    payment_pct = float(inputs.get("payment_pct", DEFAULTS["payment_pct"]))
    payment_fixed = float(inputs.get("payment_fixed", DEFAULTS["payment_fixed"]))
    chargeback_fee = float(inputs.get("chargeback_fee", DEFAULTS["chargeback_fee"]))
    fixed_monthly = float(inputs.get("fixed_monthly", DEFAULTS["fixed_monthly"]))
    duty_basis = inputs.get("duty_basis", DEFAULTS["duty_basis"])

    net_price = price * (1.0 - v["discount_rate"])

    if duty_basis == "cost":
        duty_base = v["unit_cost"] + v["ship_cost"]
    elif duty_basis == "declared_value":
        duty_base = net_price
    else:
        raise ValueError("duty_basis must be 'declared_value' or 'cost'")
    duty = v["duty_rate"] * duty_base

    payment_fee = net_price * payment_pct + payment_fixed
    refund_loss = v["refund_rate"] * (net_price + v["unit_cost"] + v["ship_cost"] + duty)
    chargeback_loss = v["chargeback_rate"] * (net_price + chargeback_fee)

    contribution = (
        net_price
        - v["unit_cost"]
        - v["ship_cost"]
        - duty
        - v["packaging_cost"]
        - payment_fee
        - refund_loss
        - chargeback_loss
    )

    margin_pct = (contribution / net_price * 100.0) if net_price else 0.0
    if contribution > 0:
        break_even_roas = net_price / contribution
        orders_to_cover_fixed = int(math.ceil(fixed_monthly / contribution))
    else:
        break_even_roas = None
        orders_to_cover_fixed = None

    return {
        "scenario": scenario,
        "inputs": {
            "price": _round(price),
            "net_price": _round(net_price),
            "unit_cost": _round(v["unit_cost"]),
            "ship_cost": _round(v["ship_cost"]),
            "duty_rate": _round(v["duty_rate"]),
            "duty_basis": duty_basis,
            "refund_rate": _round(v["refund_rate"]),
            "discount_rate": _round(v["discount_rate"]),
            "chargeback_rate": _round(v["chargeback_rate"]),
            "packaging_cost": _round(v["packaging_cost"]),
            "payment_pct": payment_pct,
            "payment_fixed": payment_fixed,
            "chargeback_fee": chargeback_fee,
            "fixed_monthly": fixed_monthly,
        },
        "costs": {
            "duty": _round(duty),
            "payment_fee": _round(payment_fee),
            "refund_loss": _round(refund_loss),
            "chargeback_loss": _round(chargeback_loss),
        },
        "contribution_margin": _round(contribution),
        "contribution_margin_pct": _round(margin_pct),
        "break_even_cac": _round(contribution),
        "break_even_roas": _round(break_even_roas) if break_even_roas is not None else None,
        "orders_to_cover_fixed_monthly": orders_to_cover_fixed,
    }


def compute(inputs):
    required = ("price",) + SCENARIO_FIELDS
    missing = [f for f in required if f not in inputs]
    if missing:
        raise ValueError("missing required input fields: %s" % ", ".join(missing))

    scenarios = {s: compute_scenario(inputs, s) for s in SCENARIOS}
    base = scenarios["base"]
    pess = scenarios["pessimistic"]

    gate_g6 = "pass"
    reasons = []
    if base["contribution_margin"] < 12.0:
        gate_g6 = "fail"
        reasons.append("base contribution margin $%.2f is below $12" % base["contribution_margin"])
    if base["contribution_margin_pct"] < 35.0:
        gate_g6 = "fail"
        reasons.append("base contribution margin %.1f%% is below 35%%" % base["contribution_margin_pct"])
    if pess["contribution_margin"] < 0.0:
        gate_g6 = "fail"
        reasons.append("pessimistic contribution margin $%.2f is below zero" % pess["contribution_margin"])

    return {
        "product_id": inputs.get("product_id"),
        "generated_by": "research/tools/unit_econ.py",
        "scenarios": scenarios,
        "gate_G6": {"result": gate_g6, "reasons": reasons},
        "input_labels": inputs.get("labels", {}),
        "assumption_notes": ASSUMPTION_NOTES,
    }


def render_table(result):
    rows = [
        ("Net price", "net_price"),
        ("Unit cost", "unit_cost"),
        ("Shipping", "ship_cost"),
    ]
    out = []
    out.append("| Metric | Pessimistic | Base | Optimistic |")
    out.append("|---|---:|---:|---:|")
    for label, key in rows:
        vals = [result["scenarios"][s]["inputs"][key] for s in SCENARIOS]
        out.append("| %s | %.2f | %.2f | %.2f |" % (label, vals[0], vals[1], vals[2]))
    for label, key in (("Duty", "duty"), ("Payment fee", "payment_fee"),
                       ("Refund allowance", "refund_loss"), ("Chargeback allowance", "chargeback_loss")):
        vals = [result["scenarios"][s]["costs"][key] for s in SCENARIOS]
        out.append("| %s | %.2f | %.2f | %.2f |" % (label, vals[0], vals[1], vals[2]))
    vals = [result["scenarios"][s]["contribution_margin"] for s in SCENARIOS]
    out.append("| **Contribution margin** | **%.2f** | **%.2f** | **%.2f** |" % (vals[0], vals[1], vals[2]))
    vals = [result["scenarios"][s]["contribution_margin_pct"] for s in SCENARIOS]
    out.append("| Contribution margin %% | %.1f | %.1f | %.1f |" % (vals[0], vals[1], vals[2]))
    vals = [result["scenarios"][s]["break_even_cac"] for s in SCENARIOS]
    out.append("| Break-even CAC | %.2f | %.2f | %.2f |" % (vals[0], vals[1], vals[2]))
    roas = [result["scenarios"][s]["break_even_roas"] for s in SCENARIOS]
    out.append("| Break-even ROAS | %s | %s | %s |" % tuple(
        ("%.2f" % r) if r is not None else "n/a" for r in roas))
    orders = [result["scenarios"][s]["orders_to_cover_fixed_monthly"] for s in SCENARIOS]
    out.append("| Orders/month to cover fixed | %s | %s | %s |" % tuple(
        str(o) if o is not None else "n/a" for o in orders))
    out.append("")
    out.append("Gate G6: **%s**%s" % (
        result["gate_G6"]["result"].upper(),
        (" (" + "; ".join(result["gate_G6"]["reasons"]) + ")") if result["gate_G6"]["reasons"] else ""))
    return "\n".join(out)


DEMO_INPUT = {
    "product_id": "P-2026-09-16-001",
    "price": 39.99,
    "unit_cost": {"pessimistic": 9.50, "base": 7.80, "optimistic": 6.90},
    "ship_cost": {"pessimistic": 6.00, "base": 4.50, "optimistic": 3.80},
    "duty_rate": {"pessimistic": 0.25, "base": 0.15, "optimistic": 0.00},
    "refund_rate": {"pessimistic": 0.12, "base": 0.06, "optimistic": 0.03},
    "discount_rate": {"pessimistic": 0.15, "base": 0.10, "optimistic": 0.05},
    "chargeback_rate": {"pessimistic": 0.015, "base": 0.007, "optimistic": 0.003},
    "packaging_cost": {"pessimistic": 1.50, "base": 1.00, "optimistic": 0.50},
    "labels": {
        "price": "ESTIMATE (midpoint of observed competitor range)",
        "unit_cost": "FACT (supplier listing) / ESTIMATE for the low and high",
        "duty_rate": "ASSUMPTION (rate not yet confirmed for this HTS code)",
        "refund_rate": "ASSUMPTION (no store history yet)",
    },
}


def self_test():
    """Hand-checked arithmetic for the base scenario of DEMO_INPUT.

    net_price       = 39.99 * 0.90                       = 35.991
    duty            = 0.15 * 35.991                      = 5.39865
    payment_fee     = 35.991 * 0.029 + 0.30              = 1.343739
    refund_loss     = 0.06 * (35.991 + 7.80 + 4.50 + 5.39865) = 3.2213190
    chargeback_loss = 0.007 * (35.991 + 15.00)           = 0.356937
    contribution    = 35.991 - 7.80 - 4.50 - 5.39865 - 1.00
                      - 1.343739 - 3.221319 - 0.356937   = 12.370355
    """
    failures = []

    r = compute(DEMO_INPUT)
    base = r["scenarios"]["base"]

    expected = {
        "net_price": 35.991,
        "duty": 5.39865,
        "payment_fee": 1.343739,
        "refund_loss": 3.221319,
        "chargeback_loss": 0.356937,
        "contribution": 12.370355,
    }
    checks = [
        ("net_price", base["inputs"]["net_price"], expected["net_price"]),
        ("duty", base["costs"]["duty"], expected["duty"]),
        ("payment_fee", base["costs"]["payment_fee"], expected["payment_fee"]),
        ("refund_loss", base["costs"]["refund_loss"], expected["refund_loss"]),
        ("chargeback_loss", base["costs"]["chargeback_loss"], expected["chargeback_loss"]),
        ("contribution", base["contribution_margin"], expected["contribution"]),
    ]
    for name, got, want in checks:
        if abs(got - want) > 0.0005:
            failures.append("base %s: got %.6f, expected %.6f" % (name, got, want))

    # break-even ROAS = net_price / contribution
    want_roas = expected["net_price"] / expected["contribution"]
    if abs(base["break_even_roas"] - want_roas) > 0.001:
        failures.append("base break_even_roas: got %.4f, expected %.4f" % (base["break_even_roas"], want_roas))

    # break-even CAC equals contribution margin
    if abs(base["break_even_cac"] - base["contribution_margin"]) > 1e-9:
        failures.append("break_even_cac should equal contribution_margin")

    # orders to cover $55 fixed at $12.370355 contribution = ceil(4.446) = 5
    if base["orders_to_cover_fixed_monthly"] != 5:
        failures.append("orders_to_cover_fixed_monthly: got %s, expected 5" % base["orders_to_cover_fixed_monthly"])

    # margin ordering: optimistic > base > pessimistic
    o = r["scenarios"]["optimistic"]["contribution_margin"]
    b = base["contribution_margin"]
    p = r["scenarios"]["pessimistic"]["contribution_margin"]
    if not (o > b > p):
        failures.append("expected optimistic > base > pessimistic, got %.2f, %.2f, %.2f" % (o, b, p))

    # G6 fails this demo on the percentage test (34.4% < 35%)
    if r["gate_G6"]["result"] != "fail":
        failures.append("demo should fail G6 on margin percentage, got %s" % r["gate_G6"]["result"])

    # scalar shorthand works
    scalar = dict(DEMO_INPUT)
    scalar["packaging_cost"] = 1.00
    s = compute(scalar)
    if abs(s["scenarios"]["base"]["contribution_margin"] - b) > 1e-9:
        failures.append("scalar shorthand for packaging_cost changed the base result")

    # negative contribution yields no ROAS instead of a division error
    bad = dict(DEMO_INPUT)
    bad["price"] = 9.00
    nb = compute(bad)
    if nb["scenarios"]["base"]["break_even_roas"] is not None:
        failures.append("negative contribution should give break_even_roas = None")
    if nb["gate_G6"]["result"] != "fail":
        failures.append("negative contribution should fail G6")

    # missing field is reported, not silently defaulted
    incomplete = {k: v for k, v in DEMO_INPUT.items() if k != "ship_cost"}
    try:
        compute(incomplete)
        failures.append("missing ship_cost should raise ValueError")
    except ValueError:
        pass

    # missing scenario key is reported
    partial = json.loads(json.dumps(DEMO_INPUT))
    del partial["unit_cost"]["optimistic"]
    try:
        compute(partial)
        failures.append("missing scenario key should raise ValueError")
    except ValueError:
        pass

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("unit_econ.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Unit-economics scenarios for one product.")
    ap.add_argument("--input", help="path to an input JSON file")
    ap.add_argument("--out", help="write the result JSON here")
    ap.add_argument("--demo", action="store_true", help="run the documented worked example")
    ap.add_argument("--self-test", action="store_true", dest="self_test", help="check the arithmetic")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if args.demo:
        inputs = DEMO_INPUT
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as fh:
            inputs = json.load(fh)
    else:
        ap.error("give --input, --demo or --self-test")
        return 2

    try:
        result = compute(inputs)
    except ValueError as exc:
        print("input error: %s" % exc, file=sys.stderr)
        return 2

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
            fh.write("\n")
        print("wrote %s" % args.out)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_table(result))
        print("")
        print("Assumptions carried by this model:")
        for note in result["assumption_notes"]:
            print("  - " + note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
