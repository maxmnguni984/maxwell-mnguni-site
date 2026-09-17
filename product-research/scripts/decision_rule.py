#!/usr/bin/env python3
"""Pre-registered decision rule for a buying-intent test.

    python3 decision_rule.py --clicks 300
    python3 decision_rule.py --clicks 500 --dead 0.005 --viable 0.02

Exact binomial arithmetic, no approximations and no borrowed benchmarks. Use it
to set the pass threshold BEFORE spending, and to read the result afterwards.

The asymmetry this exposes is the point: a cheap test is far better at
disproving demand than proving it. Design to kill; treat a pass as provisional.
"""

import argparse
from math import comb, sqrt


def p_at_least(k, n, p):
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    ph = k / n
    d = 1 + z * z / n
    centre = (ph + z * z / (2 * n)) / d
    half = z * sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half) * 100, min(1.0, centre + half) * 100)


def main():
    ap = argparse.ArgumentParser(description="Set and read a buying-intent decision rule.")
    ap.add_argument("--clicks", type=int, default=300)
    ap.add_argument("--dead", type=float, default=0.005, help="rate considered commercially dead")
    ap.add_argument("--viable", type=float, default=0.02, help="rate considered viable")
    ap.add_argument("--observed", type=int, help="payers actually observed, to read a result")
    ap.add_argument("--max-false-pass", type=float, default=0.05,
                    help="largest acceptable chance of green-lighting a dead product")
    a = ap.parse_args()
    n = a.clicks

    print("Test size: {} clicks.  Dead = {:.1%}.  Viable = {:.1%}.\n".format(n, a.dead, a.viable))
    print("{:>10}{:>16}{:>16}".format("threshold", "passes if dead", "catches if viable"))
    print("-" * 42)
    chosen = None
    for k in range(1, 13):
        fp = p_at_least(k, n, a.dead)
        pw = p_at_least(k, n, a.viable)
        mark = ""
        if chosen is None and fp <= a.max_false_pass:
            chosen, mark = k, "   <-- recommended"
        print("{:>10}{:>15.1%}{:>15.1%}{}".format(">= " + str(k), fp, pw, mark))

    upper = (1 - 0.05 ** (1.0 / n)) * 100
    print("\nIf ZERO payers: true rate is below {:.2f}% at 95% confidence.".format(upper))
    print("That alone is usually enough to cancel an order.")
    print("\nA dead product still produces at least one sale {:.1%} of the time at this size."
          .format(p_at_least(1, n, a.dead)))
    print("One sale is the EXPECTED outcome of a dead product, not evidence of life.")

    if chosen:
        print("\nPRE-REGISTER THIS: pass requires >= {} payers out of {} clicks.".format(chosen, n))
        print("  chance of passing a dead product:  {:.1%}".format(p_at_least(chosen, n, a.dead)))
        print("  chance of catching a viable one:   {:.1%}".format(p_at_least(chosen, n, a.viable)))

    if a.observed is not None:
        k = a.observed
        lo, hi = wilson(k, n)
        print("\nRESULT: {} payers of {} clicks = {:.2f}%".format(k, n, k / n * 100))
        print("  95% interval: {:.2f}% to {:.2f}%".format(lo, hi))
        if chosen is None:
            verdict = "no threshold met the false-pass limit"
        elif k == 0:
            verdict = "HARD KILL - true rate below {:.2f}%".format(upper)
        elif k >= chosen:
            verdict = "PASS - but the interval is wide; treat as provisional"
        else:
            verdict = "FAIL - a dead product reaches this {:.1%} of the time".format(
                p_at_least(k, n, a.dead))
        print("  verdict: {}".format(verdict))


if __name__ == "__main__":
    main()
