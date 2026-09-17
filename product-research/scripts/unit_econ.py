#!/usr/bin/env python3
"""Full-stack unit economics, dual threshold, with advertising-cost scenarios.

    python3 unit_econ.py products/candidate.yaml
    python3 unit_econ.py products/candidate.yaml --sensitivity
    python3 unit_econ.py products/candidate.yaml --json

CONTRIBUTION HERE ALWAYS MEANS CONTRIBUTION BEFORE ADVERTISING. Advertising is
paid out of it, which is why contribution is also the break-even customer
acquisition cost. Nothing in this file credits a second purchase: every figure
is the first order, standing on its own.

--------------------------------------------------------------------------
CHANGES MADE 2026-09-17 AFTER REVIEW. Two were arithmetic errors, not gaps.

1. RETURNS WERE UNDERSTATED, BADLY (error). The old model charged a return
   `landed * (1 - resellable)` and never reversed the refunded revenue. A
   return is a refund: you give back the net price, you eat the outbound
   postage, usually a share of the return postage, and usually the payment
   processor keeps its fee. What you get back is the unit itself, worth its
   landed cost, and only for the share that is resellable. Measured on the
   worked example by scripts/model_check.py: the old formula charged $1.95 a
   unit where the correct one charges $7.33, an understatement of $5.38. With
   the chargeback fix netted off, the two corrections together move that spec
   from 51.2% to 45.3% of net revenue - 5.87 margin points, and the difference
   between comfortably clearing a 45% gate and sitting exactly on it.

2. CHARGEBACKS WERE DOUBLE-COUNTED (error). The old model charged
   `landed + fulfilment` again on a chargeback, although both were already
   subtracted for every unit shipped. In a chargeback the customer keeps the
   goods and you lose the money: the loss is the revenue plus the fee. Small
   in absolute terms, but wrong in the same direction as everything else a
   founder does to their own spreadsheet.

3. RETURN POSTAGE DID NOT MOVE IN THE DOWNSIDE CASE (inconsistency). It was
   copied from outbound postage before the scenario multipliers ran, so a
   downside that raised outbound postage 25% left return postage at base.

4. DIMENSIONAL WEIGHT (gap). US domestic parcels bill on the greater of actual
   and volumetric weight. A light bulky box was previously costed on actual
   weight only, which flatters exactly the product that looks cheapest.

5. CARGO INSURANCE, FX SLIPPAGE, CUSTOMER SUPPORT (gaps). All three are real
   cash, all three were missing.

6. FOUNDER'S TIME (gap, handled deliberately). It is NOT in contribution,
   because contribution has to stay comparable across candidates and time is
   not cash out of the bank. It is reported as a separate shadow line, so a
   product that only works by paying yourself nothing is visible as such.

7. DUTY BASE (gap). Tooling paid to the factory is an assist and is generally
   part of transaction value, so it is dutiable by default.

No network access, no dependencies, standard library only.
"""

import argparse
import json
import math
import os
import sys

# --------------------------------------------------------------------- input

FIELDS = (
    # revenue side
    "retail_price_usd",
    "discount_rate_pct",
    # goods
    "exfactory_usd",
    "tooling_total_usd",
    "tooling_dutiable",
    "factory_packaging_usd",
    "first_order_units",
    "moq_units",
    "packaging_usd",
    # inbound
    "inbound_freight_usd",
    "duty_rate_pct",
    "customs_entry_total_usd",
    "inspection_total_usd",
    "cargo_insurance_pct",
    "fx_slippage_pct",
    "fx_exposed_share_pct",
    # warehouse and outbound
    "receiving_usd",
    "storage_usd",
    "pick_pack_usd",
    "outbound_postage_usd",
    "postage_base_usd",
    "postage_per_kg_usd",
    "packed_weight_kg",
    "packed_length_cm", "packed_width_cm", "packed_height_cm",
    "dim_divisor_cm3_per_kg",
    "support_usd",
    # money
    "payment_fee_pct",
    "payment_fee_fixed_usd",
    "platform_fee_pct",
    # losses
    "return_rate_pct",
    "return_postage_paid_by_us_pct",
    "return_postage_usd",
    "return_handling_usd",
    "resellable_after_return_pct",
    "defect_rate_pct",
    "chargeback_rate_pct",
    "chargeback_fee_usd",
    # shadow line, never inside contribution
    "founder_minutes_per_order",
    "founder_hourly_usd",
)

