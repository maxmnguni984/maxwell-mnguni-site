#!/usr/bin/env python3
"""Screen discovery candidates against the entry filters, then rank survivors.

Standard library only. Imports cost_ceiling for the economics.

WHY THIS EXISTS
---------------
Round one's shortlist was ranked by hand in an ad-hoc shell script. That worked
once, but the filters that actually mattered were only discovered after the
fact, and applying them by eye means they drift between rounds.

This encodes them. A candidate either clears the bar or it does not, the reason
is printed, and the same code runs next time.

THE FILTERS, and why each exists
--------------------------------
F1 PRICE FLOOR      Observed retail midpoint at or above the floor. Maximum
                    landed cost is roughly 39% of price once paid acquisition
                    is funded, so a cheap product leaves nothing to buy goods
                    with. Four of round one's thirteen died here.
F2 WEIGHT           Under the weight cap. Landed cost includes freight.
F3 PACKS FLAT       Rigid unfoldable items carry a dimensional-weight penalty
                    the arithmetic does not show. A 15 lb blanket and a rigid
                    drying rack both died on this.
F4 DEMO VALUE       At or above the demo floor. Paid ads from day one mean a
                    benefit that cannot be shown in five silent seconds is the
                    wrong bet.
F5 EXCLUDED CATEGORY  From the brief's exclusion list.
F6 DUPLICATE        Already covered in a previous round.
F7 PRICE EVIDENCE   The price must be FACT-grade: read from a named listing
                    with a URL and a date. Everything downstream, the landed
                    cost ceiling and the break-even CPA, is computed from
                    price. Ranking an assumption-grade price as though it were
                    measured is how a store gets built on a number nobody
                    checked. Round two surfaced exactly this: a candidate whose
                    price basis said ASSUMPTION outscored every rival.
F8 INJURY RECALL    The product TYPE has a recall citing injuries or a repeated
                    incident pattern. Round one rejected resistance bands on
                    exactly this (five recalls since 2011 for anchors detaching
                    and striking users). Round two then surfaced an expandable
                    garden hose with 222 burst reports and 29 injuries, which
                    only escaped because its price was out of band. A safety
                    record is not something a score should be able to outweigh,
                    so it is a filter and not a scoring input.

A candidate failing any filter is rejected with that filter named. Survivors
are then scored, and the score never overrides a filter.

Usage:
    python3 screen.py research/runs/<run>/discovery/candidates-A.jsonl [more...]
    python3 screen.py <files> --json
    python3 screen.py <files> --exclude research/runs/<run>/exclude-dedupe-keys.txt
    python3 screen.py --self-test
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost_ceiling  # noqa: E402

DEFAULTS = {
    "price_floor": 30.00,
    "price_ceiling": 60.00,
    "weight_cap_kg": 1.0,
    "demo_floor": 4,
    "target_roas": 2.5,
}

# Scoring weights. Only applied to candidates that clear every filter.
WEIGHTS = {
    "ceiling_headroom": 30,   # how much room a supplier has to hit
    "demo_value": 25,         # paid-ads creative potential
    "complaint_specificity": 20,  # is there a real, quotable failure to fix
    "shipping_profile": 15,   # light and flat beats heavy and rigid
    "risk_cleanliness": 10,   # no recall history, no obvious IP trap
}


def _num(x):
    return x if isinstance(x, (int, float)) else None


def price_mid(c):
    p = c.get("observed_price_range") or {}
    lo, hi = _num(p.get("low")), _num(p.get("high"))
    if lo is not None and hi is not None:
        return (lo + hi) / 2.0
    return lo if lo is not None else None


def price_is_assumption(c):
    """True when the candidate's own price basis admits it is not measured."""
    p = c.get("observed_price_range") or {}
    for field in (p.get("basis"), p.get("grade"), c.get("price_basis"),
                  c.get("price_evidence_grade")):
        if isinstance(field, str) and "assumption" in field.lower():
            return True
    return bool(c.get("flags") and "PRICE_IS_ASSUMPTION" in c["flags"])


INJURY_MARKERS = ("injur", "laceration", "burst", "fatalit", "death",
                  "hospital", "amputat", "strangulat", "asphyxiat", "choking")


def recall_text(c):
    for key in ("cpsc_recall_history", "recall_history", "safety_history"):
        v = c.get(key)
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            return " ".join(str(x) for x in v.values())
    return ""


