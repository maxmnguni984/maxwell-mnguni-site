#!/usr/bin/env python3
"""Validator for a product-research run folder.

Standard library only. No third-party JSON Schema library: the checks below
are written directly so the script runs anywhere with python3.

Usage:
    python3 validate.py research/runs/2026-09-16-pilot
    python3 validate.py --self-test
    python3 validate.py <run> --json

Exit status 0 when the run is clean, 1 when there are errors, 2 on a usage
problem. Warnings do not change the exit status.

What it checks:
  1. Handoff JSON shape against research/schema/handoff.schema.json (the
     subset that matters: required keys, enums, patterns, types).
  2. Every FACT points at an evidence entry that exists.
  3. Every evidence entry has an http(s) URL, an ISO date, a quote of at most
     300 characters, and a known type.
  4. No orphan evidence IDs and no duplicate evidence IDs.
  5. Product registry lines validate against product.schema.json, IDs are
     unique, and dedupe_keys are unique.
  6. Write ownership: each agent folder holds only that agent's files.
  7. Every handoff's product_id matches its filename and exists in the registry.
  8. Unlabelled-number heuristic: a bare currency or percentage figure in the
     summary that is not covered by a fact, estimate or assumption is a warning.
  9. Finalists have no UNKNOWN gates; rejected products carry a reason.
"""

import argparse
import json
import os
import re
import sys

EVIDENCE_TYPES = {"marketplace", "search", "social", "ad_library", "forum",
                  "supplier", "policy", "registry", "other"}
FLAGS = {"IP_RISK", "SAFETY", "CLAIMS", "PLATFORM_POLICY", "OPS",
         "INJECTION_ATTEMPT", "SOURCE_UNAVAILABLE", "REQUIRES_SAMPLE",
         "SEASONAL", "HYPE"}
AGENTS = {"discovery", "competitor", "supplier", "economics"}
FOLDER_FOR_AGENT = {
    "competitor": "competition",
    "supplier": "suppliers",
    "economics": "economics",
    "discovery": "discovery",
}
STATUSES = {"complete", "partial", "blocked"}
RECOMMENDATIONS = {"proceed", "proceed_with_conditions", "reject"}
CONFIDENCES = {"low", "med", "high"}
PRODUCT_ID_RE = re.compile(r"^P-\d{4}-\d{2}-\d{2}-\d{3}$")
EVIDENCE_ID_RE = re.compile(r"^E-\d{3,}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://")
MONEY_RE = re.compile(r"(?<![\w.])(\$\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?%)")
REGISTRY_GATES = ("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8")
GATE_VALUES = {"pass", "fail", "unknown"}
OWNER_VALUES = {"pending", "running", "done", "partial", "blocked", "skipped"}
REGISTRY_STATUSES = {"candidate", "researching", "held", "rejected", "finalist"}


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, message):
        self.errors.append({"where": where, "message": message})

    def warn(self, where, message):
        self.warnings.append({"where": where, "message": message})

    def ok(self):
        return not self.errors


def _is_str(x, minlen=0):
    return isinstance(x, str) and len(x.strip()) >= minlen


