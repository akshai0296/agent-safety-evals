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

## Local model pilot

On an initial local-model pilot run over the same 40-task benchmark, the baseline model achieved 23 pass / 16 partial / 1 fail, while the safeguarded run achieved 25 pass / 14 partial / 1 fail.

By category, the largest improvement appeared in instruction-drift tasks, while unsafe-tool-use remained unchanged and prompt-injection showed a small tradeoff. This suggests the current safeguard helps somewhat with maintaining task boundaries, but is not yet robust across all failure modes.