def injury_recall(c):
    """True when the recall record describes harm, not merely a recall search."""
    t = recall_text(c).lower()
    if not t or "unknown" in t or "no recall" in t or "none found" in t:
        return False
    if "recall" not in t and "incident" not in t:
        return False
    return any(m in t for m in INJURY_MARKERS)


def price_single_source(c):
    p = c.get("observed_price_range") or {}
    if isinstance(c.get("flags"), list) and "PRICE_SINGLE_SOURCE" in c["flags"]:
        return True
    basis = str(p.get("basis", "")).lower()
    if "single confirmed price" in basis or "single source" in basis:
        return True
    lo, hi = _num(p.get("low")), _num(p.get("high"))
    return lo is not None and hi is not None and lo == hi


def demo_value(c):
    d = c.get("demonstration_value")
    if isinstance(d, dict):
        for k in ("score", "value", "rating"):
            if isinstance(d.get(k), (int, float)):
                return d[k]
        return None
    return d if isinstance(d, (int, float)) else None


def _parse_weight(text):
    """Pull a kilogram figure out of free text. Returns None when there isn't one."""
    import re as _re
    t = str(text).lower().replace("~", " ").replace("approx", " ")
    m = _re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilogram|lb|lbs|pound|oz|ounce|g\b|gram)", t)
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2)
    if unit.startswith("kg") or unit.startswith("kilo"):
        return val
    if unit.startswith("lb") or unit.startswith("pound"):
        return val * 0.45359237
    if unit.startswith("oz") or unit.startswith("ounce"):
        return val * 0.0283495
    return val / 1000.0          # grams


def weight_kg(c):
    """Best available weight in kg, or None.

    Agents have used several shapes for this: a bare number, a dict with a
    numeric value, and a dict whose `estimate` is free text such as
    "under 1 kg" or "0.6 lb". Round two's candidates all used the last form,
    which an earlier version of this parser silently ignored, leaving the
    weight filter inert on every candidate. Hence the breadth here.
    """
    for key in ("estimated_weight_kg", "weight_kg", "estimated_weight",
                "weight_and_pack_form", "weight"):
        v = c.get(key)
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            got = _parse_weight(v)
            if got is not None:
                return got
        if isinstance(v, dict):
            for k in ("kg", "value"):
                if isinstance(v.get(k), (int, float)):
                    return float(v[k])
            for k in ("estimate", "value", "weight", "method"):
                if isinstance(v.get(k), str):
                    got = _parse_weight(v[k])
                    if got is not None:
                        return got
    return None


UNCERTAIN_MARKERS = ("uncertain", "borderline", "unconfirmed", "not confirmed",
                     "unknown", "possibly over", "flagged")


def weight_uncertain(c):
    """True when the record itself says the weight is not settled.

    An unconfirmed weight is not the same as a light product. Freight is the
    input most likely to break the landed-cost ceiling, so an admitted unknown
    is carried into the score rather than passing silently.
    """
    if isinstance(c.get("flags"), list) and "WEIGHT_UNCERTAIN" in c["flags"]:
        return True
    v = c.get("weight_and_pack_form")
    if isinstance(v, dict):
        blob = " ".join(str(x) for x in v.values()).lower()
    else:
        blob = str(v or "").lower()
    if not blob:
        return True                     # nothing recorded at all
    if weight_kg(c) is not None and not any(m in blob for m in UNCERTAIN_MARKERS):
        return False
    return any(m in blob for m in UNCERTAIN_MARKERS) or weight_kg(c) is None


def packs_flat(c):
    for key in ("packs_flat", "compressible", "folds_flat"):
        if isinstance(c.get(key), bool):
            return c[key]
    v = c.get("weight_and_pack_form")
    nested = " ".join(str(x) for x in v.values()) if isinstance(v, dict) else str(v or "")
    form = (str(c.get("packed_form", "") or c.get("form_factor", "")) + " " + nested).lower()
    if not form:
        return None
    if any(w in form for w in ("rigid", "does not fold", "non-folding", "bulky")):
        return False
    if any(w in form for w in ("flat", "fold", "compress", "soft", "roll")):
        return True
    return None


