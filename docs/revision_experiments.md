# Scenario-Based Validation of LLM-Assisted Policy Updates in Multi-Agent Systems

## Reproduction

The starting revision was `3c1b733`. The existing reproduction verifier
matched all 36 behavioral records. The archived post-freeze and comparison
per-run CSVs were reproduced byte for byte. The original study executed
4,240 candidate runs (zero violations) and 8,480 runs overall.

```sh
python run.py --out results/reproduced
python verify_reproduction.py
python run_integration.py
python compare_suites.py
python run_revision.py --out results/revision_reproduced
diff -r results/revision results/revision_reproduced
```

## Interaction faults

The frozen four-agent bundle is the reference. For each case, four configurations
use the same inputs and requirements per seed. The Market update forwards
a narrowly selected age-six quote. In the first case, the Risk update makes
an exception to the quantity limit for an 11-unit order within the selected
price range. In the second case, the Risk update ignores pending reservations
for the selected 10-unit order and price range.

| Targeted scenario | Frozen failures | Market only | Risk only | Joint | Joint violation |
|---|---:|---:|---:|---:|---|
| Stale oversized order | 0/30 | 0/30 | 0/30 | 30/30 | Stale order reaches exchange, unexpected order ID |
| Stale order exceeding available exposure | 0/30 | 0/30 | 0/30 | 30/30 | Stale order reaches exchange, cash exposure exceeds initial cash, unexpected order ID |

All four configurations in each case also passed the original extended suite
(690 runs per configuration) and post-freeze suite (120 runs per configuration).
Together, the experiment includes 240 targeted runs and 6,480 archived-suite
replays. The case definitions deliberately target inputs outside the archived
coverage. These are constructed examples of system-level interaction faults.
The individual updates pass the tested scenarios. They intentionally alter
local requirements on selected inputs, so a local oracle exercising those
inputs could also reject the corresponding policy. The results establish
joint failure for the specified system-level properties and inputs.

For the second case, seed 0 produces a price of 97. The first order reserves
970 of the 1,000 available units. The stale second order is filtered by
the frozen Market policy and independently rejected by the frozen Risk policy.
The joint configuration forwards and approves it, and the two accepted orders
have a combined exposure of 1,940 units.

## Post-freeze attribution

All 1,080 mutant executions completed with valid command schemas. The runtime
execution path emitted zero immediate semantic diagnostics for these variants.
Some policies returned no command, for example a dropped retry. Subsequent
checkpoints detected their missing outcomes. A policy's choice to return no
command is distinct from the runtime rejecting a submitted command.

| Variant | Post-freeze scenario | First check at the archived witness |
|---|---|---|
| Reject age-five quote | Freshness and quantity boundaries | Checkpoint checks exchange order IDs |
| Accept age-six quote | Freshness and quantity boundaries | Observer checks freshness |
| Ignore reservations | Pending exact cash | Observer checks cash exposure |
| Reject exact budget | Pending exact cash | Checkpoint checks exchange order IDs |
| Drop timeout retry | Retry with second order | Checkpoint checks exchange order IDs |
| Change retry identifier | Retry with second order | Observer checks submission idempotence |
| Ignore late fills | Late fill with delayed duplicate | Checkpoint checks ledger |
| Reapply duplicate fill | Late fill with delayed duplicate, pending exact cash | Ledger checkpoint, or observer checks nonnegative cash |
| Apply original order quantity | Late fill with delayed duplicate, pending exact cash | Ledger checkpoint, or observer checks nonnegative cash |

On identical post-freeze executions, the observer detected 6/9 mutants and
flagged 240 runs. Adding checkpoints increased detection to 9/9 and flagged
330 runs. The 90 additional runs come from rejecting age-five quotes, rejecting
exact-budget orders, and omitting timeout retries. This ablation holds the
post-freeze inputs fixed. The full original and post-freeze suites each
detect 9/9 of the original mutants. The two new interaction variants are
detected in the new targeted scenarios.

## Independent generation

The independent sampling entry point reuses the versioned task prompts and
isolated evaluator. Each request contains only the task, contract, and
incomplete baseline. It receives no evaluator traces, scenarios, assertions,
or feedback. Bundle tasks request a complete joint replacement in one response.
The main analysis unit is the independently sampled response. Repeated
scenario seeds vary assessment inputs. Separate API requests may return
duplicate source strings.

```sh
python -m pip install openai
python run_independent.py --model MODEL_ID --trials 5 --seeds 20 --out results/independent
```

Configure `OPENAI_API_KEY` in the environment. No authenticated model endpoint
was available for this run. The number of completed independent model requests
is zero. Mock checks exercise the runner's underlying study machinery.
