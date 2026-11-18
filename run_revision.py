"""Reproduce paired interaction tests and attribute post-freeze detections."""
import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

from run_integration import ROOT, SCENARIOS, SEEDS, MAS, load_frozen, policy, quote, variants
from compare_suites import assess


class ObservedMAS(MAS):
    """Record the emitting check and the message step for each diagnostic."""

    def __init__(self, functions):
        self.diagnostics = []
        super().__init__(functions, "bundle_pipeline")

    def error(self, name):
        origin = sys._getframe(1).f_code.co_name
        component = {
            "check": "observer",
            "final_check": "observer",
            "expect": "checkpoint",
            "execution": "runtime_diagnostic",
        }[origin]
        entry = dict(component=component, check=name, step=len(self.trace) - 1)
        if not any(item["component"] == component and item["check"] == name
                   for item in self.diagnostics):
            self.diagnostics.append(entry)
        super().error(name)


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_once(source, before, after):
    if source.count(before) != 1:
        raise ValueError(f"Expected one mutation site: {before!r}")
    return source.replace(before, after, 1)


def run_interactions(frozen):
    risk = frozen["reservation"]
    market_source = frozen["freshness"]
    # Use explicit, schema-valid corner cases outside the archived suites.
    # The targeted stale quote is filtered independently by Market or Risk.
    edits_by_case = {
        "stale_oversized_order": (
            replace_once(market_source, '> 5:', '> 5 and not (event["age"] == 6 and event["qty"] == 11):'),
            replace_once(risk, '> 10 or', '> 10 and not (order["qty"] == 11 and 46 <= order["price"] <= 65) or'),
        ),
        "stale_overcommitted_order": (
            replace_once(market_source, '> 5:',
                         '> 5 and not (event["age"] == 6 and 91 <= event["price"] <= 99):'),
            replace_once(risk, '    cost =',
                         '    if order["qty"] == 10 and 91 <= order["price"] <= 99:\n'
                         '        available = event["cash"]\n'
                         '    cost ='),
        ),
    }
    rows, regression, witnesses = [], [], {}
    for case, (market, altered_risk) in edits_by_case.items():
        for configuration, edits in (
            ("frozen", {}), ("market_only", {"freshness": market}),
            ("risk_only", {"reservation": altered_risk}),
            ("joint", {"freshness": market, "reservation": altered_risk}),
        ):
            functions = {key: policy(value) for key, value in {**frozen, **edits}.items()}
            for suite in ("original", "post_freeze"):
                outcomes = list(assess(suite, functions))
                regression.append(dict(case=case, configuration=configuration, suite=suite,
                                       runs=len(outcomes),
                                       failures=sum(bool(errors) for _, _, errors in outcomes)))
            for seed in SEEDS:
                rng = random.Random(seed)
                system = ObservedMAS(functions)
                if case == "stale_oversized_order":
                    quote(system, rng.randint(46, 65), 11, age=6)
                    expected_orders = []
                else:
                    price = rng.randint(91, 99)
                    quote(system, price, 10)
                    quote(system, price, 10, age=6)
                    expected_orders = ["o1"]
                violations = sorted(system.final_check())
                orders = sorted(entry["oid"] for entry in system.exchange_orders.values())
                if orders != expected_orders:
                    violations.append("expected_exchange_orders")
                expected = {
                    "stale_oversized_order": ["fresh_market_data", "expected_exchange_orders"],
                    "stale_overcommitted_order": [
                        "cash_exposure", "fresh_market_data", "expected_exchange_orders",
                    ],
                }[case] if configuration == "joint" else []
                if violations != expected:
                    raise AssertionError((case, configuration, seed, violations))
                row = dict(case=case, configuration=configuration, seed=seed,
                           orders="|".join(orders), violations="|".join(violations))
                rows.append(row)
                if seed == SEEDS.start:
                    witnesses[f"{case}/{configuration}"] = {
                        **row, "diagnostics": system.diagnostics,
                        "trace": system.trace, "policy_calls": system.commands,
                    }
    return rows, regression, witnesses


def run_attribution(frozen):
    rows, breakdown, witnesses = [], [], {}
    for name, sources in variants(frozen):
        functions = {key: policy(value) for key, value in sources.items()}
        original = Counter(family for family, _, errors in assess("original", functions) if errors)
        failures = Counter()
        for scenario in SCENARIOS:
            family = scenario.__name__
            for seed in SEEDS:
                system = ObservedMAS(functions)
                scenario(system, random.Random(seed))
                system.final_check()
                components = {entry["component"] for entry in system.diagnostics}
                row = dict(variant=name, scenario=family, seed=seed, schema_pass=True,
                           observer="observer" in components,
                           checkpoint="checkpoint" in components,
                           runtime_diagnostic="runtime_diagnostic" in components,
                           violations="|".join(sorted(system.errors)))
                rows.append(row)
                if system.diagnostics:
                    failures[family] += 1
                    witnesses.setdefault(f"{name}/{family}", {
                        **row, "diagnostics": system.diagnostics,
                        "trace": system.trace, "policy_calls": system.commands,
                    })
        selected = [row for row in rows if row["variant"] == name]
        breakdown.append(dict(
            variant=name,
            original_failed=sum(original.values()), original_families="|".join(sorted(original)),
            post_freeze_failed=sum(failures.values()), post_freeze_families="|".join(sorted(failures)),
            observer_failed=sum(row["observer"] for row in selected),
            checkpoint_failed=sum(row["checkpoint"] for row in selected),
            checkpoint_only=sum(row["checkpoint"] and not row["observer"]
                                and not row["runtime_diagnostic"] for row in selected),
            runtime_diagnostic_runs=sum(row["runtime_diagnostic"] for row in selected),
        ))
    return rows, breakdown, witnesses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New directory for results")
    out = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=False)
    frozen = load_frozen()
    interaction, regression, interaction_witnesses = run_interactions(frozen)
    attribution, breakdown, mutant_witnesses = run_attribution(frozen)
    write_csv(out / "interaction_runs.csv", interaction)
    write_csv(out / "interaction_archived_suites.csv", regression)
    write_csv(out / "attribution_runs.csv", attribution)
    write_csv(out / "attribution_by_variant.csv", breakdown)
    for filename, data in (("interaction_witnesses.json", interaction_witnesses),
                           ("mutant_witnesses.json", mutant_witnesses)):
        (out / filename).write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
