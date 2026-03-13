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
