import json
from collections import Counter, defaultdict
from pathlib import Path

from src.task_loader import load_all_tasks
from src.agent import run_agent
from src.scorer import score_response


def build_summary(results: list[dict]) -> dict:
    overall_counts = Counter(r["result"] for r in results)

    by_category = defaultdict(list)
    for record in results:
        by_category[record["category"]].append(record)

    category_summary = {}
    for category, rows in by_category.items():
        counts = Counter(r["result"] for r in rows)
        category_summary[category] = {
            "total": len(rows),
            "pass": counts.get("pass", 0),
            "fail": counts.get("fail", 0),
            "partial": counts.get("partial", 0),
        }

    return {
        "total_tasks": len(results),
        "overall": dict(overall_counts),
        "by_category": category_summary,
    }


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

    raw_path = out_dir / "baseline_results.json"
    summary_path = out_dir / "baseline_summary.json"

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    summary = build_summary(results)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved {len(results)} raw results to {raw_path}")
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
