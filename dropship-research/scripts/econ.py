#!/usr/bin/env python3
"""Deterministic unit economics for one product.

Usage:
    python3 scripts/econ.py data/products/P-0007/econ-inputs.yaml [-o out.md] [--print]

Reads the three scenarios written by the economics agent, fills any missing key
from config/fees.yaml, and writes economics-calc.md next to the input file.
Stdlib only: the YAML subset used by these files is parsed here directly.

Definitions (see .claude/skills/unit-economics-risk/SKILL.md):
    contribution = price_after_discount - goods - duty - packaging - payment_fee
                   - refund_loss - chargeback_loss
    break-even CAC  = contribution
    break-even ROAS = price_after_discount / contribution
"""

import argparse
import math
import os
import sys

FEES_DEFAULTS = "config/fees.yaml"

INPUT_KEYS = (
    "price_usd",
    "product_cost_usd",
    "shipping_cost_usd",
    "duty_rate_pct",
    "discount_rate_pct",
    "refund_rate_pct",
    "chargeback_rate_pct",
    "chargeback_fee_usd",
    "packaging_usd",
    "payment_fee_pct",
    "payment_fee_fixed_usd",
)

SCENARIOS = ("pessimistic", "base", "optimistic")


def _scalar(raw):
    """Convert a YAML scalar to float/bool/str."""
    text = raw.strip().strip('"').strip("'")
    if text == "":
        return ""
    try:
        return float(text) if ("." in text or "e" in text.lower()) else int(text)
    except ValueError:
        return text


def _inline_map(text):
    """Parse {a: 1, b: 2} -> dict. Values here are always scalars."""
    out = {}
    body = text.strip()[1:-1]
    for part in body.split(","):
        if ":" not in part:
            continue
        key, _, value = part.partition(":")
        out[key.strip()] = _scalar(value)
    return out


def load_yaml_subset(path):
    """Parse the flat/one-level-nested YAML these files use.

    Supports: `key: scalar`, `key:` followed by indented `key: scalar` or
    `key: {inline map}` lines, and `# comments`. Anything else is ignored.
    """
    data = {}
    current = None
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.split(" #")[0].rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indented = line[0] in " \t"
            stripped = line.strip()
            if ":" not in stripped:
                continue
            key, _, value = stripped.partition(":")
            key, value = key.strip(), value.strip()
            if not indented:
                if value == "":
                    current = {}
                    data[key] = current
                else:
                    data[key] = _inline_map(value) if value.startswith("{") else _scalar(value)
                    current = None
            elif current is not None:
                current[key] = _inline_map(value) if value.startswith("{") else _scalar(value)
    return data


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_defaults():
    path = os.path.join(repo_root(), FEES_DEFAULTS)
    if not os.path.exists(path):
        return {}
    return {k: v for k, v in load_yaml_subset(path).items() if isinstance(v, (int, float))}


def compute(values):
    """Return the economics for one scenario. Pure arithmetic, no I/O."""
    price = float(values["price_usd"])
    discount = price * float(values["discount_rate_pct"]) / 100.0
    net_price = price - discount

    product = float(values["product_cost_usd"])
    shipping = float(values["shipping_cost_usd"])
    duty = product * float(values["duty_rate_pct"]) / 100.0
    packaging = float(values["packaging_usd"])
    goods = product + shipping + duty + packaging

    payment_fee = net_price * float(values["payment_fee_pct"]) / 100.0 + float(
        values["payment_fee_fixed_usd"]
    )
    refund_loss = float(values["refund_rate_pct"]) / 100.0 * (net_price + goods)
    chargeback_loss = (
        float(values["chargeback_rate_pct"])
        / 100.0
        * (net_price + goods + float(values["chargeback_fee_usd"]))
    )

    contribution = net_price - goods - payment_fee - refund_loss - chargeback_loss
    margin_pct = contribution / net_price * 100.0 if net_price else 0.0

    return {
        "price": price,
        "discount": discount,
        "net_price": net_price,
        "goods": goods,
        "duty": duty,
        "payment_fee": payment_fee,
        "refund_loss": refund_loss,
        "chargeback_loss": chargeback_loss,
        "contribution": contribution,
        "margin_pct": margin_pct,
        "be_cac": contribution,
        "be_roas": (net_price / contribution) if contribution > 0 else None,
        "orders_to_recover_test": (
            math.ceil(100.0 / contribution) if contribution > 0 else None
        ),
    }


def money(value):
    return "n/a" if value is None else "{:.2f}".format(value)


def ratio(value):
    return "n/a (contribution <= 0)" if value is None else "{:.2f}".format(value)


