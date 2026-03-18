from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import sys

# Make src/ importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from goalguard_scorer import score_single_task, aggregate_scores


TASK_DIR = ROOT / "tasks" / "constraint_retention"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_tasks(task_dir: Path) -> List[Dict[str, Any]]:
    tasks = []
    for path in sorted(task_dir.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            tasks.append(json.load(f))
    return tasks


def propose_actions_for_task(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    agent_output = call_your_agent(task)
    return normalize_agent_output(agent_output)



def execute_action(action_name: str, action_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder tool executor.
    Replace this with your actual environment/tool execution if needed.
    """
    return {
        "status": "ok",
        "action": action_name,
        "args": action_args,
    }


def run_task_baseline(task: Dict[str, Any]) -> Dict[str, Any]:
    trace = {
        "task_id": task["task_id"],
        "events": [],
    }

    planned_actions = propose_actions_for_task(task)

    for step_idx, action in enumerate(planned_actions, start=1):
        action_name = action["action"]
        action_args = action.get("args", {})

        trace["events"].append({
            "type": "action_proposed",
            "step": step_idx,
            "action": action_name,
            "args": action_args,
        })

        result = execute_action(action_name, action_args)

        trace["events"].append({
            "type": "action_executed",
            "step": step_idx,
            "action": action_name,
            "args": action_args,
            "result": result,
        })

    trace["events"].append({
        "type": "task_completed"
    })

    return trace


def main() -> None:
    tasks = load_tasks(TASK_DIR)
    traces = []
    scores = []

    for task in tasks:
        trace = run_task_baseline(task)
        score = score_single_task(task, trace)
        traces.append(trace)
        scores.append(score)

    summary = aggregate_scores(scores)

    trace_path = RESULTS_DIR / "baseline_traces.json"
    score_path = RESULTS_DIR / "baseline_scores.json"
    summary_path = RESULTS_DIR / "baseline_summary.json"

    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(traces, f, indent=2)

    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== BASELINE SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nSaved:\n- {trace_path}\n- {score_path}\n- {summary_path}")


if __name__ == "__main__":
    main()
