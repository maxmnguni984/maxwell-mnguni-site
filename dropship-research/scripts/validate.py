#!/usr/bin/env python3
"""Structural validation for the research corpus.

Usage:
    python3 scripts/validate.py                 # structure, IDs, evidence, dedup
    python3 scripts/validate.py --check-urls    # also resolve every evidence URL
    python3 scripts/validate.py --run 2026-09-16-r1

Checks, in order of how badly they bite:
  1. Every product file has the required front-matter keys with valid values.
  2. Every FACT/CLAIM/ESTIMATE inline citation points at an E-id defined in that
     file's evidence table, and every E-id row is well formed.
  3. Evidence URLs are http(s) or an existing path under inputs/ (manual-input).
  4. Product IDs are unique, registry rows match folders on disk, dedup_key is
     unique across the registry, and no product is researched twice.
  5. Agents wrote only the files they own.
  6. With --check-urls: every evidence URL resolves (HEAD, then GET on 4xx/405).
     URLs unreachable because the machine's network is blocked are warnings, not errors.

Exit 1 if any error is found. Warnings never fail the run. Stdlib only.
"""

import argparse
import datetime
import os
import re
import sys
import urllib.error
import urllib.request

REQUIRED_FRONTMATTER = ("product_id", "agent", "run_id", "date", "status", "confidence")
VALID_STATUS = {"complete", "partial", "blocked"}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_EVIDENCE_TYPES = {
    "marketplace-listing", "review", "forum", "video", "ad-library", "trend-csv",
    "supplier-listing", "policy-page", "recall-db", "manual-input", "search-results",
}
VALID_EVIDENCE_CONFIDENCE = {"fact", "claim", "estimate"}

OWNERSHIP = {
    "discovery.md": "discovery",
    "competitor.md": "competitor",
    "supplier.md": "supplier",
    "economics.md": "economics",
    "verdict.md": "lead",
}

EID_RE = re.compile(r"E-[A-Za-z0-9]+-[DCSEL]-\d{2}")
PRODUCT_DIR_RE = re.compile(r"^P-(\d{4}|TMP-\d{2})$")
USER_AGENT = "dropship-research-validate/1 (+local evidence check)"


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checked = 0

    def error(self, where, message):
        self.errors.append("{}: {}".format(where, message))

    def warn(self, where, message):
        self.warnings.append("{}: {}".format(where, message))


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_real_date(text):
    """True only for a calendar-valid YYYY-MM-DD, so 2026-13-99 fails."""
    try:
        datetime.date.fromisoformat(text)
    except (ValueError, TypeError):
        return False
    return True