DEFAULTS = {
    "discount_rate_pct": 10.0,
    "tooling_total_usd": 0.0,
    "tooling_dutiable": 1.0,          # assists are generally part of transaction value
    "factory_packaging_usd": 0.0,     # retail box bought from the factory, dutiable
    "first_order_units": 500,
    "moq_units": 500,
    "packaging_usd": 1.00,            # domestic mailer and insert, not dutiable
    "duty_rate_pct": 0.0,
    "customs_entry_total_usd": 900.0,
    "inspection_total_usd": 300.0,
    "cargo_insurance_pct": 0.40,      # of goods + freight + duty
    "fx_slippage_pct": 2.00,          # movement between deposit and balance payment
    "fx_exposed_share_pct": 70.0,     # the balance, typically 70% of the order
    "receiving_usd": 0.50,
    "storage_usd": 0.60,
    "pick_pack_usd": 2.75,
    "dim_divisor_cm3_per_kg": 5000.0, # 139 cu in per lb expressed in metric
    "support_usd": 0.50,              # helpdesk seat and per-order handling, cash only
    "payment_fee_pct": 2.9,
    "payment_fee_fixed_usd": 0.30,
    "platform_fee_pct": 0.0,
    "return_rate_pct": 8.0,
    "return_postage_paid_by_us_pct": 50.0,
    "return_handling_usd": 2.00,      # inspect, repack, restock
    "resellable_after_return_pct": 60.0,
    "defect_rate_pct": 2.0,
    "chargeback_rate_pct": 0.4,
    "chargeback_fee_usd": 15.0,
    "founder_minutes_per_order": 6.0,
    "founder_hourly_usd": 25.0,
}

DOWNSIDE = {
    "exfactory_usd": 1.25, "inbound_freight_usd": 1.40, "outbound_postage_usd": 1.25,
    "postage_base_usd": 1.25, "postage_per_kg_usd": 1.25, "return_postage_usd": 1.25,
    "duty_rate_pct": 1.50, "discount_rate_pct": 1.50, "return_rate_pct": 1.75,
    "defect_rate_pct": 2.00, "chargeback_rate_pct": 1.50, "packaging_usd": 1.20,
    "pick_pack_usd": 1.15, "resellable_after_return_pct": 0.70,
    "fx_slippage_pct": 1.50, "support_usd": 1.50, "return_handling_usd": 1.25,
    "packed_weight_kg": 1.10,
}
SEVERE = {
    "exfactory_usd": 1.45, "inbound_freight_usd": 1.90, "outbound_postage_usd": 1.45,
    "postage_base_usd": 1.45, "postage_per_kg_usd": 1.45, "return_postage_usd": 1.45,
    "duty_rate_pct": 2.20, "discount_rate_pct": 2.00, "return_rate_pct": 2.75,
    "defect_rate_pct": 4.00, "chargeback_rate_pct": 2.50, "packaging_usd": 1.40,
    "pick_pack_usd": 1.30, "resellable_after_return_pct": 0.35,
    "fx_slippage_pct": 2.50, "support_usd": 2.50, "return_handling_usd": 1.50,
    "packed_weight_kg": 1.20,
}

# Gates. Contribution is BEFORE advertising in all three.
GATE_CONTRIBUTION_USD = 20.0
BAND_A_MARGIN_PCT = 45.0          # preferred target
BAND_B_MARGIN_PCT = 35.0          # conditional floor
GATE_MAX_BE_ROAS = 2.2            # equivalent to band A by construction

# Cost-per-click anchors used to invert CAC into a required conversion rate.
# ESTIMATE, from third-party vendor panels that disagree with each other by
# two to three times. Not measured for this product and not a forecast.
CPC_ANCHORS = (
    ("TikTok, $1.00 CPC", 1.00),
    ("blended ecommerce, $0.87 CPC", 0.87),
    ("Meta all-industry, $1.72 CPC", 1.72),
)


