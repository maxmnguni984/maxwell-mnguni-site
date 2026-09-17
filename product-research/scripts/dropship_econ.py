#!/usr/bin/env python3
"""Dropshipping unit economics: single-unit fulfilment, no inventory.

    python3 scripts/dropship_econ.py products/ds-shear.yaml
    python3 scripts/dropship_econ.py products/ds-shear.yaml --json
    python3 scripts/dropship_econ.py products/ds-shear.yaml --cac-grid

This is NOT the bulk-import model in unit_econ.py with different numbers. The
cost structure is genuinely different and the differences run both ways.

GONE, because there is no inventory:
  inbound sea freight, customs entry amortised over an order, pre-shipment
  inspection, warehouse receiving, storage, pick and pack, tooling amortised,
  cargo insurance on a container, FX on a balance payment, and - the reason
  anyone does this - the five-figure cash outlay before the first sale.

NEW OR WORSE, because every parcel is its own import:
  the supplier's single-unit price, which is typically well above the same
  item's price at 500 units; a per-parcel international shipping charge;
  DUTY ON EVERY PARCEL, because the US de minimis exemption is repealed, so
  the $800 threshold that made dropshipping work no longer exists; a
  per-parcel clearance or brokerage charge; and a refund allowance that
  recovers almost nothing, because a unit returned to a US address cannot be
  economically shipped back to China.

DEFINITION OF "NET". Net revenue is the retail price less discounts actually
given. It excludes sales tax, which is collected on behalf of a state and was
never yours. It excludes shipping revenue unless the spec sets
shipping_charged_usd, in which case that is added to net revenue and the
outbound cost is charged separately, so the two never silently cancel.

THE THRESHOLDS, stated plainly:
  Contribution before advertising is what is left of net revenue after every
  non-advertising cost. Advertising is paid out of it, so contribution IS the
  break-even customer acquisition cost.
    45% (preferred)   -> break-even ROAS 2.22. For each $1 of net revenue,
                         45 cents is available to buy the customer and keep.
    35% (conditional) -> break-even ROAS 2.86.
  Both also require contribution >= $20 in absolute dollars. The percentage
  alone is not enough: 45% of a $30 order is a $13.50 break-even CAC, and at
  a $0.87 cost per click that needs 6.4% of visitors to buy, which is roughly
  three times any plausible cold-traffic conversion rate. The dollar floor is
  what keeps the required conversion rate inside the achievable range.

No network access, no dependencies, standard library only.
"""

import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unit_econ import parse_simple_yaml  # noqa: E402

FIELDS = (
    "retail_price_usd", "discount_rate_pct", "shipping_charged_usd",
    "supplier_unit_usd",            # single-unit dropship price, NOT bulk ex-factory
    "supplier_shipping_usd",        # per-parcel, supplier to customer
    "duty_rate_pct",                # on declared customs value; de minimis is repealed
    "declared_value_basis",         # "supplier_unit" or "retail"
    "clearance_fee_usd",            # per-parcel brokerage / entry / disbursement
    "duty_paid_by",                 # "seller" (DDP) or "customer" (DDU)
    "neutral_packaging_surcharge_usd",
    "payment_fee_pct", "payment_fee_fixed_usd", "platform_fee_pct",
    "return_rate_pct", "return_recovery_pct", "return_shipping_paid_by_us_usd",
    "defect_rate_pct", "chargeback_rate_pct", "chargeback_fee_usd",
    "support_usd",
    "processing_days", "transit_days_low", "transit_days_high",
)

DEFAULTS = {
    "discount_rate_pct": 10.0,
    "shipping_charged_usd": 0.0,
    # Duty is assessed on TRANSACTION VALUE - what you pay the supplier, not
    # retail. US de minimis is gone: suspended for all countries since
    # 2025-08-29, re-grounded 2026-06-24 on CBP's own 19 USC 1321 + TFTEA
    # authority (so the Feb 2026 Supreme Court IEEPA ruling did not restore
    # it), and terminated by statute from 2027-07-01. There is no value floor
    # below which a commercial parcel enters free.
    "duty_rate_pct": 0.0,
    "declared_value_basis": "supplier_unit",
    # VERIFIED* 2026-09-17. This is floor-driven and does NOT scale with parcel
    # value, which is what makes low-value cross-border uneconomic:
    #   ECCF fee per air waybill ~$1.38 (19 CFR 24.23(b)(4)(i), FY2027 factor).
    #     In the express channel this applies IN LIEU OF the informal MPF of
    #     $2.77 - do not charge both. Most spreadsheets get this wrong.
    #   Carrier disbursement/advancement floor: UPS 3.5% min $14.00;
    #     FedEx greater of $17.50 or 2.5%, raised in 2026 from $15.00/2%.
    #   A standalone broker filing instead would be $50-150 per entry (CLAIM),
    #     at which level nothing in this price band survives.
    "clearance_fee_usd": 20.0,
    "duty_paid_by": "seller",
    "neutral_packaging_surcharge_usd": 0.0,
    "payment_fee_pct": 2.9,
    "payment_fee_fixed_usd": 0.30,
    "platform_fee_pct": 0.0,
    "return_rate_pct": 8.0,
    # A returned unit goes to a US address. Shipping it back to China costs more
    # than the unit is worth, so recovery is near zero unless a US return hub
    # exists. This is the single biggest structural difference from holding stock.
    "return_recovery_pct": 0.0,
    "return_shipping_paid_by_us_usd": 0.0,
    "defect_rate_pct": 3.0,
    "chargeback_rate_pct": 0.8,
    "chargeback_fee_usd": 15.0,
    "support_usd": 1.00,
}

