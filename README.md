# Scenario-Based Validation of LLM-Assisted Policy Updates in Multi-Agent Systems

Research artifact accompanying the manuscript. It contains the stock-trading
simulator, policy evaluator, archived candidates, and experimental results
for individual and coordinated policy updates, interaction faults, and
fault detection.

## Results at a glance

| Evaluation | Result |
|---|---|
| Archived assistant-authored updates | Six policies and three derived bundles completed 4,240 scenario executions with no observed violations. |
| Paired interaction assessment | In each of two constructed Market Data–Risk cases, the frozen and both single-update configurations had 0/30 violating runs each. The joint-update configuration had 30/30 violating runs in each case. |
| Post-freeze fault detection | On the same 1,080 mutant executions, the runtime observer detected 6/9 mutants and flagged 240 runs. With scenario checkpoints, detection increased to 9/9 mutants and 330 flagged runs. |
| Independently sampled updates | 43/45 candidates passed the final suite, including 28/30 single-policy candidates and 15/15 coordinated bundles. |

## System and validation

The Market Data, Analysis, Portfolio, Risk, Execution, and Reconciliation
agents exchange messages through a FIFO queue in one process. The simulator
uses synthetic quotes and a buy-side exchange model. The six individual
tasks cover timeout retry, quote freshness, pending cash reservation,
partial-fill accounting, notification deduplication, and late-fill
reconciliation. The three coordinated tasks update Market Data and
Execution, Risk and Execution, or four agent policies together.

Candidate functions receive copied inputs and return structured commands.
The evaluator checks the permitted Python constructs before integration,
validates commands during execution, and checks the resulting behavior
against invariants and scenario outcome checkpoints. Execution traces
record messages and policy invocations for diagnosis. Resource-limited
workers are designed to execute restricted policies in this study.
Arbitrary Python requires a separate operating-system sandbox.

## Reproduce the archived experiments

Use Linux and Python 3.10 or later. The reported replay was checked with
Python 3.12.14 on Linux x86_64. These commands use the standard library
and require no API key.

```sh
python run.py --out results/reproduced
python verify_reproduction.py

python run_integration.py
diff -u results/integration/runs.csv results/integration_reproduced/runs.csv

python compare_suites.py
diff -u results/comparison/runs.csv results/comparison_reproduced/runs.csv

python run_revision.py --out results/revision_reproduced
diff -r results/revision results/revision_reproduced
```

The replay checks frozen candidate hashes before execution. The original
reproduction verifier compares behavioral counts and outcomes, excluding
timing. GitHub Actions runs the commands above.

### Archived assistant-authored updates

A coding assistant authored six restricted Python policies with prior
knowledge of the simulator, reference policies, and evaluator. Three
coordinated configurations reuse those policies. The archived candidates
completed 1,220 development and 3,020 final-suite scenario executions.
Including the baseline configurations, this assessment comprised 8,480
executions. The baselines deliberately omit the requested capabilities.
Results and baseline failure traces are in `results/reported/`.

### Post-freeze assessment and paired interaction cases

The post-freeze suite assesses a frozen four-agent configuration and nine
single-edit mutants on four scenario families, with 30 seeds per family.
The original extended suite has 23 scenario families. A matched comparison
using 30 seeds per family showed that both suites detected the same nine
mutants with their full checks. See [integration assessment](docs/integration_assessment.md)
and the records in `results/integration/` and `results/comparison/`.

The revision experiments compare frozen, single-update, and joint-update
configurations under matched scenarios, seeds, and checks. They also
measure the additional mutant detections provided by checkpoints on the
same post-freeze executions. Per-run verdicts and witness traces are in
`results/revision/`. See [revision experiments](docs/revision_experiments.md).

## Independently sampled policy updates

Section 4.6 and Table 12 report five separate API requests for each of
the six single-policy tasks and three coordinated-update tasks. The
experiment used `gpt-4.1-mini-2025-04-14`. Each request supplied the task
requirements, policy interfaces, permitted code constructs, and baseline
code. The prompts omitted the evaluator, test scenarios, and assertions.
Each request started without conversation history or evaluation feedback.
Every candidate was evaluated without repair or selection, using 20
seeds per scenario family.

| Candidate type | Sampled | Rejected before execution | Passed the final suite |
|---|---:|---:|---:|
| Single-policy | 30 | 2 | 28 |
| Coordinated bundles | 15 | 0 | 15 |
| **Total** | **45** | **2** | **43** |

The two rejected candidates used an unsupported `is not` operator in the
quote-freshness task and a disallowed `min` call in the partial-fill task.
Both were rejected during restricted-code checks. The 43 accepted
candidates completed 5,900 development and 14,500 final-suite scenario
executions with no observed behavioral violations.

The [archived independent results](results/independent/) include the
configuration, prompts, responses, generated policies and bundles, and
per-candidate evaluation reports. Use
[`independent_samples.csv`](results/independent/independent_samples.csv)
for the 45 candidate-level outcomes in Table 12. The lower-level
`trials.csv` contains additional arm records from the common runner.
At a request budget of one, these records reuse the initial candidate.

The saved candidates can be evaluated again locally without API calls.
To generate a **new** sample using the same experimental settings, install
the `openai` Python package and configure `OPENAI_API_KEY`, then use a
separate output directory:

```sh
python -m pip install openai
python run_independent.py \
  --model gpt-4.1-mini-2025-04-14 \
  --trials 5 --seeds 20 \
  --out results/independent_new
```

This command issues new API requests. The generated policies and pass
counts may vary across samples.

## Repository contents

- `candidates/` contains the six archived policies and three derived bundles.
- `prompts/` contains task descriptions.
- `tool_source/` contains the simulator, evaluator, and API-study runner.
- `results/reported/`, `results/integration/`, `results/comparison/`, and
  `results/revision/` contain archived results and execution evidence.
- `results/independent/` contains the 45 independently sampled candidates
  and their evaluation records.
- `provenance.json` records the context of the original assistant-authored
  evaluation.
- `frozen_candidates_sha256.json` records the frozen candidate hashes.
- `MANIFEST_SHA256.json` records checksums for the original artifact files.
- `docs/RESULTS_VI.md` summarizes the original results and limitations in
  Vietnamese.

## Scope and limitations

The study evaluates small policy updates through fixed interfaces in one
simulator. Several tasks share the reconciliation interface, and the two
constructed interaction cases both involve the Market Data–Risk pair.
A passing configuration indicates that the selected checks observed no
violation on the tested executions. The sampling experiment covers one
model snapshot, nine tasks, and five requests per task. Scenario seeds
vary test inputs and schedules. Each API request supplies one candidate.

Future work includes feedback-guided repair and evaluation across
additional models, agent pairs, domains, and distributed settings.