def parse_simple_yaml(path):
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
            if value.lower() in ("true", "yes"):
                data[key] = 1.0
            elif value.lower() in ("false", "no"):
                data[key] = 0.0
            else:
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
    for key in ("discount_rate_pct", "return_rate_pct", "defect_rate_pct", "chargeback_rate_pct"):
        if key in out:
            out[key] = min(out[key], 95.0)
    if "resellable_after_return_pct" in out:
        out["resellable_after_return_pct"] = max(0.0, min(out["resellable_after_return_pct"], 100.0))
    return out


# ----------------------------------------------------------------- the model

def billable_weight(v):
    """US domestic parcels bill on the greater of actual and volumetric weight."""
    actual = float(v.get("packed_weight_kg", 0.0) or 0.0)
    l = float(v.get("packed_length_cm", 0.0) or 0.0)
    w = float(v.get("packed_width_cm", 0.0) or 0.0)
    h = float(v.get("packed_height_cm", 0.0) or 0.0)
    divisor = float(v.get("dim_divisor_cm3_per_kg", 5000.0) or 5000.0)
    dim = (l * w * h / divisor) if (l and w and h and divisor) else 0.0
    return max(actual, dim), actual, dim


def compute(v):
    """Per-order economics for one scenario. Contribution is before advertising."""
    units = max(1.0, float(v["first_order_units"]))

    price = float(v["retail_price_usd"])
    net_price = price * (1 - float(v["discount_rate_pct"]) / 100.0)

    # --- goods and inbound ----------------------------------------------
    exfactory = float(v["exfactory_usd"])
    tooling = float(v["tooling_total_usd"]) / units
    factory_pack = float(v.get("factory_packaging_usd", 0.0) or 0.0)

    duty_base = exfactory + factory_pack
    if float(v.get("tooling_dutiable", 1.0)):
        duty_base += tooling
    duty = duty_base * float(v["duty_rate_pct"]) / 100.0

    inbound = float(v["inbound_freight_usd"])
    cargo_ins = (exfactory + factory_pack + inbound + duty) * float(v["cargo_insurance_pct"]) / 100.0
    fx = ((exfactory + factory_pack + tooling)
          * float(v["fx_exposed_share_pct"]) / 100.0
          * float(v["fx_slippage_pct"]) / 100.0)
    entry = float(v["customs_entry_total_usd"]) / units
    inspection = float(v["inspection_total_usd"]) / units

    landed = (exfactory + factory_pack + tooling + duty + inbound
              + cargo_ins + fx + entry + inspection)

    # --- getting it to a customer ---------------------------------------
    packaging = float(v["packaging_usd"])
    warehouse = float(v["receiving_usd"]) + float(v["storage_usd"]) + float(v["pick_pack_usd"])
    bill_kg, actual_kg, dim_kg = billable_weight(v)
    if v.get("postage_per_kg_usd") is not None and bill_kg:
        postage = float(v.get("postage_base_usd", 0.0) or 0.0) + float(v["postage_per_kg_usd"]) * bill_kg
    else:
        postage = float(v["outbound_postage_usd"])
    support = float(v["support_usd"])
    fulfilment = packaging + warehouse + postage + support

    # --- money costs -----------------------------------------------------
    payment_fee = net_price * float(v["payment_fee_pct"]) / 100.0 + float(v["payment_fee_fixed_usd"])
    platform_fee = net_price * float(v["platform_fee_pct"]) / 100.0

    # --- losses ----------------------------------------------------------
    # A return is a REFUND. You reverse the net price, you have already spent
    # the outbound postage, you often pay return postage, the processor usually
    # keeps its fee, and you pay to inspect and restock. Against that you get
    # the unit back, worth its landed cost, for the resellable share only.
    r = float(v["return_rate_pct"]) / 100.0
    resell = float(v["resellable_after_return_pct"]) / 100.0
    ret_post_share = float(v["return_postage_paid_by_us_pct"]) / 100.0
    ret_post = float(v.get("return_postage_usd") or postage)
    ret_handling = float(v["return_handling_usd"])
    return_loss = r * (net_price + postage + ret_post_share * ret_post
                       + payment_fee + ret_handling - resell * landed)

    # A defect is resolved by shipping a replacement: a second unit's landed
    # cost, packaging, pick-pack and postage, with no revenue against it.
    d = float(v["defect_rate_pct"]) / 100.0
    defect_loss = d * (landed + postage + packaging + float(v["pick_pack_usd"]))

    # In a chargeback the customer keeps the goods and you lose the money. The
    # goods cost is already expensed for every unit shipped; charging it again
    # here would be a double count.
    cb = float(v["chargeback_rate_pct"]) / 100.0
    chargeback_loss = cb * (net_price + float(v["chargeback_fee_usd"]))

    losses = return_loss + defect_loss + chargeback_loss

    contribution = net_price - landed - fulfilment - payment_fee - platform_fee - losses
    margin_pct = (contribution / net_price * 100.0) if net_price else 0.0

    # Shadow line. Deliberately OUTSIDE contribution.
    founder_cost = float(v["founder_minutes_per_order"]) / 60.0 * float(v["founder_hourly_usd"])

    # Cash. Everything paid before a single customer exists.
    upfront = (exfactory + factory_pack + tooling + duty + inbound + cargo_ins + fx
               + entry + inspection + packaging + float(v["receiving_usd"])) * units

    return {
        "price": price, "net_price": net_price,
        "exfactory": exfactory, "factory_pack": factory_pack, "tooling": tooling,
        "duty": duty, "duty_base": duty_base, "inbound": inbound,
        "cargo_ins": cargo_ins, "fx": fx, "entry": entry, "inspection": inspection,
        "landed": landed,
        "packaging": packaging, "warehouse": warehouse, "postage": postage, "support": support,
        "fulfilment": fulfilment,
        "billable_kg": bill_kg, "actual_kg": actual_kg, "dim_kg": dim_kg,
        "payment_fee": payment_fee, "platform_fee": platform_fee,
        "return_loss": return_loss, "defect_loss": defect_loss,
        "chargeback_loss": chargeback_loss, "losses": losses,
        "contribution": contribution, "margin_pct": margin_pct,
        "founder_cost": founder_cost,
        "contribution_after_founder_time": contribution - founder_cost,
        "be_cac": contribution,
        "be_roas": (net_price / contribution) if contribution > 0 else None,
        "units": units,
        "upfront_cash": upfront,
    }