DOWNSIDE = {
    "supplier_unit_usd": 1.20, "supplier_shipping_usd": 1.35, "duty_rate_pct": 1.40,
    "clearance_fee_usd": 1.30, "discount_rate_pct": 1.50, "return_rate_pct": 1.75,
    "defect_rate_pct": 1.80, "chargeback_rate_pct": 1.75, "support_usd": 1.60,
}
SEVERE = {
    "supplier_unit_usd": 1.40, "supplier_shipping_usd": 1.80, "duty_rate_pct": 2.00,
    "clearance_fee_usd": 1.60, "discount_rate_pct": 2.00, "return_rate_pct": 2.75,
    "defect_rate_pct": 3.00, "chargeback_rate_pct": 3.00, "support_usd": 2.40,
}

GATE_CONTRIBUTION_USD = 20.0
BAND_A_MARGIN_PCT = 45.0
BAND_B_MARGIN_PCT = 35.0
CPC_ANCHORS = (("blended ecommerce, $0.87", 0.87), ("TikTok, $1.00", 1.00), ("Meta all-industry, $1.72", 1.72))


def apply_scenario(base, mult):
    out = dict(base)
    for k, f in mult.items():
        if k in out and isinstance(out[k], (int, float)):
            out[k] = out[k] * f
    for k in ("discount_rate_pct", "return_rate_pct", "defect_rate_pct", "chargeback_rate_pct"):
        if k in out:
            out[k] = min(out[k], 95.0)
    return out


def compute(v):
    retail = float(v["retail_price_usd"])
    disc_pct = float(v["discount_rate_pct"])
    discounts = retail * disc_pct / 100.0
    ship_rev = float(v["shipping_charged_usd"])
    net = retail - discounts + ship_rev

    product = float(v["supplier_unit_usd"])
    ship_cost = float(v["supplier_shipping_usd"])
    neutral = float(v["neutral_packaging_surcharge_usd"])

    basis = str(v.get("declared_value_basis", "supplier_unit"))
    declared = retail if basis == "retail" else product
    duty_full = declared * float(v["duty_rate_pct"]) / 100.0
    seller_pays_duty = str(v.get("duty_paid_by", "seller")) == "seller"
    duty = duty_full if seller_pays_duty else 0.0
    clearance = float(v["clearance_fee_usd"]) if seller_pays_duty else 0.0

    fulfilment = ship_cost + neutral + duty + clearance
    support = float(v["support_usd"])

    payment_fee = net * float(v["payment_fee_pct"]) / 100.0 + float(v["payment_fee_fixed_usd"])
    platform_fee = net * float(v["platform_fee_pct"]) / 100.0

    # A refund gives back the net revenue. The goods are already gone and the
    # shipping is already spent; recovery is whatever fraction of the product
    # cost can realistically be recovered, which for China-direct is ~0.
    r = float(v["return_rate_pct"]) / 100.0
    rec = float(v["return_recovery_pct"]) / 100.0
    ret_ship = float(v["return_shipping_paid_by_us_usd"])
    refund_allowance = r * (net + payment_fee + ret_ship - rec * product)

    # A defect is resolved by reshipping: a second product cost and a second
    # parcel, with no revenue against it.
    d = float(v["defect_rate_pct"]) / 100.0
    defect_allowance = d * (product + ship_cost + duty + clearance)

    cb = float(v["chargeback_rate_pct"]) / 100.0
    chargeback_allowance = cb * (net + float(v["chargeback_fee_usd"]))

    losses = refund_allowance + defect_allowance + chargeback_allowance

    contribution = net - product - fulfilment - support - payment_fee - platform_fee - losses
    margin = (contribution / net * 100.0) if net else 0.0

    return {
        "retail": retail, "discounts": discounts, "ship_rev": ship_rev, "net": net,
        "product": product, "ship_cost": ship_cost, "neutral": neutral,
        "declared": declared, "duty_full": duty_full, "duty": duty, "clearance": clearance,
        "seller_pays_duty": seller_pays_duty,
        "fulfilment": fulfilment, "support": support,
        "payment_fee": payment_fee, "platform_fee": platform_fee,
        "refund_allowance": refund_allowance, "defect_allowance": defect_allowance,
        "chargeback_allowance": chargeback_allowance, "losses": losses,
        "contribution": contribution, "margin_pct": margin,
        "be_cac": contribution,
        "be_roas": (net / contribution) if contribution > 0 else None,
    }


