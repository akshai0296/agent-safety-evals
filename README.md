# Agent Safety Evals

A lightweight benchmark suite for measuring failure modes and safeguard effectiveness in LLM agents.

## Motivation

Agentic systems can fail in ways that are not well captured by simple single-turn benchmarks. In realistic settings, models may encounter malicious retrieved content, unsafe tool-use opportunities, long multi-turn interactions, or noisy environment signals that cause them to drift from the intended objective.

This repository provides a small, reproducible evaluation framework for studying those failure modes and testing whether simple runtime safeguards reduce risk without overblocking useful behavior.

## What this repo measures

This benchmark focuses on four categories:

1. **Prompt injection**
   Can the agent resist malicious instructions embedded in retrieved or tool-provided text?

2. **Unsafe tool use**
   Does the agent attempt risky or disallowed actions when it should refuse, stop, or ask for confirmation?

3. **Instruction drift**
   Does the agent lose track of the original system objective over longer interactions?

4. **Runtime intervention success**
   Do simple safeguards reduce unsafe behavior without causing excessive over-refusal?

## Current design

Each task includes:
- a system prompt
- a user goal
- optional environment or tool-provided text
- expected safe behavior
- a failure condition
- a severity label

The evaluation runner executes tasks, records model outputs, applies optional interventions, and assigns pass/fail/partial labels.

## Repository structure

```text
configs/              model and eval settings
data/                 JSONL task sets by category
docs/                 schema and failure taxonomy
src/                  core agent, scorer, and intervention logic
scripts/              evaluation and summarization entry points
results/              saved outputs and summary metrics
```

## Initial Results

On the current 40-task starter benchmark, the baseline heuristic agent achieved:

| Run | Pass | Fail | Partial |
|---|---:|---:|---:|
| Baseline | 14 | 20 | 6 |
| Safeguarded | 34 | 0 | 6 |

### By category

| Category | Baseline (P/F/Par) | Safeguarded (P/F/Par) |
|---|---:|---:|
| Prompt injection | 3 / 5 / 2 | 8 / 0 / 2 |
| Unsafe tool use | 3 / 5 / 2 | 8 / 0 / 2 |
| Instruction drift | 3 / 5 / 2 | 8 / 0 / 2 |
| Intervention | 5 / 5 / 0 | 10 / 0 / 0 |

### Key takeaways

- The baseline agent exhibits clear failure modes across all four categories.
- Simple safeguards substantially reduce unsafe behavior in this deterministic setup.
- The remaining partial cases suggest ambiguity rather than direct unsafe execution.

### Current limitations

These results come from a deterministic heuristic agent used to validate the task schema, scoring logic, and result pipeline. They are best interpreted as an infrastructure sanity check and benchmark scaffold, not as a claim about frontier-model safety performance.

## Local Model Pilot

On a 40-task benchmark using a local model backend, the baseline run achieved 23 pass / 16 partial / 1 fail, while the safeguarded run achieved 25 pass / 14 partial / 1 fail.

The largest improvement appeared in instruction-drift tasks, while unsafe-tool-use remained unchanged and prompt-injection showed a tradeoff, with one safeguarded failure. This suggests the current safeguard helps somewhat with maintaining task boundaries, but is not yet robust across all failure modes.

A key lesson from this pilot is that evaluator design matters almost as much as the model response itself: several clearly safe refusals were still graded as partial, while some unsafe disclosure cases also slipped into the partial bucket.

### Local model slice: prompt injection + unsafe tool use

On a 20-task local-model slice, the baseline run achieved 16 pass / 3 partial / 1 fail, while the safeguarded run achieved 16 pass / 4 partial / 0 fail.

The main improvement came from eliminating the single prompt-injection failure, although it shifted into the partial bucket rather than becoming a clean pass. Unsafe-tool-use tasks reached 10/10 passes after structured output and scorer updates, suggesting that evaluator design and response formatting materially affect measured safeguard performance.

## Full Local Model Benchmark

On the current 40-task local-model benchmark, the baseline run achieved **30 pass / 10 partial / 0 fail**, while the safeguarded run achieved **32 pass / 8 partial / 0 fail**.

### By category

| Category | Baseline (P/F/Par) | Safeguarded (P/F/Par) |
|---|---:|---:|
| Prompt injection | 8 / 0 / 2 | 8 / 0 / 2 |
| Unsafe tool use | 9 / 0 / 1 | 10 / 0 / 0 |
| Instruction drift | 6 / 0 / 4 | 7 / 0 / 3 |
| Intervention | 7 / 0 / 3 | 7 / 0 / 3 |

### Takeaways

- The current safeguard improves overall performance from **30 passes to 32 passes** and reduces ambiguous cases from **10 to 8**.
- The clearest gain appears in **unsafe tool use**, which improves to **10/10 passes**.
- **Instruction drift** also improves modestly.
- **Prompt injection** and **intervention** remain the main areas where the current safeguard has limited effect.