def band(r):
    """A, B or NEITHER. Contribution is before advertising in every test."""
    if r["contribution"] < GATE_CONTRIBUTION_USD:
        return "NEITHER"
    if r["margin_pct"] >= BAND_A_MARGIN_PCT:
        return "A"
    if r["margin_pct"] >= BAND_B_MARGIN_PCT:
        return "B"
    return "NEITHER"


def gates(r, threshold=BAND_A_MARGIN_PCT):
    checks = [
        ("contribution before ads >= $%.2f" % GATE_CONTRIBUTION_USD,
         r["contribution"] >= GATE_CONTRIBUTION_USD),
        ("contribution >= %.1f%% of net" % threshold, r["margin_pct"] >= threshold),
        ("break-even ROAS <= %.2f" % (100.0 / threshold),
         r["be_roas"] is not None and 0 < r["be_roas"] <= (100.0 / threshold)),
    ]
    return checks, all(ok for _, ok in checks)


# ---------------------------------------------------------------- reporting

def money(x):
    return "n/a" if x is None else "${:,.2f}".format(x)


def report(name, scenarios):
    print("=" * 84)
    print(name)
    print("=" * 84)

    rows = [
        ("Retail price", "price"), ("Net after discount", "net_price"),
        ("  ex-factory", "exfactory"), ("  factory packaging", "factory_pack"),
        ("  tooling amortised", "tooling"), ("  duty", "duty"),
        ("  inbound freight", "inbound"), ("  cargo insurance", "cargo_ins"),
        ("  fx slippage", "fx"), ("  customs entry amortised", "entry"),
        ("  inspection amortised", "inspection"),
        ("LANDED COST", "landed"),
        ("  packaging", "packaging"), ("  warehouse", "warehouse"),
        ("  outbound postage", "postage"), ("  customer support", "support"),
        ("FULFILMENT", "fulfilment"),
        ("Payment fee", "payment_fee"), ("Platform fee", "platform_fee"),
        ("  return loss", "return_loss"), ("  defect loss", "defect_loss"),
        ("  chargeback loss", "chargeback_loss"),
        ("LOSSES", "losses"),
    ]
    labels = [s[0] for s in scenarios]
    print("{:<32}".format("") + "".join("{:>16}".format(l) for l in labels))
    print("-" * 84)
    for label, key in rows:
        print("{:<32}".format(label) + "".join("{:>16}".format(money(r[key])) for _, r in scenarios))

    print("-" * 84)
    print("{:<32}".format("CONTRIBUTION (before ads)")
          + "".join("{:>16}".format(money(r["contribution"])) for _, r in scenarios))
    print("{:<32}".format("  as % of net revenue")
          + "".join("{:>16}".format("{:.1f}%".format(r["margin_pct"])) for _, r in scenarios))
    print("{:<32}".format("Break-even CAC")
          + "".join("{:>16}".format(money(r["be_cac"])) for _, r in scenarios))
    print("{:<32}".format("Break-even ROAS")
          + "".join("{:>16}".format("n/a" if r["be_roas"] is None else "{:.2f}".format(r["be_roas"]))
                    for _, r in scenarios))
    print("{:<32}".format("BAND")
          + "".join("{:>16}".format(band(r)) for _, r in scenarios))
    print()

    base = scenarios[0][1]
    if base["dim_kg"] > base["actual_kg"] and base["actual_kg"]:
        print("SHIPPING WEIGHT: billed on volume, not mass.")
        print("  actual {:.2f} kg, volumetric {:.2f} kg -> billed {:.2f} kg. "
              "The box is the cost, not the product."
              .format(base["actual_kg"], base["dim_kg"], base["billable_kg"]))
        print()

    print("BANDS (contribution is BEFORE advertising in every line)")
    print("  Band A, preferred:   contribution >= $%.0f and >= %.0f%% of net"
          % (GATE_CONTRIBUTION_USD, BAND_A_MARGIN_PCT))
    print("  Band B, conditional: contribution >= $%.0f and %.0f%% to %.1f%% of net"
          % (GATE_CONTRIBUTION_USD, BAND_B_MARGIN_PCT, BAND_A_MARGIN_PCT - 0.1))
    for label, r in scenarios:
        checks, _ = gates(r, BAND_A_MARGIN_PCT)
        detail = ", ".join(("ok " if ok else "FAIL ") + c for c, ok in checks)
        print("  {:<10} band {:<8} [{}]".format(label, band(r), detail))
    print()

    cac_scenarios(scenarios)
    cash_and_recovery(scenarios)


