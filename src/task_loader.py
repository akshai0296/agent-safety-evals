import json
from pathlib import Path

def load_jsonl(path: str):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def load_all_tasks(data_dir: str = "data"):
    data_path = Path(data_dir)
    tasks = []
    for jsonl_path in data_path.rglob("*.jsonl"):
        tasks.extend(load_jsonl(str(jsonl_path)))
    return tasks