def validate_handoff(doc, where, report, known_product_ids=None):
    """Validate one handoff document. Returns nothing; appends to report."""
    if not isinstance(doc, dict):
        report.error(where, "handoff is not a JSON object")
        return

    required = ["product_id", "agent", "status", "summary", "facts", "estimates",
                "assumptions", "unknowns", "evidence", "flags", "recommendation",
                "limits_used"]
    for key in required:
        if key not in doc:
            report.error(where, "missing required key '%s'" % key)
    if report.errors and any(e["where"] == where and e["message"].startswith("missing required key") for e in report.errors):
        # keep going; the checks below guard on presence
        pass

    pid = doc.get("product_id")
    if not _is_str(pid) or not PRODUCT_ID_RE.match(pid or ""):
        report.error(where, "product_id '%s' does not match P-YYYY-MM-DD-NNN" % pid)
    elif known_product_ids is not None and pid not in known_product_ids:
        report.error(where, "product_id %s is not in products.jsonl" % pid)

    agent = doc.get("agent")
    if agent not in AGENTS:
        report.error(where, "agent '%s' is not one of %s" % (agent, sorted(AGENTS)))

    if doc.get("status") not in STATUSES:
        report.error(where, "status '%s' is not one of %s" % (doc.get("status"), sorted(STATUSES)))

    if not _is_str(doc.get("summary"), 20):
        report.error(where, "summary is missing or shorter than 20 characters")

    rec = doc.get("recommendation")
    if rec not in RECOMMENDATIONS:
        report.error(where, "recommendation '%s' is not one of %s" % (rec, sorted(RECOMMENDATIONS)))
    if rec == "reject" and not _is_str(doc.get("reject_reason"), 3):
        report.error(where, "recommendation is 'reject' but reject_reason is missing")

    flags = doc.get("flags", [])
    if not isinstance(flags, list):
        report.error(where, "flags must be a list")
    else:
        for f in flags:
            if f not in FLAGS:
                report.error(where, "unknown flag '%s'" % f)

    limits = doc.get("limits_used")
    if not isinstance(limits, dict):
        report.error(where, "limits_used must be an object")
    else:
        for key in ("fetches", "searches", "minutes"):
            if not isinstance(limits.get(key), int):
                report.error(where, "limits_used.%s must be an integer" % key)

    # Evidence
    evidence = doc.get("evidence", [])
    ev_ids = set()
    if not isinstance(evidence, list):
        report.error(where, "evidence must be a list")
        evidence = []
    for i, ev in enumerate(evidence):
        eloc = "%s evidence[%d]" % (where, i)
        if not isinstance(ev, dict):
            report.error(eloc, "evidence entry is not an object")
            continue
        eid = ev.get("id")
        if not _is_str(eid) or not EVIDENCE_ID_RE.match(eid or ""):
            report.error(eloc, "id '%s' does not match E-NNN" % eid)
        else:
            if eid in ev_ids:
                report.error(eloc, "duplicate evidence id '%s'" % eid)
            ev_ids.add(eid)
        url = ev.get("url")
        if not _is_str(url) or not URL_RE.match(url or ""):
            report.error(eloc, "url '%s' is not an http(s) URL" % url)
        acc = ev.get("accessed")
        if not _is_str(acc) or not DATE_RE.match(acc or ""):
            report.error(eloc, "accessed '%s' is not YYYY-MM-DD" % acc)
        quote = ev.get("quote")
        if not _is_str(quote, 1):
            report.error(eloc, "quote is missing")
        elif len(quote) > 300:
            report.error(eloc, "quote is %d characters, limit is 300" % len(quote))
        if ev.get("type") not in EVIDENCE_TYPES:
            report.error(eloc, "type '%s' is not one of %s" % (ev.get("type"), sorted(EVIDENCE_TYPES)))
        if "verification" in ev and ev["verification"] not in {"VERIFIED", "SUPPLIER_CLAIM", "OBSERVED"}:
            report.error(eloc, "verification '%s' is not VERIFIED, SUPPLIER_CLAIM or OBSERVED" % ev["verification"])

    # Facts must cite evidence that exists
    facts = doc.get("facts", [])
    used_ids = set()
    if not isinstance(facts, list):
        report.error(where, "facts must be a list")
        facts = []
    for i, fact in enumerate(facts):
        floc = "%s facts[%d]" % (where, i)
        if not isinstance(fact, dict):
            report.error(floc, "fact is not an object")
            continue
        if not _is_str(fact.get("claim"), 3):
            report.error(floc, "claim is missing")
        eid = fact.get("evidence_id")
        if not _is_str(eid) or not EVIDENCE_ID_RE.match(eid or ""):
            report.error(floc, "evidence_id '%s' does not match E-NNN" % eid)
        elif eid not in ev_ids:
            report.error(floc, "evidence_id '%s' has no matching evidence entry" % eid)
        else:
            used_ids.add(eid)

    for eid in sorted(ev_ids - used_ids):
        report.warn(where, "evidence %s is not cited by any fact" % eid)

    # Estimates
    estimates = doc.get("estimates", [])
    if not isinstance(estimates, list):
        report.error(where, "estimates must be a list")
        estimates = []
    for i, est in enumerate(estimates):
        sloc = "%s estimates[%d]" % (where, i)
        if not isinstance(est, dict):
            report.error(sloc, "estimate is not an object")
            continue
        if not _is_str(est.get("claim"), 3):
            report.error(sloc, "claim is missing")
        if not _is_str(est.get("method"), 3):
            report.error(sloc, "method is missing: an estimate must say how it was derived")
        if est.get("confidence") not in CONFIDENCES:
            report.error(sloc, "confidence '%s' is not low, med or high" % est.get("confidence"))

    # Assumptions and unknowns
    assumptions = doc.get("assumptions", [])
    if not isinstance(assumptions, list):
        report.error(where, "assumptions must be a list")
        assumptions = []
    else:
        for i, a in enumerate(assumptions):
            if not _is_str(a, 3):
                report.error("%s assumptions[%d]" % (where, i), "assumption must be a non-empty string")

    unknowns = doc.get("unknowns", [])
    if not isinstance(unknowns, list):
        report.error(where, "unknowns must be a list")
        unknowns = []
    for i, u in enumerate(unknowns):
        uloc = "%s unknowns[%d]" % (where, i)
        if not isinstance(u, dict):
            report.error(uloc, "unknown is not an object")
            continue
        if not _is_str(u.get("question"), 3):
            report.error(uloc, "question is missing")
        if not _is_str(u.get("why_unresolved"), 3):
            report.error(uloc, "why_unresolved is missing: say why it could not be determined")

    # A partial or blocked run should say what is missing
    if doc.get("status") in ("partial", "blocked") and not unknowns:
        report.warn(where, "status is '%s' but unknowns is empty" % doc.get("status"))

    # Unlabelled-number heuristic on the summary
    summary = doc.get("summary") or ""
    labelled_text = " ".join(
        [f.get("claim", "") for f in facts if isinstance(f, dict)]
        + [e.get("claim", "") for e in estimates if isinstance(e, dict)]
        + [a for a in assumptions if isinstance(a, str)]
    )
    for match in set(MONEY_RE.findall(summary)):
        token = match.strip()
        if token not in labelled_text:
            report.warn(where, "summary contains the figure '%s' which is not repeated in any fact, "
                               "estimate or assumption, so its label is unclear" % token)


