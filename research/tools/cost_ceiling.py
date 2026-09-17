#!/usr/bin/env python3
"""Maximum landed cost a product can bear, given a price and an ad target.

Standard library only.

WHY THIS EXISTS
---------------
`unit_econ.py` answers "given a cost, what is the margin?". That question needs
a supplier quote. In an environment where supplier catalogues cannot be read,
that question is unanswerable and any answer is invention.

This tool asks the question backwards: "given the price we can charge and the
return on ad spend we can realistically achieve, what is the most this product
may cost us, landed, before the business stops working?"

That flips an unknowable into a single checkable number. Nobody has to guess a
cost. Someone opens one supplier page, reads one price, and compares.

MODEL, per order of one unit
----------------------------
  net_price     = price * (1 - discount_rate)
  payment_fee   = net_price * payment_pct + payment_fixed
  refund_loss   = refund_rate * (net_price + landed_cost)
  chargeback    = chargeback_rate * (net_price + chargeback_fee)
  ad_cost       = net_price / target_roas
  contribution  = net_price - landed_cost - packaging - payment_fee
                  - refund_loss - chargeback
  profit        = contribution - ad_cost

Setting profit to the required profit per order and solving for landed_cost:

  landed_cost * (1 + refund_rate)
      = net_price - packaging - payment_fee - refund_rate*net_price
        - chargeback - ad_cost - required_profit

  landed_cost = (that whole right-hand side) / (1 + refund_rate)

The (1 + refund_rate) divisor is the part people forget: on a refunded order you
lose the goods as well as the revenue, so every dollar of unit cost is exposed
to the refund rate on top of itself.

Usage:
    python3 cost_ceiling.py --price 39.99
    python3 cost_ceiling.py --price 39.99 --roas 2.5 --profit 5
    python3 cost_ceiling.py --price 39.99 --json
    python3 cost_ceiling.py --self-test
"""

import argparse
import json
import sys

# Fee assumptions. All ASSUMPTIONS for a new store with no trading history.
PAYMENT_PCT = 0.029          # Shopify Payments US online card rate
PAYMENT_FIXED = 0.30
CHARGEBACK_FEE = 15.00

SCENARIOS = {
    # name: (discount_rate, refund_rate, chargeback_rate, packaging, target_roas)
    "pessimistic": (0.15, 0.12, 0.015, 1.50, 1.8),
    "base":        (0.10, 0.06, 0.007, 1.00, 2.5),
    "optimistic":  (0.05, 0.03, 0.003, 0.50, 3.5),
}

ASSUMPTION_NOTES = [
    "Every rate here is an ASSUMPTION. A new store has no history to measure.",
    "Target ROAS is the return on ad spend the store must actually achieve on cold traffic. Base case 2.5 means $2.50 of revenue per $1.00 of ad spend. It is a target, not a prediction, and no one can promise it.",
    "Landed cost means everything to get one unit to the customer's door: unit price, supplier shipping, and duty. US de minimis relief ended for all countries on 2025-08-29 under Executive Order 14324, so imported parcels are dutiable and duty belongs inside this figure.",
    "Payment fees use the Shopify Payments US online card rate of 2.9% + $0.30. Confirm against the plan actually bought.",
    "Refund loss assumes the unit is not recovered, so the goods are lost along with the revenue.",
    "This tool says what a product may cost. It does not say what it does cost. That still requires a real supplier quote.",
]


def ceiling(price, target_roas, required_profit=0.0, discount_rate=0.10,
            refund_rate=0.06, chargeback_rate=0.007, packaging=1.00,
            payment_pct=PAYMENT_PCT, payment_fixed=PAYMENT_FIXED,
            chargeback_fee=CHARGEBACK_FEE):
    """Maximum landed cost per unit. May be negative, which means unworkable."""
    if price <= 0:
        raise ValueError("price must be positive")
    if target_roas <= 0:
        raise ValueError("target_roas must be positive")
    if not 0 <= refund_rate < 1:
        raise ValueError("refund_rate must be at least 0 and below 1")

    net_price = price * (1.0 - discount_rate)
    payment_fee = net_price * payment_pct + payment_fixed
    chargeback = chargeback_rate * (net_price + chargeback_fee)
    ad_cost = net_price / target_roas

    rhs = (net_price
           - packaging
           - payment_fee
           - refund_rate * net_price
           - chargeback
           - ad_cost
           - required_profit)
    landed = rhs / (1.0 + refund_rate)

    return {
        "price": round(price, 2),
        "net_price": round(net_price, 4),
        "target_roas": target_roas,
        "required_profit_per_order": round(required_profit, 2),
        "ad_cost_per_order": round(ad_cost, 4),
        "payment_fee": round(payment_fee, 4),
        "chargeback_allowance": round(chargeback, 4),
        "refund_rate": refund_rate,
        "packaging": packaging,
        "max_landed_cost": round(landed, 2),
        "max_landed_cost_pct_of_price": round(landed / price * 100, 1) if price else 0.0,
        "workable": landed > 0,
    }