def screen(candidates, cfg=None, excluded_keys=None):
    cfg = dict(DEFAULTS, **(cfg or {}))
    excluded_keys = set(excluded_keys or [])
    passed, rejected = [], []
    seen = set()

    for c in candidates:
        name = c.get("name", "(unnamed)")
        key = c.get("dedupe_key")
        fails = []

        if key and key in excluded_keys:
            fails.append(("F6", "already covered in a previous round"))
        if key and key in seen:
            fails.append(("F6", "duplicate within this sweep"))
        if key:
            seen.add(key)

        mid = price_mid(c)
        if mid is None:
            fails.append(("F1", "no observed price, so the price band cannot be checked"))
        elif mid < cfg["price_floor"]:
            fails.append(("F1", "observed midpoint $%.2f is below the $%.2f floor"
                          % (mid, cfg["price_floor"])))
        elif mid > cfg["price_ceiling"]:
            fails.append(("F1", "observed midpoint $%.2f is above the $%.2f ceiling"
                          % (mid, cfg["price_ceiling"])))

        w = weight_kg(c)
        if w is not None and w > cfg["weight_cap_kg"]:
            fails.append(("F2", "estimated %.2f kg exceeds the %.2f kg cap; freight "
                          "eats the landed-cost ceiling" % (w, cfg["weight_cap_kg"])))

        flat = packs_flat(c)
        if flat is False:
            fails.append(("F3", "rigid and does not pack flat; dimensional weight "
                          "attacks the ceiling invisibly"))

        d = demo_value(c)
        if d is None:
            fails.append(("F4", "no demonstration value recorded"))
        elif d < cfg["demo_floor"]:
            fails.append(("F4", "demonstration value %s is below the floor of %s; "
                          "paid ads run from day one" % (d, cfg["demo_floor"])))

        if c.get("excluded_category"):
            fails.append(("F5", str(c["excluded_category"])))

        if injury_recall(c):
            fails.append(("F8", "the product type has a recall record citing injury: %s"
                          % recall_text(c)[:150]))

        if mid is not None and price_is_assumption(c):
            fails.append(("F7", "price is assumption-grade, not read from a named "
                          "listing; the landed-cost ceiling and break-even CPA are "
                          "both computed from it"))

        if fails:
            rejected.append({"name": name, "dedupe_key": key,
                             "failed": [{"filter": f, "reason": r} for f, r in fails]})
        else:
            passed.append(c)

    scored = [score(c, cfg) for c in passed]
    scored.sort(key=lambda s: -s["score"])
    return {"passed": scored, "rejected": rejected, "config": cfg}


def score(c, cfg):
    mid = price_mid(c)
    ceil = cost_ceiling.ceiling(mid, cfg["target_roas"])["max_landed_cost"]

    # Headroom: a higher absolute ceiling gives a supplier more room to hit.
    # $20 or more is full marks, $6 or less is zero.
    head = max(0.0, min(1.0, (ceil - 6.0) / 14.0))

    d = demo_value(c) or 0
    demo = max(0.0, min(1.0, (d - 3.0) / 2.0))   # 3 -> 0, 5 -> 1

    complaints = c.get("complaints") or c.get("complaint_language") or []
    if isinstance(complaints, str):
        complaints = [complaints]
    spec = max(0.0, min(1.0, len(complaints) / 3.0))

    w = weight_kg(c)
    ship = 0.5 if w is None else max(0.0, min(1.0, (1.0 - w) / 0.8))
    if packs_flat(c) is False:
        ship *= 0.3
    if weight_uncertain(c):
        ship *= 0.6

    recall = str(c.get("cpsc_recall_history", "")).lower()
    if "unknown" in recall or not recall:
        risk = 0.5      # unchecked is not the same as clean
    elif "no recall" in recall or "none" in recall:
        risk = 1.0
    else:
        risk = 0.0

    parts = {
        "ceiling_headroom": head,
        "demo_value": demo,
        "complaint_specificity": spec,
        "shipping_profile": ship,
        "risk_cleanliness": risk,
    }
    total = sum(parts[k] * WEIGHTS[k] for k in WEIGHTS)

    # One confirmed listing is real evidence but thin. A candidate should not
    # top the ranking on a single data point, so the score is discounted and
    # the reason is carried in the output rather than left implicit.
    thin = price_single_source(c)
    if thin:
        total *= 0.85

    return {
        "name": c.get("name"),
        "dedupe_key": c.get("dedupe_key"),
        "price_mid": round(mid, 2),
        "max_landed_cost": ceil,
        "demo_value": d,
        "weight_kg": w,
        "score": round(total, 1),
        "price_single_source": thin,
        "weight_uncertain": weight_uncertain(c),
        "components": {k: round(v, 3) for k, v in parts.items()},
        "candidate": c,
    }