def band(r):
    if r["contribution"] < GATE_CONTRIBUTION_USD:
        return "NEITHER"
    if r["margin_pct"] >= BAND_A_MARGIN_PCT:
        return "A"
    if r["margin_pct"] >= BAND_B_MARGIN_PCT:
        return "B"
    return "NEITHER"


def m(x):
    return "${:,.2f}".format(x)


def show_formula(name, r, v):
    print("=" * 78)
    print(name)
    print("=" * 78)
    print()
    print("THE FORMULA, WITH DOLLARS. One order, single-unit fulfilment.")
    print("-" * 78)
    print("  {:<46}{:>14}".format("retail price", m(r["retail"])))
    print("  {:<46}{:>14}".format("less discounts given (%.0f%%)" % float(v["discount_rate_pct"]), "-" + m(r["discounts"])))
    if r["ship_rev"]:
        print("  {:<46}{:>14}".format("plus shipping charged to customer", "+" + m(r["ship_rev"])))
    print("  {:<46}{:>14}   <- NET REVENUE".format("= NET REVENUE", m(r["net"])))
    print("     (excludes sales tax, which is the state's, never yours)")
    print()
    print("  {:<46}{:>14}".format("less product cost (supplier, 1 unit)", "-" + m(r["product"])))
    print("  {:<46}{:>14}".format("less shipping, supplier to customer", "-" + m(r["ship_cost"])))
    if r["neutral"]:
        print("  {:<46}{:>14}".format("less neutral-packaging surcharge", "-" + m(r["neutral"])))
    if r["seller_pays_duty"]:
        print("  {:<46}{:>14}".format("less import duty on %s" % m(r["declared"]), "-" + m(r["duty"])))
        print("  {:<46}{:>14}".format("less per-parcel clearance fee", "-" + m(r["clearance"])))
    else:
        print("  {:<46}{:>14}".format("import duty billed to the CUSTOMER", "(" + m(r["duty_full"]) + ")"))
        print("     NOT a cost to you, and a serious conversion and refund risk. See the note below.")
    print("  {:<46}{:>14}   <- FULFILMENT".format("= FULFILMENT COST", m(r["fulfilment"])))
    print()
    print("  {:<46}{:>14}".format("less customer support per order", "-" + m(r["support"])))
    print("  {:<46}{:>14}".format("less payment processing", "-" + m(r["payment_fee"])))
    if r["platform_fee"]:
        print("  {:<46}{:>14}".format("less platform fee", "-" + m(r["platform_fee"])))
    print()
    print("  refund allowance   = %.1f%% x (net + payment fee + return shipping - recovery)" % float(v["return_rate_pct"]))
    print("  {:<46}{:>14}".format("", "-" + m(r["refund_allowance"])))
    print("  defect allowance   = %.1f%% x (product + shipping + duty + clearance)" % float(v["defect_rate_pct"]))
    print("  {:<46}{:>14}".format("", "-" + m(r["defect_allowance"])))
    print("  chargeback allowance = %.2f%% x (net + %s fee)" % (float(v["chargeback_rate_pct"]), m(float(v["chargeback_fee_usd"]))))
    print("  {:<46}{:>14}".format("", "-" + m(r["chargeback_allowance"])))
    print("  {:<46}{:>14}   <- LOSSES".format("= LOSS ALLOWANCES", m(r["losses"])))
    print()
    print("-" * 78)
    print("  {:<46}{:>14}".format("CONTRIBUTION BEFORE ADVERTISING", m(r["contribution"])))
    print("  {:<46}{:>14}".format("  as % of net revenue", "{:.1f}%".format(r["margin_pct"])))
    print("  {:<46}{:>14}".format("BREAK-EVEN CAC (same number, by definition)", m(r["be_cac"])))
    print("  {:<46}{:>14}".format("BREAK-EVEN ROAS", "n/a" if r["be_roas"] is None else "{:.2f}".format(r["be_roas"])))
    print("  {:<46}{:>14}".format("BAND", band(r)))
    print("-" * 78)
    print()


