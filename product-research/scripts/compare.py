#!/usr/bin/env python3
"""Rank every product spec in products/ into band A, band B and rejected.

    python3 scripts/compare.py                 # markdown tables to stdout
    python3 scripts/compare.py --dir products  # alternate directory

Produces exactly what a go/no-go decision needs and nothing it does not:
contribution dollars before advertising, break-even CAC, profit or loss across
labelled acquisition-cost scenarios, upfront cash, MOQ, evidence quality, and
the specific things that must be verified before spending.

No repeat purchase is credited anywhere. Every figure is a first order.
"""
import argparse, glob, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_econ as ue

CAC_POINTS = (15.0, 25.0, 40.0, 60.0)
BAND_ORDER = {"A": 0, "B": 1, "NEITHER": 2}


def load_all(directory):
    out = []
    for path in sorted(glob.glob(os.path.join(directory, "*.yaml"))):
        if os.path.basename(path).startswith("_"):
            continue
        try:
            raw, inputs = ue.load(path)
        except SystemExit as exc:
            out.append({"error": str(exc), "path": path,
                        "name": os.path.basename(path)})
            continue
        base = ue.compute(inputs)
        down = ue.compute(ue.apply_scenario(inputs, ue.DOWNSIDE))
        sev = ue.compute(ue.apply_scenario(inputs, ue.SEVERE))
        out.append({
            "path": path, "raw": raw, "inputs": inputs,
            "name": raw.get("name", os.path.basename(path)),
            "base": base, "down": down, "sev": sev,
            "band": ue.band(base), "band_down": ue.band(down),
        })
    return out


def fmt(x):
    return "${:,.2f}".format(x)


def signed(x):
    return ("+" if x >= 0 else "−") + "${:,.2f}".format(abs(x))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "products"))
    args = ap.parse_args(argv)

    rows = load_all(args.dir)
    broken = [r for r in rows if "error" in r]
    rows = [r for r in rows if "error" not in r]
    if not rows:
        print("No product specs found in {}.".format(os.path.abspath(args.dir)))
        print("Nothing to rank. This is a real result, not an empty file.")
        for b in broken:
            print("  BROKEN SPEC {}: {}".format(b["name"], b["error"]))
        return 0

    rows.sort(key=lambda r: (BAND_ORDER[r["band"]], -r["base"]["contribution"]))

    print("# Ranked shortlist\n")
    print("Contribution is **before advertising** everywhere below. Advertising is paid out of it,")
    print("which is why contribution and break-even customer acquisition cost are the same number.")
    print("No repeat purchase is credited in any figure. Every line is one first order.\n")

    for band_key, title, blurb in (
        ("A", "Band A — preferred", "Contribution at or above 45% of net revenue and at or above $20 an order."),
        ("B", "Band B — conditional", "Contribution between 35% and 44.9% of net revenue, at or above $20 an order. Investigated because the stricter screen excludes them; not an endorsement."),
        ("NEITHER", "Below both thresholds", "Shown so the failing assumption is visible rather than hidden."),
    ):
        group = [r for r in rows if r["band"] == band_key]
        print("## {}\n".format(title))
        print("{}\n".format(blurb))
        if not group:
            print("**Nothing in this band.**\n")
            continue

        print("| Product | Net price | Contribution | % of net | Break-even CAC | Break-even ROAS | Downside band |")
        print("|---|---:|---:|---:|---:|---:|---|")
        for r in group:
            b = r["base"]
            print("| {} | {} | **{}** | **{:.1f}%** | {} | {} | {} |".format(
                r["name"], fmt(b["net_price"]), fmt(b["contribution"]), b["margin_pct"],
                fmt(b["be_cac"]),
                "n/a" if b["be_roas"] is None else "{:.2f}".format(b["be_roas"]),
                r["band_down"]))
        print()

        print("### Profit or loss per order, by acquisition cost\n")
        print("Every acquisition cost below is an **assumption**. None has been measured for any of these products.\n")
        header = "| Product |" + "".join(" CAC ${:.0f} |".format(c) for c in CAC_POINTS) + " CAC at break-even |"
        print(header)
        print("|---|" + "---:|" * (len(CAC_POINTS) + 1))
        for r in group:
            b = r["base"]
            cells = "".join(" {} |".format(signed(b["contribution"] - c)) for c in CAC_POINTS)
            print("| {} |{} {} |".format(r["name"], cells, fmt(b["be_cac"])))
        print()
        print("Same table under the downside scenario, which is where a first-time importer actually lands:\n")
        print(header)
        print("|---|" + "---:|" * (len(CAC_POINTS) + 1))
        for r in group:
            d = r["down"]
            cells = "".join(" {} |".format(signed(d["contribution"] - c)) for c in CAC_POINTS)
            print("| {} |{} {} |".format(r["name"], cells,
                                         fmt(d["be_cac"]) if d["contribution"] > 0 else "never"))
        print()

        print("### Cash, quantity and evidence\n")
        print("| Product | Upfront cash | Units | MOQ | Cash per unit | Orders to recover | Evidence quality |")
        print("|---|---:|---:|---:|---:|---:|---|")
        for r in group:
            b = r["base"]
            units = b["units"]
            recover = ("{:,.0f}".format(-(-b["upfront_cash"] // b["contribution"]))
                       if b["contribution"] > 0 else "never")
            print("| {} | {} | {:,.0f} | {:,.0f} | {} | {} of {:,.0f} | {} |".format(
                r["name"], fmt(b["upfront_cash"]), units,
                r["inputs"].get("moq_units", units),
                fmt(b["upfront_cash"] / units), recover, units,
                r["raw"].get("evidence_quality", "UNKNOWN")))
        print()

        print("### What must be verified before spending\n")
        for r in group:
            print("**{}**".format(r["name"]))
            mv = r["raw"].get("must_verify")
            if mv:
                for item in str(mv).split(";"):
                    if item.strip():
                        print("- {}".format(item.strip()))
            else:
                print("- NOT STATED in the spec. Treat every input as unverified.")
            un = r["raw"].get("unverified_inputs")
            if un:
                print("- Declared unverified: {}".format(un))
            print()

    if broken:
        print("## Specs that would not load\n")
        for b in broken:
            print("- `{}`: {}".format(os.path.basename(b["path"]), b["error"]))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
