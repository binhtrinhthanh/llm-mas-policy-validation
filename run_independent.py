"""Sample policy updates using one fresh, feedback-free API request per trial."""
import argparse
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tool_source"))

from catalog import TASKS
from study import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Model ID, preferably a pinned snapshot")
    parser.add_argument("--trials", type=int, default=5, help="Independent requests per task")
    parser.add_argument("--seeds", type=int, default=20, help="Scenario seeds per family")
    parser.add_argument("--tasks", nargs="+", choices=tuple(TASKS), default=list(TASKS))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is required for real model sampling.")
    from openai import OpenAI

    # A fresh API request gets only the task prompt. The study's budget-one
    # path evaluates the response without returning any results to the model.
    summary = run(OpenAI(max_retries=0), args.model, args.out, tasks=args.tasks,
                  trials=args.trials, seeds=args.seeds, budget=1)
    # The existing study repeats the same initial candidate in all three arms
    # at budget one. Export only the initial arm for independent sample counts.
    with (args.out / "trials.csv").open(newline="") as stream:
        samples = [row for row in csv.DictReader(stream) if row["arm"] == "initial"]
    if len(samples) != summary["completed_unique_requests"]:
        raise ValueError("Expected one initial result per independent request")
    with (args.out / "independent_samples.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    passed = sum(row["final_passed"] == "True" for row in samples)
    print(f"{passed}/{len(samples)} independently sampled artifacts passed the final suite")


if __name__ == "__main__":
    main()