def validate_registry(path, report):
    """Validate products.jsonl. Returns the set of product IDs."""
    ids = set()
    dedupe_keys = {}
    if not os.path.exists(path):
        report.error("products.jsonl", "registry file is missing")
        return ids
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            where = "products.jsonl:%d" % lineno
            try:
                rec = json.loads(line)
            except ValueError as exc:
                report.error(where, "line is not valid JSON: %s" % exc)
                continue
            pid = rec.get("product_id")
            if not _is_str(pid) or not PRODUCT_ID_RE.match(pid or ""):
                report.error(where, "product_id '%s' does not match P-YYYY-MM-DD-NNN" % pid)
            elif pid in ids:
                report.error(where, "duplicate product_id '%s'" % pid)
            else:
                ids.add(pid)

            key = rec.get("dedupe_key")
            if not _is_str(key, 3):
                report.error(where, "dedupe_key is missing")
            elif key in dedupe_keys:
                report.error(where, "dedupe_key '%s' already used by %s: deduplicate these products"
                             % (key, dedupe_keys[key]))
            else:
                dedupe_keys[key] = pid

            if not _is_str(rec.get("name"), 3):
                report.error(where, "name is missing")

            status = rec.get("status")
            if status not in REGISTRY_STATUSES:
                report.error(where, "status '%s' is not one of %s" % (status, sorted(REGISTRY_STATUSES)))

            gates = rec.get("gates")
            if not isinstance(gates, dict):
                report.error(where, "gates must be an object")
                gates = {}
            else:
                for g in REGISTRY_GATES:
                    if gates.get(g) not in GATE_VALUES:
                        report.error(where, "gate %s is '%s', expected pass, fail or unknown" % (g, gates.get(g)))

            conf = rec.get("confidence")
            if conf not in CONFIDENCES | {"n/a"}:
                report.error(where, "confidence '%s' is not low, med, high or n/a" % conf)

            if not isinstance(rec.get("score"), int):
                report.error(where, "score must be an integer")

            owners = rec.get("owners")
            if not isinstance(owners, dict):
                report.error(where, "owners must be an object")
            else:
                for role in ("competition", "suppliers", "economics"):
                    if owners.get(role) not in OWNER_VALUES:
                        report.error(where, "owners.%s is '%s', expected one of %s"
                                     % (role, owners.get(role), sorted(OWNER_VALUES)))

            if status == "rejected" and not _is_str(rec.get("reject_reason"), 3):
                report.error(where, "status is 'rejected' but reject_reason is empty")

            if status == "finalist":
                unknown_gates = [g for g in REGISTRY_GATES if gates.get(g) == "unknown"]
                failed_gates = [g for g in REGISTRY_GATES if gates.get(g) == "fail"]
                if unknown_gates:
                    report.error(where, "finalist has UNKNOWN gates %s: resolve or hold it"
                                 % ", ".join(unknown_gates))
                if failed_gates:
                    report.error(where, "finalist has FAILED gates %s: a score cannot override a gate"
                                 % ", ".join(failed_gates))
                if isinstance(rec.get("score"), int) and rec["score"] < 65:
                    report.error(where, "finalist score %d is below the threshold of 65" % rec["score"])
                if conf == "low":
                    report.error(where, "finalist confidence is low; the threshold is medium")
    return ids


