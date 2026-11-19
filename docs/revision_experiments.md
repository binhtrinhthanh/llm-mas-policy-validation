# Scenario-Based Validation of LLM-Assisted Policy Updates in Multi-Agent Systems

## Reproduction

Use Linux and Python 3.10 or later. The reported replays were checked
with Python 3.12.14 on Linux x86_64. The commands below use the
standard library and require no API key.

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

The reproduction verifier matched all 36 behavioral records from the
original study. The archived post-freeze and suite-comparison per-run
CSVs matched their reproduced outputs byte for byte. The original
evaluation comprised 4,240 candidate runs with zero observed violations
and 8,480 runs overall, including the baselines.

## Interaction faults

The frozen four-agent bundle serves as the reference configuration.
For each case, the frozen, Market-only, Risk-only, and joint
configurations use the same scenario, seeds, and checks. The Market
update forwards a selected age-six quote. In the first case, the
Risk update relaxes the quantity limit for an 11-unit order in the
selected price range. In the second case, the Risk update ignores
pending reservations for a selected 10-unit order.

| Targeted scenario | Frozen | Market only | Risk only | Joint | Joint violation |
|---|---:|---:|---:|---:|---|
| Stale oversized order | 0/30 | 0/30 | 0/30 | 30/30 | A stale order reaches the exchange with an unexpected order ID. |
| Stale order exceeding available cash | 0/30 | 0/30 | 0/30 | 30/30 | A stale order reaches the exchange, committed exposure exceeds initial cash, and an unexpected order ID appears. |

The table reports violating executions. All four configurations in
each case also passed the original extended suite (690 runs per
configuration) and the post-freeze suite (120 runs per configuration).
The experiment therefore includes 240 targeted runs and 6,480
archived-suite replays.

Both cases were constructed for the Market Data–Risk pair and exercise
input combinations outside the archived suites. A passing single-update
configuration indicates that the selected system-level checks observed
no violation on the tested executions. A local policy test exercising
the relevant inputs could still identify the underlying deviations.

In the second case, seed 0 produces a price of 97. The first order
reserves 970 of the initial 1,000 units. The frozen Market policy
filters the stale second quote. If that quote is forwarded, the frozen
Risk policy rejects the resulting order. With both replacements active,
the system forwards and approves the second order, bringing the
committed exposure to 1,940 units.

## Post-freeze attribution

All nine mutants passed the restricted-code checks, and all 1,080
mutant executions completed with valid command schemas. Command
handlers recorded zero runtime diagnostics in these executions.
A scenario checkpoint can detect a missing outcome, such as an expected
exchange order after a timeout retry, even when the policy returns no
command.

Each mutant was evaluated in 120 runs. The table reports the number
of executions with a violation flagged by each check configuration.
A mutant counts as detected if at least one execution is flagged.

| Mutant | Runtime diagnostics | Observer only | Observer + checkpoints |
|---|---:|---:|---:|
| Reject age-five quote | 0 | 0 | 30 |
| Accept age-six quote | 0 | 30 | 30 |
| Ignore reservations | 0 | 30 | 30 |
| Reject exact-budget order | 0 | 0 | 30 |
| Drop timeout retry | 0 | 0 | 30 |
| Change retry identifier | 0 | 30 | 30 |
| Ignore late fills | 0 | 30 | 30 |
| Reapply duplicate fill | 0 | 60 | 60 |
| Apply original order quantity | 0 | 60 | 60 |
| **Flagged executions** | **0** | **240** | **330** |
| **Mutants detected** | **0/9** | **6/9** | **9/9** |

On the same executions, adding checkpoints detected three additional
mutants and flagged 90 additional runs. These detections concerned
rejection of age-five quotes, rejection of exact-budget orders, and
omission of timeout retries. The first check to flag a violation can
vary by trace. For example, a ledger checkpoint can report a discrepancy
before the observer reaches its final ledger check.

The original extended and post-freeze suites each detected all nine
single-edit mutants with their full checks. Per-run verdicts and trace
witnesses are available in [`results/revision/`](../results/revision/).

## Independently sampled policy updates

The experiment used `gpt-4.1-mini-2025-04-14`, with five separate
requests for each of six single-policy tasks and three coordinated-update
tasks. Each request supplied the task requirements, policy interfaces,
permitted code constructs, and baseline code. Prompts omitted the
evaluator, test scenarios, and assertions. Each request began without
conversation history or evaluation feedback. Each coordinated-update
request returned a complete bundle.

All 45 candidates were evaluated without repair or selection, using
20 seeds per scenario family in the development and final suites.
Separate requests could return identical source code.

| Candidate type | Sampled | Rejected before execution | Passed the final suite |
|---|---:|---:|---:|
| Single-policy candidates | 30 | 2 | 28 |
| Coordinated bundles | 15 | 0 | 15 |
| **Total** | **45** | **2** | **43** |

The quote-freshness candidate that used `is not` was rejected because
the operator is outside the permitted syntax. The partial-fill candidate
that called `min` was rejected because that function is outside the
permitted set of calls. Both rejections occurred before scenario
execution. The remaining 43 candidates completed 5,900 development
runs and 14,500 final-suite runs with no observed behavioral violations.

The [archived results](../results/independent/) include the configuration,
prompts, responses, generated policies and bundles, and per-candidate
evaluation reports. The
[`independent_samples.csv`](../results/independent/independent_samples.csv)
file contains the 45 candidate-level outcomes reported in Table 12.
The saved candidates can be evaluated again locally without API calls.

### Generate a new sample

To issue new API requests with the reported settings, install the
`openai` Python package, configure `OPENAI_API_KEY`, and run:

```sh
python -m pip install openai
python run_independent.py \
  --model gpt-4.1-mini-2025-04-14 \
  --trials 5 --seeds 20 \
  --out results/independent_new
```

A new sample may produce different policies and pass counts. The
published results are stored under `results/independent/`.