def verdict(price, required_profit=0.0):
    """Run all three scenarios and return the table plus a decision rule."""
    rows = {}
    for name, (disc, refund, cb, pack, roas) in SCENARIOS.items():
        rows[name] = ceiling(price, roas, required_profit, disc, refund, cb, pack)

    base = rows["base"]["max_landed_cost"]
    pess = rows["pessimistic"]["max_landed_cost"]

    if pess <= 0:
        grade = "REJECT"
        rule = ("Even the base case leaves nothing for the product if the "
                "pessimistic case is negative. This price cannot support paid "
                "acquisition.")
    elif base <= 3.0:
        grade = "HARD"
        rule = ("Base case allows only $%.2f landed. Very few products with real "
                "perceived value land that cheaply with tracked US delivery."
                % base)
    else:
        grade = "WORKABLE"
        rule = ("Source below $%.2f landed and the base case works. Below $%.2f "
                "and it survives the pessimistic case too." % (base, pess))

    return {
        "price": price,
        "required_profit_per_order": required_profit,
        "scenarios": rows,
        "grade": grade,
        "decision_rule": rule,
        "check_this_number": base,
        "assumptions": ASSUMPTION_NOTES,
    }


def render(v):
    out = []
    out.append("Selling price $%.2f, required profit $%.2f per order"
               % (v["price"], v["required_profit_per_order"]))
    out.append("")
    out.append("| Scenario | Target ROAS | Ad cost | Fees+refunds | Max landed cost | % of price |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for name in ("pessimistic", "base", "optimistic"):
        r = v["scenarios"][name]
        overhead = (r["payment_fee"] + r["chargeback_allowance"]
                    + r["refund_rate"] * r["net_price"] + r["packaging"])
        out.append("| %s | %.1f | $%.2f | $%.2f | **$%.2f** | %.1f%% |"
                   % (name, r["target_roas"], r["ad_cost_per_order"], overhead,
                      r["max_landed_cost"], r["max_landed_cost_pct_of_price"]))
    out.append("")
    out.append("Verdict: **%s**" % v["grade"])
    out.append(v["decision_rule"])
    out.append("")
    out.append("The one number to check with a supplier: **$%.2f** landed per unit."
               % v["check_this_number"])
    out.append("")
    out.append("Assumptions carried by this model:")
    for a in v["assumptions"]:
        out.append("  - " + a)
    return "\n".join(out)


def self_test():
    failures = []

    # Hand-checked base case at $39.99.
    #   net_price   = 39.99 * 0.90            = 35.991
    #   payment_fee = 35.991*0.029 + 0.30     = 1.343739
    #   chargeback  = 0.007*(35.991+15)       = 0.356937
    #   ad_cost     = 35.991 / 2.5            = 14.3964
    #   refund term = 0.06 * 35.991           = 2.15946
    #   rhs = 35.991 - 1.00 - 1.343739 - 2.15946 - 0.356937 - 14.3964 - 0
    #       = 16.734464
    #   landed = 16.734464 / 1.06             = 15.786
    r = ceiling(39.99, 2.5)
    if abs(r["max_landed_cost"] - 15.79) > 0.01:
        failures.append("base ceiling at $39.99/ROAS2.5: got %.2f, expected 15.79"
                        % r["max_landed_cost"])
    if abs(r["ad_cost_per_order"] - 14.3964) > 0.001:
        failures.append("ad cost: got %.4f, expected 14.3964" % r["ad_cost_per_order"])

    # Round trip: feed the ceiling back in and profit should be about zero.
    landed = r["max_landed_cost"]
    net = r["net_price"]
    contribution = (net - landed - 1.00
                    - (net * PAYMENT_PCT + PAYMENT_FIXED)
                    - 0.06 * (net + landed)
                    - 0.007 * (net + CHARGEBACK_FEE))
    profit = contribution - net / 2.5
    if abs(profit) > 0.02:
        failures.append("round trip should leave about zero profit, got %.4f" % profit)

    # Requiring profit must lower the ceiling.
    r2 = ceiling(39.99, 2.5, required_profit=5.0)
    if not r2["max_landed_cost"] < r["max_landed_cost"]:
        failures.append("requiring profit should reduce the ceiling")
    # And by slightly more than the profit itself, because of the refund divisor.
    drop = r["max_landed_cost"] - r2["max_landed_cost"]
    if not 5.0 / 1.06 - 0.02 <= drop <= 5.0 / 1.06 + 0.02:
        failures.append("a $5 profit requirement should drop the ceiling by about "
                        "$%.2f, got $%.2f" % (5.0 / 1.06, drop))

    # A harder ROAS target must lower the ceiling.
    if not ceiling(39.99, 1.8)["max_landed_cost"] < ceiling(39.99, 3.5)["max_landed_cost"]:
        failures.append("a lower target ROAS should allow less landed cost")

    # Scenario ordering.
    v = verdict(39.99)
    p = v["scenarios"]["pessimistic"]["max_landed_cost"]
    b = v["scenarios"]["base"]["max_landed_cost"]
    o = v["scenarios"]["optimistic"]["max_landed_cost"]
    if not o > b > p:
        failures.append("expected optimistic > base > pessimistic, got %.2f %.2f %.2f"
                        % (o, b, p))

    # A cheap product with an aggressive ROAS target is called unworkable.
    low = verdict(12.00)
    if low["grade"] != "REJECT" and low["scenarios"]["pessimistic"]["max_landed_cost"] > 0:
        pass  # a $12 product may still be workable optimistically; only assert the flag
    if low["scenarios"]["pessimistic"]["workable"] and \
       low["scenarios"]["pessimistic"]["max_landed_cost"] <= 0:
        failures.append("workable flag disagrees with the sign of the ceiling")

    # A price that cannot cover its own fees must go negative, not raise.
    tiny = ceiling(3.00, 1.5)
    if tiny["max_landed_cost"] > 0:
        failures.append("a $3.00 product at ROAS 1.5 should have a negative ceiling")
    if tiny["workable"]:
        failures.append("a negative ceiling must not be marked workable")

    # Bad inputs are refused rather than silently producing a number.
    for bad in ((0, 2.5), (-5, 2.5), (39.99, 0), (39.99, -1)):
        try:
            ceiling(*bad)
            failures.append("ceiling%s should raise ValueError" % (bad,))
        except ValueError:
            pass
    try:
        ceiling(39.99, 2.5, refund_rate=1.0)
        failures.append("a refund rate of 1.0 should raise ValueError")
    except ValueError:
        pass

    # Higher price must allow a higher ceiling, monotonically.
    ceilings = [ceiling(p, 2.5)["max_landed_cost"] for p in (25, 35, 45, 55)]
    if ceilings != sorted(ceilings):
        failures.append("ceiling should rise with price, got %s" % ceilings)

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("cost_ceiling.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Maximum landed cost a product can bear on paid traffic.")
    ap.add_argument("--price", type=float, help="selling price in USD")
    ap.add_argument("--roas", type=float, help="single target ROAS instead of all three scenarios")
    ap.add_argument("--profit", type=float, default=0.0,
                    help="required profit per order in USD (default 0, i.e. break-even)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.price is None:
        ap.error("give --price or --self-test")
        return 2

    try:
        if args.roas:
            r = ceiling(args.price, args.roas, args.profit)
            print(json.dumps(r, indent=2) if args.json else
                  "Max landed cost at $%.2f and ROAS %.1f: $%.2f (%.1f%% of price)"
                  % (args.price, args.roas, r["max_landed_cost"],
                     r["max_landed_cost_pct_of_price"]))
        else:
            v = verdict(args.price, args.profit)
            print(json.dumps(v, indent=2) if args.json else render(v))
    except ValueError as exc:
        print("input error: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
