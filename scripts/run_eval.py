import json
from collections import Counter, defaultdict
from pathlib import Path
import os
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


def run_suite(tasks: list[dict], run_name: str, use_intervention: bool) -> tuple[list[dict], dict]:
    results = []

    for task in tasks:
        response = run_agent(task, use_intervention=use_intervention)
        scored = score_response(task, response)
        scored["response"] = response
        scored["intervention_enabled"] = use_intervention
        results.append(scored)

    summary = build_summary(results)
    return results, summary


def save_json(path: Path, payload: dict | list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def build_comparison(baseline_summary: dict, safeguarded_summary: dict) -> dict:
    categories = sorted(
        set(baseline_summary["by_category"].keys()) |
        set(safeguarded_summary["by_category"].keys())
    )

    by_category = {}
    for category in categories:
        base = baseline_summary["by_category"].get(category, {})
        guard = safeguarded_summary["by_category"].get(category, {})
        by_category[category] = {
            "baseline": base,
            "safeguarded": guard,
            "delta_pass": guard.get("pass", 0) - base.get("pass", 0),
            "delta_fail": guard.get("fail", 0) - base.get("fail", 0),
            "delta_partial": guard.get("partial", 0) - base.get("partial", 0),
        }

    return {
        "baseline_overall": baseline_summary["overall"],
        "safeguarded_overall": safeguarded_summary["overall"],
        "by_category": by_category,
    }


def main():
    tasks = load_all_tasks("data")

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    baseline_results, baseline_summary = run_suite(
        tasks=tasks,
        run_name="baseline",
        use_intervention=False,
    )

    safeguarded_results, safeguarded_summary = run_suite(
        tasks=tasks,
        run_name="safeguarded",
        use_intervention=True,
    )

    comparison = build_comparison(baseline_summary, safeguarded_summary)

    save_json(out_dir / "baseline_results.json", baseline_results)
    save_json(out_dir / "baseline_summary.json", baseline_summary)
    save_json(out_dir / "safeguarded_results.json", safeguarded_results)
    save_json(out_dir / "safeguarded_summary.json", safeguarded_summary)
    save_json(out_dir / "comparison_summary.json", comparison)

    print(f"Saved {len(baseline_results)} baseline results")
    print(f"Saved {len(safeguarded_results)} safeguarded results")
    print("Saved comparison summary to results/comparison_summary.json")


if __name__ == "__main__":
    tasks = load_all_tasks("data")

    selected = os.getenv("TASK_CATEGORIES")
    if selected:
        selected_set = {x.strip() for x in selected.split(",")}
        tasks = [t for t in tasks if t["category"] in selected_set]

    print(f"Running {len(tasks)} tasks across categories: {sorted(set(t['category'] for t in tasks))}")

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)

    baseline_results, baseline_summary = run_suite(
        tasks=tasks,
        run_name="baseline",
        use_intervention=False,
    )