def cac_scenarios(scenarios):
    """Profit or loss per order at clearly labelled acquisition costs.

    No repeat purchase is credited anywhere. Every line is the first order.
    """
    base = scenarios[0][1]
    print("PROFIT OR LOSS PER ORDER, BY ACQUISITION COST")
    print("  No repeat purchase is credited. Each line is one first order, standing alone.")
    print("-" * 84)
    print("  {:<46}{:>11}{:>11}{:>11}".format("acquisition cost per order", "base", "downside", "severe"))

    anchors = []
    c = base["contribution"]
    if c > 0:
        for frac, tag in ((0.25, "25% of base contribution"), (0.50, "50% of base contribution"),
                          (0.75, "75% of base contribution"), (1.00, "100% = break-even, base")):
            anchors.append(("{} (${:.2f})".format(tag, c * frac), c * frac))
    for absolute in (15.0, 25.0, 40.0, 60.0):
        anchors.append(("$%.0f flat  [ESTIMATE, spanning value, not a forecast]" % absolute, absolute))

    for label, cac in anchors:
        cells = ""
        for _, r in scenarios:
            p = r["contribution"] - cac
            cells += "{:>11}".format(("+" if p >= 0 else "") + "{:,.2f}".format(p))
        print("  {:<46}{}".format(label, cells))
    print()
    print("  Every CAC above is an ASSUMPTION. No CAC has been measured for this product.")
    print("  A positive number is profit per order before overheads, tax and the founder's time.")
    print()

    if c > 0:
        print("  Break-even conversion rate implied by each CPC anchor:")
        print("    (required visitor-to-buyer rate for advertising to pay for itself)")
        for label, cpc in CPC_ANCHORS:
            rate = cpc / c * 100.0
            print("      {:<38} {:.2f}%".format(label, rate))
        print("    CPC figures are ESTIMATE, from third-party vendor panels that disagree")
        print("    with each other by two to three times. Not measured for this product.")
        print()