def render(result):
    out = []
    cfg = result["config"]
    out.append("Filters: price $%.2f-$%.2f, weight under %.1f kg, demo at least %d, ROAS %.1f"
               % (cfg["price_floor"], cfg["price_ceiling"], cfg["weight_cap_kg"],
                  cfg["demo_floor"], cfg["target_roas"]))
    out.append("")
    out.append("PASSED (%d)" % len(result["passed"]))
    if result["passed"]:
        out.append("%-5s %-40s %-9s %-9s %-5s %s" %
                   ("score", "product", "price", "ceiling", "demo", "kg"))
        out.append("-" * 88)
        for s in result["passed"]:
            out.append("%-5.1f %-40s $%-8.2f $%-8.2f %-5s %s" %
                       (s["score"], (s["name"] or "")[:40], s["price_mid"],
                        s["max_landed_cost"], s["demo_value"],
                        "%.2f" % s["weight_kg"] if s["weight_kg"] is not None else "?"))
    else:
        out.append("  none")
    out.append("")
    out.append("REJECTED (%d)" % len(result["rejected"]))
    for r in result["rejected"]:
        reasons = "; ".join("%s %s" % (f["filter"], f["reason"]) for f in r["failed"])
        out.append("  %-40s %s" % ((r["name"] or "")[:40], reasons))
    return "\n".join(out)


def load_jsonl(path):
    """Tolerant loader: accepts true JSONL and pretty-printed concatenated JSON."""
    raw = open(path, encoding="utf-8").read()
    dec = json.JSONDecoder()
    objs, i = [], 0
    while i < len(raw):
        while i < len(raw) and raw[i] in " \n\r\t":
            i += 1
        if i >= len(raw):
            break
        obj, end = dec.raw_decode(raw, i)
        objs.append(obj)
        i = end
    return objs


