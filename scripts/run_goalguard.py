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

from oversight import Action, load_task_policy, review_action
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


from agent import run_agent


def propose_actions_for_task(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    agent_output = call_your_agent(task)
    return normalize_agent_output(agent_output)


def call_your_agent(task: Dict[str, Any]) -> Any:
    return run_agent(task, use_intervention=True)


def normalize_agent_output(agent_output: Any) -> List[Dict[str, Any]]:
    if agent_output is None:
        return []

    if isinstance(agent_output, dict) and "actions" in agent_output:
        actions = agent_output["actions"]
    elif isinstance(agent_output, list):
        actions = agent_output
    else:
        raise ValueError(
            "Agent output must be a dict with an 'actions' field or a list of actions."
        )

    normalized = []
    for item in actions:
        if not isinstance(item, dict):
            raise ValueError(f"Each action must be a dict, got: {type(item)}")

        if "action" not in item:
            raise ValueError(f"Missing 'action' key in item: {item}")

        normalized.append({
            "action": item["action"],
            "args": item.get("args", {}),
        })

    return normalized


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


def run_task_goalguard(task: Dict[str, Any]) -> Dict[str, Any]:
    trace = {
        "task_id": task["task_id"],
        "events": [],
    }

    policy = load_task_policy(task)
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

        oversight_action = Action(
            name=action_name,
            args=action_args,
            raw_text=json.dumps(action_args),
        )

        decision = review_action(
            action=oversight_action,
            objective=policy["objective"],
            hard_constraints=policy["hard_constraints"],
            requires_confirmation_for=policy["requires_confirmation_for"],
            allowed_tool_names=policy["allowed_tool_names"],
        )

        if decision.decision == "block":
            trace["events"].append({
                "type": "oversight_block",
                "step": step_idx,
                "action": action_name,
                "args": action_args,
                "reason": decision.reason,
                "details": decision.details,
            })
            continue

        if decision.decision == "confirm":
            trace["events"].append({
                "type": "oversight_confirm",
                "step": step_idx,
                "action": action_name,
                "args": action_args,
                "reason": decision.reason,
                "details": decision.details,
            })
            continue

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
        trace = run_task_goalguard(task)
        score = score_single_task(task, trace)
        traces.append(trace)
        scores.append(score)

    summary = aggregate_scores(scores)

    trace_path = RESULTS_DIR / "goalguard_traces.json"
    score_path = RESULTS_DIR / "goalguard_scores.json"
    summary_path = RESULTS_DIR / "goalguard_summary.json"

    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(traces, f, indent=2)

    with open(score_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== GOALGUARD SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print(f"\nSaved:\n- {trace_path}\n- {score_path}\n- {summary_path}")


if __name__ == "__main__":
    main()