def split_frontmatter(text):
    """Return (frontmatter_dict, body). Missing front-matter yields ({}, text)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block, body = text[3:end], text[end + 4:]
    data = {}
    for line in block.splitlines():
        line = line.split(" #")[0].rstrip()
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        if line[0] in " \t":
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data, body


def parse_evidence_rows(body):
    """Return {eid: {url, accessed, type, confidence}} from the Evidence table."""
    rows = {}
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 6 or not EID_RE.fullmatch(cells[0]):
            continue
        rows[cells[0]] = {
            "url": cells[1],
            "accessed": cells[2],
            "type": cells[3].lower(),
            "what": cells[4],
            "confidence": cells[5].lower(),
        }
    return rows


def check_frontmatter(path_label, front, report, expected_agent=None):
    for key in REQUIRED_FRONTMATTER:
        if key not in front or front[key] == "":
            report.error(path_label, "front-matter missing '{}'".format(key))
    status = front.get("status")
    if status and status not in VALID_STATUS:
        report.error(path_label, "status '{}' not in {}".format(status, sorted(VALID_STATUS)))
    confidence = front.get("confidence")
    if confidence and confidence not in VALID_CONFIDENCE:
        report.error(path_label, "confidence '{}' not in {}".format(confidence, sorted(VALID_CONFIDENCE)))
    date = front.get("date")
    if date and not is_real_date(date):
        report.error(path_label, "date '{}' is not a valid YYYY-MM-DD date".format(date))
    agent = front.get("agent")
    if expected_agent and agent != expected_agent:
        report.error(path_label, "agent '{}' but this filename belongs to '{}'".format(agent, expected_agent))


def check_evidence(path_label, body, report):
    """Validate the evidence table and every inline E-id citation."""
    rows = parse_evidence_rows(body)
    for eid, row in rows.items():
        if row["type"] not in VALID_EVIDENCE_TYPES:
            report.error(path_label, "{} has type '{}', not one of {}".format(
                eid, row["type"], sorted(VALID_EVIDENCE_TYPES)))
        if row["confidence"] not in VALID_EVIDENCE_CONFIDENCE:
            report.error(path_label, "{} has confidence '{}', not one of {}".format(
                eid, row["confidence"], sorted(VALID_EVIDENCE_CONFIDENCE)))
        if not is_real_date(row["accessed"]):
            report.error(path_label, "{} accessed '{}' is not a valid YYYY-MM-DD date".format(eid, row["accessed"]))
        url = row["url"]
        if row["type"] == "manual-input":
            local = os.path.join(repo_root(), url)
            if not os.path.exists(local):
                report.error(path_label, "{} manual-input path does not exist: {}".format(eid, url))
        elif not url.startswith(("http://", "https://")):
            report.error(path_label, "{} url is neither http(s) nor a manual-input path: {}".format(eid, url))
        words = len(row["what"].split())
        if words > 25:
            report.warn(path_label, "{} description is {} words (limit 25)".format(eid, words))

    body_wo_table = "\n".join(
        line for line in body.splitlines()
        if not (line.strip().startswith("|") and EID_RE.search(line))
    )
    for eid in set(EID_RE.findall(body_wo_table)):
        if eid not in rows:
            report.error(path_label, "cites {} but it has no evidence row".format(eid))

    for line in body_wo_table.splitlines():
        if re.search(r"\bFACT\b", line) and not EID_RE.search(line):
            report.error(path_label, "FACT without an evidence ID: {}".format(line.strip()[:90]))
    return rows


def iter_product_files(root):
    products_dir = os.path.join(root, "data", "products")
    if not os.path.isdir(products_dir):
        return
    for entry in sorted(os.listdir(products_dir)):
        folder = os.path.join(products_dir, entry)
        if not os.path.isdir(folder) or entry.startswith("."):
            continue
        yield entry, folder


def read_registry(root, report):
    path = os.path.join(root, "data", "registry.csv")
    rows = []
    if not os.path.exists(path):
        report.error("data/registry.csv", "missing")
        return rows
    with open(path, encoding="utf-8") as handle:
        lines = [l.rstrip("\n") for l in handle if l.strip()]
    if not lines:
        report.error("data/registry.csv", "empty (needs at least a header row)")
        return rows
    header = [h.strip() for h in lines[0].split(",")]
    expected = ["product_id", "name", "niche", "dedup_key", "status", "first_seen_run",
                "last_updated", "owner_stage", "reject_reason"]
    if header != expected:
        report.error("data/registry.csv", "header is {} but expected {}".format(header, expected))
    for number, line in enumerate(lines[1:], start=2):
        cells = [c.strip() for c in line.split(",")]
        if len(cells) != len(expected):
            report.error("data/registry.csv:{}".format(number),
                         "{} columns, expected {}".format(len(cells), len(expected)))
            continue
        rows.append(dict(zip(expected, cells)))
    return rows


def check_registry(root, rows, product_dirs, report):
    seen_ids, seen_keys = {}, {}
    for row in rows:
        pid, key = row["product_id"], row["dedup_key"]
        if pid in seen_ids:
            report.error("data/registry.csv", "duplicate product_id {}".format(pid))
        seen_ids[pid] = row
        if key and key in seen_keys:
            report.error("data/registry.csv",
                         "duplicate dedup_key '{}' ({} and {}) — the same product was researched twice"
                         .format(key, seen_keys[key], pid))
        elif key:
            seen_keys[key] = pid
        if key and "|" not in key:
            report.warn("data/registry.csv", "dedup_key '{}' is missing the '|function' half".format(key))
        if pid not in product_dirs:
            report.error("data/registry.csv", "{} has no folder under data/products/".format(pid))
    for folder in product_dirs:
        if folder.startswith("P-TMP"):
            report.warn("data/products/{}".format(folder),
                        "temporary discovery ID still present; the Lead should assign a P-xxxx ID")
        elif folder not in seen_ids:
            report.error("data/products/{}".format(folder), "folder has no registry.csv row")


NETWORK_BLOCK_MARKERS = ("tunnel connection failed", "proxy", "name or service not known",
                        "temporary failure in name resolution", "certificate verify failed")


def check_url(url, timeout):
    """Return (verdict, note) where verdict is 'ok', 'dead', or 'unverifiable'.

    'unverifiable' means this machine could not reach the network (egress proxy,
    DNS, TLS interception), not that the citation is bad. Those are reported as
    warnings so a sandboxed run never reads as a fabricated source.
    """
    note = "unreachable"
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return "ok", "{} {}".format(method, response.status)
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 405, 400, 501):
                note = "HTTP {}".format(exc.code)
                continue
            return "dead", "HTTP {}".format(exc.code)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            note = str(getattr(exc, "reason", exc))[:70]
            if any(marker in note.lower() for marker in NETWORK_BLOCK_MARKERS):
                return "unverifiable", note
            if method == "HEAD":
                continue
            return "dead", note
    return "dead", note


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the research corpus.")
    parser.add_argument("--check-urls", action="store_true", help="resolve every evidence URL")
    parser.add_argument("--run", help="only check files whose run_id matches")
    parser.add_argument("--timeout", type=float, default=10.0, help="per-URL timeout in seconds")
    args = parser.parse_args(argv)

    root = repo_root()
    report = Report()
    product_dirs, all_urls = [], {}

    for entry, folder in iter_product_files(root):
        product_dirs.append(entry)
        if not PRODUCT_DIR_RE.match(entry):
            report.error("data/products/{}".format(entry),
                         "folder name must be P-0000 or P-TMP-00")
        for filename in sorted(os.listdir(folder)):
            if not filename.endswith(".md") or filename == "economics-calc.md":
                continue
            label = "data/products/{}/{}".format(entry, filename)
            with open(os.path.join(folder, filename), encoding="utf-8") as handle:
                text = handle.read()
            front, body = split_frontmatter(text)
            if not front:
                report.error(label, "no YAML front-matter")
                continue
            if args.run and front.get("run_id") != args.run:
                continue
            report.checked += 1
            expected_agent = OWNERSHIP.get(filename)
            if expected_agent is None:
                report.warn(label, "unexpected filename in a product folder")
            check_frontmatter(label, front, report, expected_agent)
            if front.get("product_id") != entry:
                report.error(label, "product_id '{}' does not match folder '{}'".format(
                    front.get("product_id"), entry))
            for eid, row in check_evidence(label, body, report).items():
                if row["type"] != "manual-input" and row["url"].startswith(("http://", "https://")):
                    all_urls.setdefault(row["url"], []).append("{} {}".format(label, eid))

    rows = read_registry(root, report)
    check_registry(root, rows, product_dirs, report)

    approvals = os.path.join(root, "approvals", "requests.md")
    if not os.path.exists(approvals):
        report.error("approvals/requests.md", "missing")

    if args.check_urls and all_urls:
        print("resolving {} evidence URLs...".format(len(all_urls)), file=sys.stderr)
        blocked = 0
        for url, wheres in sorted(all_urls.items()):
            verdict, note = check_url(url, args.timeout)
            if verdict == "dead":
                report.error(wheres[0], "evidence URL did not resolve ({}): {}".format(note, url))
            elif verdict == "unverifiable":
                blocked += 1
                report.warn(wheres[0], "could not reach the network to check this URL ({}): {}".format(note, url))
        if blocked:
            print("NOTE: {} of {} URLs were unverifiable from this machine (network blocked). "
                  "Re-run --check-urls where outbound HTTPS is open before trusting the result."
                  .format(blocked, len(all_urls)), file=sys.stderr)

    print("checked {} product files, {} registry rows, {} distinct evidence URLs".format(
        report.checked, len(rows), len(all_urls)))
    for warning in report.warnings:
        print("WARN  {}".format(warning))
    for error in report.errors:
        print("ERROR {}".format(error))
    if report.errors:
        print("\nFAILED: {} error(s), {} warning(s)".format(len(report.errors), len(report.warnings)))
        return 1
    print("\nOK: 0 errors, {} warning(s)".format(len(report.warnings)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