def render(product_id, inputs, results, labels, missing, sensitivities, gates):
    lines = []
    add = lines.append
    add("<!-- Generated by scripts/econ.py. Do not edit by hand; edit econ-inputs.yaml and re-run. -->")
    add("# {} — unit economics (calculated)".format(product_id))
    add("")
    add("Source: `econ-inputs.yaml`. Defaults for any omitted input come from `config/fees.yaml`.")
    add("")
    add("## Inputs used")
    add("")
    add("| Input | Pessimistic | Base | Optimistic | Label / source |")
    add("|---|---|---|---|---|")
    for key in INPUT_KEYS:
        row = [key]
        for scenario in SCENARIOS:
            row.append("{:.2f}".format(float(inputs[scenario][key])))
        label = labels.get(key, "ASSUMPTION — config/fees.yaml" if key in missing else "")
        row.append(str(label))
        add("| " + " | ".join(row) + " |")
    add("")
    if missing:
        add("Inputs defaulted from `config/fees.yaml` (not supplied per product): "
            + ", ".join("`{}`".format(k) for k in sorted(missing)) + ".")
        add("")
    add("## Results")
    add("")
    add("| Metric | Pessimistic | Base | Optimistic |")
    add("|---|---|---|---|")
    rows = [
        ("Net price after discount (USD)", lambda r: money(r["net_price"])),
        ("Goods landed + packaging (USD)", lambda r: money(r["goods"])),
        ("Payment fee (USD)", lambda r: money(r["payment_fee"])),
        ("Expected refund loss (USD)", lambda r: money(r["refund_loss"])),
        ("Expected chargeback loss (USD)", lambda r: money(r["chargeback_loss"])),
        ("**Contribution per order (USD)**", lambda r: money(r["contribution"])),
        ("**Contribution margin (%)**", lambda r: "{:.1f}".format(r["margin_pct"])),
        ("Break-even CAC (USD)", lambda r: money(r["be_cac"])),
        ("Break-even ROAS", lambda r: ratio(r["be_roas"])),
        ("Orders to recover a 100 USD test",
         lambda r: "n/a" if r["orders_to_recover_test"] is None else str(r["orders_to_recover_test"])),
    ]
    for title, fn in rows:
        add("| " + title + " | " + " | ".join(fn(results[s]) for s in SCENARIOS) + " |")
    add("")
    add("## Sensitivity (base case)")
    add("")
    add("| Change | Contribution (USD) | Margin (%) |")
    add("|---|---|---|")
    for title, result in sensitivities:
        add("| {} | {} | {:.1f} |".format(title, money(result["contribution"]), result["margin_pct"]))
    add("")
    add("## Gate G4 check")
    add("")
    for line in gates:
        add("- " + line)
    add("")
    add("Break-even CAC is what one order can pay to acquire a customer. Break-even ROAS is the "
        "return on ad spend below which paid traffic loses money. Organic CAC is assumed to be "
        "0 USD, so these figures exist as thresholds for a later paid test, not as a plan to run ads.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compute scenario unit economics for one product.")
    parser.add_argument("inputs", help="path to econ-inputs.yaml")
    parser.add_argument("-o", "--out", help="output path (default: economics-calc.md beside the input)")
    parser.add_argument("--print", dest="to_stdout", action="store_true", help="also print the report")
    args = parser.parse_args(argv)

    if not os.path.exists(args.inputs):
        parser.error("no such file: {}".format(args.inputs))

    doc = load_yaml_subset(args.inputs)
    product_id = doc.get("product_id", "P-????")
    scenarios = doc.get("scenarios") or {}
    labels = doc.get("labels") or {}
    defaults = load_defaults()

    inputs, missing = {}, set()
    for scenario in SCENARIOS:
        supplied = scenarios.get(scenario)
        if not isinstance(supplied, dict):
            parser.error("scenario '{}' missing from {}".format(scenario, args.inputs))
        values = {}
        for key in INPUT_KEYS:
            if key in supplied:
                values[key] = supplied[key]
            elif key in defaults:
                values[key] = defaults[key]
                missing.add(key)
            else:
                parser.error(
                    "input '{}' missing for scenario '{}' and absent from config/fees.yaml".format(
                        key, scenario
                    )
                )
        inputs[scenario] = values

    results = {s: compute(inputs[s]) for s in SCENARIOS}

    shipped_up = dict(inputs["base"])
    shipped_up["shipping_cost_usd"] = float(shipped_up["shipping_cost_usd"]) + 3.0
    price_down = dict(inputs["base"])
    price_down["price_usd"] = float(price_down["price_usd"]) - 5.0
    sensitivities = [
        ("Base", results["base"]),
        ("Shipping +3.00 USD", compute(shipped_up)),
        ("Price -5.00 USD", compute(price_down)),
    ]

    base, pess = results["base"], results["pessimistic"]
    checks = [
        ("base contribution >= 12.00 USD", base["contribution"] >= 12.0,
         "{} USD".format(money(base["contribution"]))),
        ("base margin >= 35%", base["margin_pct"] >= 35.0,
         "{:.1f}%".format(base["margin_pct"])),
        ("pessimistic contribution > 0", pess["contribution"] > 0,
         "{} USD".format(money(pess["contribution"]))),
    ]
    gates = ["{} — {} ({})".format("PASS" if ok else "FAIL", rule, value)
             for rule, ok, value in checks]
    gates.append(
        "**G4 {}** (thresholds from `config/rubric.yaml`; the Lead makes the final call).".format(
            "PASS" if all(ok for _, ok, _ in checks) else "FAIL"
        )
    )

    report = render(product_id, inputs, results, labels, missing, sensitivities, gates)
    out_path = args.out or os.path.join(os.path.dirname(os.path.abspath(args.inputs)),
                                        "economics-calc.md")
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    if args.to_stdout:
        sys.stdout.write(report)
    print("wrote {}".format(out_path), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