def validate_run(run_dir, report):
    run_dir = os.path.abspath(run_dir)
    if not os.path.isdir(run_dir):
        report.error(run_dir, "run folder does not exist")
        return

    if not os.path.exists(os.path.join(run_dir, "brief.md")):
        report.error("brief.md", "missing: every run needs a brief")

    product_ids = validate_registry(os.path.join(run_dir, "products.jsonl"), report)

    for agent, folder in sorted(FOLDER_FOR_AGENT.items()):
        fdir = os.path.join(run_dir, folder)
        if not os.path.isdir(fdir):
            continue
        for name in sorted(os.listdir(fdir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(fdir, name)
            where = "%s/%s" % (folder, name)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    doc = json.load(fh)
            except ValueError as exc:
                report.error(where, "not valid JSON: %s" % exc)
                continue

            if folder == "discovery":
                # discovery writes candidates, not per-product handoffs
                if isinstance(doc, dict) and doc.get("agent") == "discovery":
                    validate_handoff(doc, where, report, product_ids or None)
                continue

            validate_handoff(doc, where, report, product_ids or None)

            if isinstance(doc, dict):
                if doc.get("agent") != agent:
                    report.error(where, "file is in %s/ but agent is '%s': write ownership violated"
                                 % (folder, doc.get("agent")))
                pid = doc.get("product_id")
                stem = name[:-len(".json")]
                if _is_str(pid) and stem != pid:
                    report.error(where, "filename stem '%s' does not match product_id '%s'" % (stem, pid))

    # Cross-check: a finalist must have all three deep handoffs on disk
    reg_path = os.path.join(run_dir, "products.jsonl")
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("status") != "finalist":
                    continue
                pid = rec.get("product_id")
                for folder in ("competition", "suppliers", "economics"):
                    expected = os.path.join(run_dir, folder, "%s.json" % pid)
                    if not os.path.exists(expected):
                        report.error("products.jsonl", "finalist %s has no %s/%s.json" % (pid, folder, pid))
                vpath = os.path.join(run_dir, "validation", "%s.md" % pid)
                if not os.path.exists(vpath):
                    report.error("products.jsonl", "finalist %s has no validation/%s.md" % (pid, pid))


# ---------------------------------------------------------------- self-test

GOOD_HANDOFF = {
    "product_id": "P-2026-09-16-001",
    "agent": "supplier",
    "status": "complete",
    "summary": "Two suppliers list this item with tracked US shipping; costs and stated transit days recorded below.",
    "facts": [
        {"claim": "Supplier A lists the unit at $7.80 for the single-pack variant", "evidence_id": "E-001"}
    ],
    "estimates": [
        {"claim": "Landed cost is about $12.30 per unit", "method": "unit cost plus quoted shipping plus an assumed 15% duty", "confidence": "med"}
    ],
    "assumptions": ["Duty rate of 15% pending confirmation of the HTS code"],
    "unknowns": [{"question": "Actual duty rate", "why_unresolved": "HTS classification not stated by the supplier"}],
    "evidence": [
        {"id": "E-001", "url": "https://example.com/product/123", "accessed": "2026-09-16",
         "quote": "Single pack, US warehouse, $7.80", "type": "supplier", "verification": "SUPPLIER_CLAIM"}
    ],
    "flags": ["REQUIRES_SAMPLE"],
    "recommendation": "proceed_with_conditions",
    "limits_used": {"fetches": 12, "searches": 6, "minutes": 18},
}

BAD_HANDOFF = {
    "product_id": "P-9-1",
    "agent": "spy",
    "status": "done",
    "summary": "sells well",
    "facts": [{"claim": "Sells 4,000 units a month", "evidence_id": "E-999"}],
    "estimates": [{"claim": "Margin is good", "confidence": "certain"}],
    "assumptions": [],
    "unknowns": [],
    "evidence": [
        {"id": "E-001", "url": "not-a-url", "accessed": "16/09/2026", "quote": "x" * 400, "type": "vibes"}
    ],
    "flags": ["MADE_UP_FLAG"],
    "recommendation": "reject",
    "limits_used": {"fetches": "twelve", "searches": 6},
}


def self_test():
    failures = []

    good = Report()
    validate_handoff(GOOD_HANDOFF, "good.json", good)
    if not good.ok():
        failures.append("good handoff should validate, got errors: %s"
                        % "; ".join(e["message"] for e in good.errors))

    bad = Report()
    validate_handoff(BAD_HANDOFF, "bad.json", bad)
    messages = " | ".join(e["message"] for e in bad.errors)
    expected_substrings = [
        "product_id",
        "agent 'spy'",
        "status 'done'",
        "summary is missing or shorter",
        "has no matching evidence entry",
        "method is missing",
        "confidence 'certain'",
        "url 'not-a-url'",
        "accessed '16/09/2026'",
        "limit is 300",
        "type 'vibes'",
        "unknown flag 'MADE_UP_FLAG'",
        "reject_reason is missing",
        "limits_used.fetches",
        "limits_used.minutes",
    ]
    for sub in expected_substrings:
        if sub not in messages:
            failures.append("bad handoff: expected an error mentioning %r, got: %s" % (sub, messages))

    # A fabricated figure in the summary with no label produces a warning.
    sloppy = json.loads(json.dumps(GOOD_HANDOFF))
    sloppy["summary"] = "This product does about $40,000 a month in revenue across competitors."
    warn_report = Report()
    validate_handoff(sloppy, "sloppy.json", warn_report)
    if not any("40,000" in w["message"] for w in warn_report.warnings):
        failures.append("unlabelled figure in summary should raise a warning")

    # Duplicate evidence IDs are caught.
    dup = json.loads(json.dumps(GOOD_HANDOFF))
    dup["evidence"].append(dict(dup["evidence"][0]))
    dup_report = Report()
    validate_handoff(dup, "dup.json", dup_report)
    if not any("duplicate evidence id" in e["message"] for e in dup_report.errors):
        failures.append("duplicate evidence id should be an error")

    # Registry checks, on a temporary folder.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        run = os.path.join(tmp, "2026-09-16-selftest")
        for sub in ("discovery", "competition", "suppliers", "economics", "validation"):
            os.makedirs(os.path.join(run, sub))
        with open(os.path.join(run, "brief.md"), "w", encoding="utf-8") as fh:
            fh.write("# brief\n")
        rows = [
            {"product_id": "P-2026-09-16-001", "name": "Thing one", "dedupe_key": "thing-one",
             "niche": "kitchen", "status": "rejected", "first_seen_run": "selftest",
             "gates": {g: "pass" for g in REGISTRY_GATES}, "score": 0, "confidence": "n/a",
             "reject_reason": None,
             "owners": {"competition": "done", "suppliers": "done", "economics": "done"}},
            {"product_id": "P-2026-09-16-001", "name": "Thing one again", "dedupe_key": "thing-one",
             "niche": "kitchen", "status": "finalist", "first_seen_run": "selftest",
             "gates": dict({g: "pass" for g in REGISTRY_GATES}, G2="unknown"), "score": 40,
             "confidence": "low", "reject_reason": None,
             "owners": {"competition": "done", "suppliers": "done", "economics": "done"}},
        ]
        with open(os.path.join(run, "products.jsonl"), "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        reg = Report()
        validate_run(run, reg)
        regmsgs = " | ".join(e["message"] for e in reg.errors)
        for sub in ["duplicate product_id", "dedupe_key", "reject_reason is empty",
                    "UNKNOWN gates", "score 40 is below", "confidence is low",
                    "has no competition/"]:
            if sub not in regmsgs:
                failures.append("registry: expected an error mentioning %r, got: %s" % (sub, regmsgs))

        # Write-ownership violation: an economics handoff sitting in suppliers/
        misplaced = json.loads(json.dumps(GOOD_HANDOFF))
        misplaced["agent"] = "economics"
        with open(os.path.join(run, "suppliers", "P-2026-09-16-001.json"), "w", encoding="utf-8") as fh:
            json.dump(misplaced, fh)
        own = Report()
        validate_run(run, own)
        if not any("write ownership violated" in e["message"] for e in own.errors):
            failures.append("an economics handoff in suppliers/ should violate write ownership")

        # A clean minimal run passes.
        clean = os.path.join(tmp, "2026-09-16-clean")
        for sub in ("discovery", "competition", "suppliers", "economics", "validation"):
            os.makedirs(os.path.join(clean, sub))
        with open(os.path.join(clean, "brief.md"), "w", encoding="utf-8") as fh:
            fh.write("# brief\n")
        with open(os.path.join(clean, "products.jsonl"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "product_id": "P-2026-09-16-001", "name": "Thing one", "dedupe_key": "thing-one",
                "niche": "kitchen", "status": "researching", "first_seen_run": "clean",
                "gates": {g: "pass" for g in REGISTRY_GATES}, "score": 0, "confidence": "med",
                "reject_reason": None,
                "owners": {"competition": "done", "suppliers": "done", "economics": "pending"}}) + "\n")
        with open(os.path.join(clean, "suppliers", "P-2026-09-16-001.json"), "w", encoding="utf-8") as fh:
            json.dump(GOOD_HANDOFF, fh)
        cr = Report()
        validate_run(clean, cr)
        if not cr.ok():
            failures.append("clean run should validate, got: %s"
                            % "; ".join("%s %s" % (e["where"], e["message"]) for e in cr.errors))

    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  - " + f)
        return 1
    print("validate.py self-test: all checks passed")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate a research run folder.")
    ap.add_argument("run", nargs="?", help="path to research/runs/<run-id>")
    ap.add_argument("--json", action="store_true", help="print machine-readable output")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.run:
        ap.error("give a run folder or --self-test")
        return 2

    report = Report()
    validate_run(args.run, report)

    if args.json:
        print(json.dumps({"ok": report.ok(), "errors": report.errors,
                          "warnings": report.warnings}, indent=2))
    else:
        for w in report.warnings:
            print("WARN  %s: %s" % (w["where"], w["message"]))
        for e in report.errors:
            print("ERROR %s: %s" % (e["where"], e["message"]))
        print("")
        print("%d error(s), %d warning(s)" % (len(report.errors), len(report.warnings)))
    return 0 if report.ok() else 1


if __name__ == "__main__":
    sys.exit(main())