def cash_and_recovery(scenarios):
    base = scenarios[0][1]
    units = base["units"]
    print("CASH AT RISK BEFORE THE FIRST CUSTOMER EXISTS")
    print("  First order units              {:,.0f}".format(units))
    print("  Cash per unit                  {}".format(money(base["upfront_cash"] / units)))
    print("  TOTAL UPFRONT CASH             {}".format(money(base["upfront_cash"])))
    print("  (goods, tooling, duty, freight, insurance, fx, entry, inspection,")
    print("   packaging and receiving. Excludes advertising and any platform cost.)")
    print()
    for label, r in scenarios:
        prefix = "  Orders to recover outlay {:<11}".format("(" + label + ")")
        if r["contribution"] > 0:
            n = math.ceil(base["upfront_cash"] / r["contribution"])
            flag = "" if n <= units else "   <-- more orders than units ordered"
            print("{} {:>6}  of {:,.0f} units{}".format(prefix, n, units, flag))
        else:
            print("{} never, contribution is negative".format(prefix))
    print()
    print("  Founder's time, reported separately and NOT inside contribution:")
    for label, r in scenarios:
        print("    {:<10} {} per order -> contribution after own time {}"
              .format(label, money(r["founder_cost"]), money(r["contribution_after_founder_time"])))
    print()


def sensitivity(base_inputs, threshold):
    print("SENSITIVITY: what single change breaks the %.0f%% threshold?" % threshold)
    print("-" * 84)
    base = compute(base_inputs)
    _, base_ok = gates(base, threshold)
    print("  base: contribution {} at {:.1f}% of net  [{}]".format(
        money(base["contribution"]), base["margin_pct"], "PASS" if base_ok else "FAIL"))
    print()
    knobs = [
        ("ex-factory", "exfactory_usd", [1.1, 1.25, 1.5, 2.0]),
        ("outbound postage", "outbound_postage_usd", [1.25, 1.5, 2.0, 3.0]),
        ("postage per kg", "postage_per_kg_usd", [1.25, 1.5, 2.0, 3.0]),
        ("packed weight", "packed_weight_kg", [1.25, 1.5, 2.0]),
        ("duty rate", "duty_rate_pct", [1.5, 2.0, 3.0]),
        ("return rate", "return_rate_pct", [1.5, 2.0, 3.0]),
        ("discount given", "discount_rate_pct", [1.5, 2.0, 3.0]),
        ("defect rate", "defect_rate_pct", [2.0, 4.0, 8.0]),
    ]
    for label, key, factors in knobs:
        if key not in base_inputs or not isinstance(base_inputs.get(key), (int, float)):
            continue
        breaking = None
        for f in factors:
            trial = dict(base_inputs)
            trial[key] = base_inputs[key] * f
            _, ok = gates(compute(trial), threshold)
            if not ok:
                breaking = f
                break
        if breaking:
            print("  {:<20} breaks it at {:.0f}% of base ({:.2f}x)"
                  .format(label, breaking * 100, breaking))
        else:
            print("  {:<20} survives every tested increase".format(label))
    print()


