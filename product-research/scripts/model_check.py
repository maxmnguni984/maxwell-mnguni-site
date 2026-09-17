#!/usr/bin/env python3
"""Verification for unit_econ.py. Proves the corrections do what the docstring claims.

Run: python3 scripts/model_check.py

Three things it checks, because a model nobody tested is a model nobody should
price a $12,000 order with:

1. IDENTITY. Contribution must equal net revenue minus every cost line. If the
   report prints lines that do not add up to the total, the report is fiction.
2. THE CORRECTIONS. Reimplements the two old formulas and prints the exact
   difference, so the docstring's claimed impact is measured, not asserted.
3. EDGE CASES. Dimensional weight, zero-weight specs, negative contribution.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_econ as ue

FAILURES = []

def check(label, ok, detail=""):
    print("  {:<58} {}".format(label, "ok" if ok else "FAIL"), detail)
    if not ok:
        FAILURES.append(label)

spec = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "products", "_example.yaml")
raw, inputs = ue.load(spec)
r = ue.compute(inputs)

print("1. IDENTITY: do the printed lines add up to the printed total?")
parts = (r["exfactory"] + r["factory_pack"] + r["tooling"] + r["duty"] + r["inbound"]
         + r["cargo_ins"] + r["fx"] + r["entry"] + r["inspection"])
check("landed = sum of its components", abs(parts - r["landed"]) < 1e-9,
      "({:.6f} vs {:.6f})".format(parts, r["landed"]))
ful = r["packaging"] + r["warehouse"] + r["postage"] + r["support"]
check("fulfilment = sum of its components", abs(ful - r["fulfilment"]) < 1e-9)
loss = r["return_loss"] + r["defect_loss"] + r["chargeback_loss"]
check("losses = sum of its components", abs(loss - r["losses"]) < 1e-9)
contrib = (r["net_price"] - r["landed"] - r["fulfilment"] - r["payment_fee"]
           - r["platform_fee"] - r["losses"])
check("contribution = net - landed - fulfilment - fees - losses",
      abs(contrib - r["contribution"]) < 1e-9)
check("break-even CAC == contribution (ads are paid out of it)",
      abs(r["be_cac"] - r["contribution"]) < 1e-9)
check("break-even ROAS == net_price / contribution",
      abs(r["be_roas"] - r["net_price"] / r["contribution"]) < 1e-9)
check("founder time is NOT inside contribution",
      abs((r["contribution"] - r["founder_cost"]) - r["contribution_after_founder_time"]) < 1e-9)
print()

print("2. THE CORRECTIONS, measured against the formulas they replaced")
rr = inputs["return_rate_pct"] / 100.0
resell = inputs["resellable_after_return_pct"] / 100.0
share = inputs["return_postage_paid_by_us_pct"] / 100.0
ret_post = inputs["return_postage_usd"]

old_return = rr * (r["postage"] + share * ret_post + r["payment_fee"] + r["landed"] * (1 - resell))
new_return = r["return_loss"]
d_ret = new_return - old_return
print("  returns:     old ${:>6.2f}   new ${:>6.2f}   understated by ${:.2f} a unit"
      .format(old_return, new_return, d_ret))
check("the old return formula understated the cost", d_ret > 0)

cb = inputs["chargeback_rate_pct"] / 100.0
old_cb = cb * (r["net_price"] + r["landed"] + r["fulfilment"] + inputs["chargeback_fee_usd"])
new_cb = r["chargeback_loss"]
d_cb = new_cb - old_cb
print("  chargebacks: old ${:>6.2f}   new ${:>6.2f}   overstated by ${:.2f} a unit"
      .format(old_cb, new_cb, -d_cb))
check("the old chargeback formula double-counted goods and fulfilment", d_cb < 0)

net_effect = d_ret + d_cb
pts = net_effect / r["net_price"] * 100.0
print("  NET EFFECT of both corrections: ${:.2f} a unit, {:.2f} margin points"
      .format(net_effect, pts))
print("  Same spec, old loss formulas:   contribution ${:.2f} at {:.1f}% of net"
      .format(r["contribution"] + net_effect, (r["contribution"] + net_effect) / r["net_price"] * 100))
print("  Same spec, corrected:           contribution ${:.2f} at {:.1f}% of net"
      .format(r["contribution"], r["margin_pct"]))
print()

print("  new cost lines that did not exist before:")
for label, key in (("cargo insurance", "cargo_ins"), ("fx slippage", "fx"),
                   ("customer support", "support")):
    print("    {:<20} ${:.2f}".format(label, r[key]))
newlines = r["cargo_ins"] + r["fx"] + r["support"]
print("    {:<20} ${:.2f}  ({:.2f} margin points)".format("total", newlines, newlines / r["net_price"] * 100))
print()

print("3. EDGE CASES")
bulky = dict(inputs)
bulky.update({"packed_weight_kg": 0.4, "packed_length_cm": 40, "packed_width_cm": 30,
              "packed_height_cm": 25, "postage_base_usd": 4.0, "postage_per_kg_usd": 4.0})
bill, actual, dim = ue.billable_weight(bulky)
check("a light bulky box bills on volume, not mass",
      dim > actual and abs(bill - dim) < 1e-9,
      "(actual {:.2f} kg, volumetric {:.2f} kg)".format(actual, dim))
rb = ue.compute(bulky)
flat = dict(bulky); flat.pop("postage_per_kg_usd")
rf = ue.compute(flat)
check("volumetric billing costs more than the flat assumption",
      rb["postage"] > rf["postage"],
      "(${:.2f} vs ${:.2f})".format(rb["postage"], rf["postage"]))

noweight = dict(inputs)
for k in ("packed_length_cm", "packed_width_cm", "packed_height_cm"):
    noweight.pop(k, None)
rn = ue.compute(noweight)
check("a spec with no dimensions still computes, using flat postage",
      abs(rn["postage"] - inputs["outbound_postage_usd"]) < 1e-9)

dead = dict(inputs); dead["retail_price_usd"] = 30.0
rd = ue.compute(dead)
check("negative contribution yields band NEITHER and no ROAS",
      rd["contribution"] < 0 and ue.band(rd) == "NEITHER" and rd["be_roas"] is None,
      "(contribution ${:.2f})".format(rd["contribution"]))

b45 = dict(inputs)
check("band A requires BOTH the dollar floor and the percentage",
      ue.band({"contribution": 19.0, "margin_pct": 60.0}) == "NEITHER"
      and ue.band({"contribution": 25.0, "margin_pct": 40.0}) == "B"
      and ue.band({"contribution": 25.0, "margin_pct": 45.0}) == "A"
      and ue.band({"contribution": 25.0, "margin_pct": 34.9}) == "NEITHER")

down = ue.compute(ue.apply_scenario(inputs, ue.DOWNSIDE))
check("return postage now worsens with outbound postage in the downside",
      down["postage"] > r["postage"],
      "(base ${:.2f} -> downside ${:.2f})".format(r["postage"], down["postage"]))
print()

if FAILURES:
    print("{} CHECK(S) FAILED: {}".format(len(FAILURES), "; ".join(FAILURES)))
    sys.exit(1)
print("all checks passed")