def show_cac(scenarios):
    print("PROFIT OR LOSS PER ORDER, BY ACQUISITION COST")
    print("  Contribution is positive => there IS a positive break-even CAC. The")
    print("  question is never whether one exists, but whether it is reachable.")
    print("-" * 78)
    labels = [s[0] for s in scenarios]
    print("  {:<28}".format("acquisition cost") + "".join("{:>15}".format(l) for l in labels))
    for cac in (5.0, 10.0, 15.0, 20.0, 25.0, 35.0):
        cells = "".join("{:>15}".format(("+" if (r["contribution"] - cac) >= 0 else "") + "{:,.2f}".format(r["contribution"] - cac))
                        for _, r in scenarios)
        print("  {:<28}{}".format("$%.0f" % cac, cells))
    print()
    print("  {:<28}".format("break-even CAC")
          + "".join("{:>15}".format(m(r["be_cac"]) if r["contribution"] > 0 else "none") for _, r in scenarios))
    print()
    print("  REQUIRED CONVERSION RATE for advertising to pay for itself")
    print("  (= cost per click / break-even CAC; a cold-traffic rate above about 3% is")
    print("   outside anything this project found evidence for)")
    for label, cpc in CPC_ANCHORS:
        cells = ""
        for _, r in scenarios:
            if r["contribution"] > 0:
                cells += "{:>15}".format("{:.2f}%".format(cpc / r["contribution"] * 100.0))
            else:
                cells += "{:>15}".format("impossible")
        print("  {:<28}{}".format(label, cells))
    print()


def load(path):
    raw = parse_simple_yaml(path)
    v = dict(DEFAULTS)
    for k in FIELDS:
        if k in raw:
            v[k] = raw[k]
    missing = [k for k in ("retail_price_usd", "supplier_unit_usd", "supplier_shipping_usd") if k not in v]
    if missing:
        sys.exit("spec is missing required field(s): {}".format(", ".join(missing)))
    return raw, v


def main(argv=None):
    ap = argparse.ArgumentParser(description="Dropshipping unit economics, single-unit fulfilment.")
    ap.add_argument("spec")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if not os.path.exists(args.spec):
        sys.exit("no such spec: " + args.spec)

    raw, v = load(args.spec)
    name = raw.get("name", os.path.basename(args.spec))
    scenarios = [("base", compute(v)),
                 ("downside", compute(apply_scenario(v, DOWNSIDE))),
                 ("severe", compute(apply_scenario(v, SEVERE)))]

    if args.json:
        print(json.dumps({"name": name, "scenarios": {
            l: {"net": round(r["net"], 2), "contribution": round(r["contribution"], 2),
                "margin_pct": round(r["margin_pct"], 1), "be_cac": round(r["be_cac"], 2),
                "be_roas": None if r["be_roas"] is None else round(r["be_roas"], 2),
                "band": band(r)} for l, r in scenarios}}, indent=2))
        return 0

    show_formula(name, scenarios[0][1], v)

    print("THE SAME THREE LINES UNDER EACH SCENARIO")
    print("  {:<30}{:>14}{:>14}{:>14}".format("", "base", "downside", "severe"))
    for label, key, f in (("contribution before ads", "contribution", m),
                          ("as % of net", "margin_pct", lambda x: "{:.1f}%".format(x)),
                          ("break-even CAC", "be_cac", m)):
        print("  {:<30}{}".format(label, "".join("{:>14}".format(f(r[key])) for _, r in scenarios)))
    print("  {:<30}{}".format("band", "".join("{:>14}".format(band(r)) for _, r in scenarios)))
    print()

    show_cac(scenarios)

    print("FULFILMENT FACTS THAT ARE NOT COSTS BUT DECIDE THE BUSINESS")
    for key, label in (("processing_days", "supplier processing days"),
                       ("transit_days_low", "transit days, fastest reported"),
                       ("transit_days_high", "transit days, slowest reported")):
        val = raw.get(key, "UNKNOWN")
        print("  {:<40}{}".format(label, val))
    print("  {:<40}{}".format("duty paid by", v.get("duty_paid_by")))
    if str(v.get("duty_paid_by")) != "seller":
        print()
        print("  WARNING: duty billed to the customer on delivery is modelled as zero cost")
        print("  to you, which is arithmetically true and commercially false. A surprise")
        print("  customs bill is the single most cited cause of refused delivery. Baymard")
        print("  attributes 40% of checkout abandonment to unexpected extra costs. If you")
        print("  ship DDU, raise the refund rate until it reflects refused parcels, or")
        print("  model it as DDP and price the duty in.")
    print()
    print("CASH AT RISK BEFORE THE FIRST SALE")
    print("  Inventory outlay                        $0.00")
    print("  This is the entire argument for the model, and it is a real one.")
    print("  What it buys in exchange: no control of lead time, no control of packaging,")
    print("  no unit to inspect before a customer sees it, and a refund that recovers")
    print("  nothing because the goods are in a customer's house and the supplier is")
    print("  8,000 miles away.")
    print()

    un = raw.get("unverified_inputs")
    if un:
        print("UNVERIFIED INPUTS declared in the spec:")
        print("  {}".format(un))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