def load(spec_path):
    raw = parse_simple_yaml(spec_path)
    inputs = dict(DEFAULTS)
    for key in FIELDS:
        if key in raw:
            inputs[key] = raw[key]
    missing = [k for k in ("retail_price_usd", "exfactory_usd", "inbound_freight_usd") if k not in inputs]
    has_postage = ("outbound_postage_usd" in inputs) or ("postage_per_kg_usd" in inputs)
    if not has_postage:
        missing.append("outbound_postage_usd or postage_per_kg_usd")
    if missing:
        sys.exit("spec is missing required field(s): {}".format(", ".join(missing)))
    inputs.setdefault("outbound_postage_usd", 0.0)
    if "return_postage_usd" not in inputs:
        bill_kg, _, _ = billable_weight(inputs)
        if inputs.get("postage_per_kg_usd") is not None and bill_kg:
            inputs["return_postage_usd"] = (float(inputs.get("postage_base_usd", 0.0) or 0.0)
                                            + float(inputs["postage_per_kg_usd"]) * bill_kg)
        else:
            inputs["return_postage_usd"] = inputs["outbound_postage_usd"]
    return raw, inputs


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Full-stack unit economics. Contribution is always BEFORE advertising.")
    parser.add_argument("spec")
    parser.add_argument("--sensitivity", action="store_true")
    parser.add_argument("--threshold", type=float, default=BAND_A_MARGIN_PCT,
                        help="margin threshold for the sensitivity run (45 = preferred, 35 = conditional)")
    parser.add_argument("--json", action="store_true", help="machine-readable, for batch comparison")
    args = parser.parse_args(argv)

    if not os.path.exists(args.spec):
        sys.exit("no such spec file: {}".format(args.spec))

    raw, inputs = load(args.spec)
    name = raw.get("name", os.path.basename(args.spec))

    scenarios = [
        ("base", compute(inputs)),
        ("downside", compute(apply_scenario(inputs, DOWNSIDE))),
        ("severe", compute(apply_scenario(inputs, SEVERE))),
    ]

    if args.json:
        out = {"name": name, "spec": os.path.basename(args.spec),
               "moq_units": inputs.get("moq_units"),
               "evidence": raw.get("evidence_quality", "UNKNOWN"),
               "unverified_inputs": raw.get("unverified_inputs", ""),
               "scenarios": {}}
        for label, r in scenarios:
            out["scenarios"][label] = {
                "contribution": round(r["contribution"], 2),
                "margin_pct": round(r["margin_pct"], 1),
                "be_cac": round(r["be_cac"], 2),
                "be_roas": None if r["be_roas"] is None else round(r["be_roas"], 2),
                "band": band(r),
                "net_price": round(r["net_price"], 2),
                "landed": round(r["landed"], 2),
                "postage": round(r["postage"], 2),
                "billable_kg": round(r["billable_kg"], 2),
                "upfront_cash": round(r["upfront_cash"], 2),
                "profit_at_cac": {str(int(c)): round(r["contribution"] - c, 2)
                                  for c in (15, 25, 40, 60)},
            }
        print(json.dumps(out, indent=2))
        return 0

    report(name, scenarios)
    if args.sensitivity:
        sensitivity(inputs, args.threshold)

    unverified = raw.get("unverified_inputs")
    if unverified:
        print("UNVERIFIED INPUTS declared in the spec:")
        print("  {}".format(unverified))
        print("  Every figure above inherits that uncertainty.")
        print()

    b_base, b_down = band(scenarios[0][1]), band(scenarios[1][1])
    print("READ: base band {}, downside band {}.".format(b_base, b_down))
    if b_base == "A" and b_down in ("A", "B"):
        print("  Clears the preferred threshold and survives the downside. Strongest result available here.")
    elif b_base == "A":
        print("  Clears the preferred threshold in base only. The business depends on nothing going wrong.")
    elif b_base == "B":
        print("  Conditional candidate. Below the preferred threshold, above the conditional floor.")
        print("  This is NOT 'roughly breaking even' - see the acquisition-cost table for the actual")
        print("  profit or loss per order, which depends entirely on a CAC nobody has measured.")
    else:
        print("  Fails both thresholds in the base case. Do not proceed on these numbers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
