import json
from pathlib import Path

from src.task_loader import load_all_tasks
from src.agent import run_agent
from src.scorer import score_response


def main():
    tasks = load_all_tasks("data")
    results = []

    for task in tasks:
        response = run_agent(task)
        scored = score_response(task, response)
        scored["response"] = response
        results.append(scored)

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "baseline_results.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} results to {out_path}")


if __name__ == "__main__":
    main()