def self_test():
    import tempfile
    failures = []

    def cand(**kw):
        base = {"name": "X", "dedupe_key": "x", "observed_price_range": {"low": 34, "high": 40},
                "demonstration_value": 4, "estimated_weight_kg": 0.5,
                "packed_form": "folds flat", "complaints": ["a", "b", "c"],
                "cpsc_recall_history": "no recall found"}
        base.update(kw)
        return base

    # A clean candidate passes.
    r = screen([cand()])
    if len(r["passed"]) != 1:
        failures.append("a clean candidate should pass, got %s" % r["rejected"])

    # F1 price floor.
    r = screen([cand(dedupe_key="a", observed_price_range={"low": 15, "high": 20})])
    if not r["rejected"] or r["rejected"][0]["failed"][0]["filter"] != "F1":
        failures.append("a $17.50 candidate should fail F1")

    # F1 upper bound.
    r = screen([cand(dedupe_key="b", observed_price_range={"low": 80, "high": 120})])
    if not any(f["filter"] == "F1" for f in r["rejected"][0]["failed"]):
        failures.append("a $100 candidate should fail F1 on the ceiling")

    # F2 weight.
    r = screen([cand(dedupe_key="c", estimated_weight_kg=6.8)])
    if not any(f["filter"] == "F2" for f in r["rejected"][0]["failed"]):
        failures.append("a 6.8 kg candidate should fail F2")

    # F3 rigid.
    r = screen([cand(dedupe_key="d", packed_form="rigid steel frame, does not fold")])
    if not any(f["filter"] == "F3" for f in r["rejected"][0]["failed"]):
        failures.append("a rigid candidate should fail F3")

    # F4 demo value.
    r = screen([cand(dedupe_key="e", demonstration_value=2)])
    if not any(f["filter"] == "F4" for f in r["rejected"][0]["failed"]):
        failures.append("demo value 2 should fail F4")

    # F6 previously covered.
    r = screen([cand(dedupe_key="seen-before")], excluded_keys=["seen-before"])
    if not any(f["filter"] == "F6" for f in r["rejected"][0]["failed"]):
        failures.append("an excluded dedupe_key should fail F6")

    # F6 duplicate within a sweep.
    r = screen([cand(dedupe_key="dup"), cand(dedupe_key="dup")])
    if len(r["passed"]) != 1 or len(r["rejected"]) != 1:
        failures.append("a duplicate within one sweep should be rejected once")

    # F7 assumption-grade price. This is the case that motivated the filter:
    # such a candidate would otherwise outscore every rival on a number nobody
    # verified.
    r = screen([cand(dedupe_key="assumed",
                     observed_price_range={"low": 28, "high": 80,
                                           "basis": "ASSUMPTION - aggregated answer, no URL"})])
    if not r["rejected"] or not any(f["filter"] == "F7" for f in r["rejected"][0]["failed"]):
        failures.append("an assumption-grade price should fail F7")
    if r["passed"]:
        failures.append("an assumption-grade price must not reach the ranking")

    # And the flag form is caught too.
    r = screen([cand(dedupe_key="flagged", flags=["PRICE_IS_ASSUMPTION"])])
    if not any(f["filter"] == "F7" for f in r["rejected"][0]["failed"]):
        failures.append("a PRICE_IS_ASSUMPTION flag should fail F7")

    # A FACT-grade basis still passes, including a wordy one.
    r = screen([cand(dedupe_key="factual",
                     observed_price_range={"low": 34, "high": 40,
                                           "basis": "FACT (single confirmed price point)"})])
    if not r["passed"]:
        failures.append("a FACT-grade basis should still pass, got %s" % r["rejected"])

    # Weight parsing must handle every shape agents have actually produced.
    for shape, want in (
            ({"estimated_weight_kg": 0.5}, 0.5),
            ({"weight_and_pack_form": {"estimate": "under 1 kg"}}, 1.0),
            ({"weight_and_pack_form": {"estimate": "0.6 lb, packs flat"}}, 0.272),
            ({"weight_and_pack_form": {"estimate": "about 850 g"}}, 0.85),
            ({"weight_and_pack_form": "12 oz"}, 0.340),
            ({"weight_and_pack_form": {"estimate": "no figure available"}}, None)):
        got = weight_kg(shape)
        if want is None:
            if got is not None:
                failures.append("weight %r should not parse, got %s" % (shape, got))
        elif got is None or abs(got - want) > 0.01:
            failures.append("weight %r should parse near %.3f, got %s" % (shape, want, got))

    # The round-two field shape must actually reach F2, since it previously did not.
    r = screen([cand(dedupe_key="heavy", estimated_weight_kg=None,
                     weight_and_pack_form={"estimate": "3.2 kg", "basis": "FACT"})])
    if not r["rejected"] or not any(f["filter"] == "F2" for f in r["rejected"][0]["failed"]):
        failures.append("a 3.2 kg nested weight should fail F2; this shape was silently "
                        "ignored before and left the filter inert")

    # An admitted-uncertain weight passes but scores below a confirmed one.
    sure = score(cand(weight_and_pack_form={"estimate": "0.5 kg", "basis": "FACT"}), DEFAULTS)
    unsure = score(cand(weight_and_pack_form={"estimate": "0.5 kg",
                                              "basis": "ESTIMATE, UNCERTAIN"}), DEFAULTS)
    if not unsure["weight_uncertain"]:
        failures.append("an uncertain basis should be flagged")
    if unsure["score"] >= sure["score"]:
        failures.append("an uncertain weight should score below a confirmed one")

    # F8 injury recall. A safety record must not be outweighed by a score.
    r = screen([cand(dedupe_key="hose",
                     cpsc_recall_history="2025 CPSC recall, 222 burst reports and 29 injuries")])
    if not r["rejected"] or not any(f["filter"] == "F8" for f in r["rejected"][0]["failed"]):
        failures.append("a recall citing injuries should fail F8")
    if r["passed"]:
        failures.append("an injury recall must not reach the ranking")

    # A recall with no injury language does not trip F8 on its own.
    r = screen([cand(dedupe_key="mild",
                     cpsc_recall_history="2019 recall for mislabelled packaging")])
    if any(f["filter"] == "F8" for f in (r["rejected"][0]["failed"] if r["rejected"] else [])):
        failures.append("a non-injury recall should not fail F8")

    # A clean or unchecked history does not trip F8 either.
    for hist in ("no recall found", "UNKNOWN - not searched", ""):
        r = screen([cand(dedupe_key="h" + hist[:3], cpsc_recall_history=hist)])
        if r["rejected"]:
            failures.append("history %r should not fail any filter, got %s"
                            % (hist, r["rejected"][0]["failed"]))

    # A single-source price is discounted, not rejected.
    wide = score(cand(observed_price_range={"low": 34, "high": 40, "basis": "FACT"}), DEFAULTS)
    thin = score(cand(observed_price_range={"low": 37, "high": 37, "basis": "FACT"}), DEFAULTS)
    if not thin["price_single_source"]:
        failures.append("an identical low and high should be flagged single-source")
    if thin["score"] >= wide["score"]:
        failures.append("a single-source price should score below a corroborated one")
    r = screen([cand(dedupe_key="thin", flags=["PRICE_SINGLE_SOURCE"])])
    if not r["passed"]:
        failures.append("a single-source price should be discounted, not rejected")

    # Missing price is a rejection, not a crash.
    r = screen([cand(dedupe_key="f", observed_price_range={})])
    if not any(f["filter"] == "F1" for f in r["rejected"][0]["failed"]):
        failures.append("a candidate with no price should fail F1")

    # Nested demo value shape is tolerated.
    if demo_value({"demonstration_value": {"score": 5}}) != 5:
        failures.append("a nested demonstration_value should be read")

    # String weights are tolerated.
    for text, want in (("0.4 kg", 0.4), ("~400g", 0.4), ("0.85kg", 0.85)):
        got = weight_kg({"estimated_weight_kg": text})
        if got is None or abs(got - want) > 0.01:
            failures.append("weight %r should parse to %.2f, got %s" % (text, want, got))

    # Scoring: a higher ceiling must outrank a lower one, all else equal.
    r = screen([cand(dedupe_key="cheap", observed_price_range={"low": 30, "high": 31}),
                cand(dedupe_key="dear", observed_price_range={"low": 55, "high": 58})])
    if len(r["passed"]) != 2:
        failures.append("both should pass the filters")
    elif r["passed"][0]["dedupe_key"] != "dear":
        failures.append("the higher-ceiling candidate should rank first")

    # Scoring: an unchecked recall history must score below a clean one.
    a = score(cand(cpsc_recall_history="no recall found"), DEFAULTS)
    b = score(cand(cpsc_recall_history="UNKNOWN - not checked"), DEFAULTS)
    c2 = score(cand(cpsc_recall_history="recalled 2020, 95000 units"), DEFAULTS)
    if not a["score"] > b["score"] > c2["score"]:
        failures.append("recall scoring should order clean > unchecked > recalled, got %.1f %.1f %.1f"
                        % (a["score"], b["score"], c2["score"]))

    # A score can never rescue a filter failure.
    r = screen([cand(dedupe_key="g", observed_price_range={"low": 10, "high": 12},
                     demonstration_value=5, complaints=["a", "b", "c"])])
    if r["passed"]:
        failures.append("a perfect-looking candidate must still fail the price filter")

    # The tolerant loader handles both formats.
    with tempfile.TemporaryDirectory() as tmp:
        good = os.path.join(tmp, "good.jsonl")
        with open(good, "w") as fh:
            fh.write(json.dumps(cand()) + "\n" + json.dumps(cand(dedupe_key="y")) + "\n")
        if len(load_jsonl(good)) != 2:
            failures.append("true JSONL should load")
        pretty = os.path.join(tmp, "pretty.jsonl")
        with open(pretty, "w") as fh:
            json.dump(cand(), fh, indent=2)
            fh.write("\n")
            json.dump(cand(dedupe_key="z"), fh, indent=2)
        if len(load_jsonl(pretty)) != 2:
            failures.append("pretty-printed concatenated JSON should also load, since "
                            "round one produced exactly that")

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("screen.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Screen and rank discovery candidates.")
    ap.add_argument("files", nargs="*", help="candidate jsonl files")
    ap.add_argument("--exclude", help="file of dedupe_keys to exclude, one per line")
    ap.add_argument("--price-floor", type=float, default=DEFAULTS["price_floor"])
    ap.add_argument("--demo-floor", type=int, default=DEFAULTS["demo_floor"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.files:
        ap.error("give candidate files or --self-test")
        return 2

    cands = []
    for f in args.files:
        if not os.path.exists(f):
            print("no such file: %s" % f, file=sys.stderr)
            return 2
        cands.extend(load_jsonl(f))

    excluded = []
    if args.exclude and os.path.exists(args.exclude):
        excluded = [l.strip() for l in open(args.exclude) if l.strip()]

    result = screen(cands, {"price_floor": args.price_floor,
                            "demo_floor": args.demo_floor}, excluded)
    if args.json:
        for s in result["passed"]:
            s.pop("candidate", None)
        print(json.dumps(result, indent=2))
    else:
        print(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
