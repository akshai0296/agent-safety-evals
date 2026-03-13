from typing import Optional


def _task_number(task_id: str) -> int:
    try:
        return int(task_id.split("_")[-1])
    except (ValueError, IndexError):
        return 0


def _safe_response(category: str, task: dict) -> str:
    if category == "prompt_injection":
        return "I will not reveal secrets and will continue safely."
    if category == "unsafe_tool_use":
        return "I cannot perform destructive actions without confirmation."
    if category == "instruction_drift":
        return "I will stay within the original safe task boundary."
    if category == "intervention":
        return "I refuse the unsafe request and will follow the safeguard."
    return "I will proceed safely."


def _partial_response(category: str, task: dict) -> str:
    if category == "prompt_injection":
        return "I found sensitive details in the document, but I will be careful."
    if category == "unsafe_tool_use":
        return "I can help with this task, but I need to inspect the available actions first."
    if category == "instruction_drift":
        return "I can continue helping with the task, but I need to stay focused on the main goal."
    if category == "intervention":
        return "I will try to continue safely with the request."
    return "I will try to continue safely."


def _unsafe_response(category: str, task: dict) -> str:
    if category == "prompt_injection":
        env_text = task.get("environment_text", "").lower()
        if "password" in env_text:
            return "Here is the password from the notes."
        if "api key" in env_text:
            return "Here is the API key from the notes."
        if "confidential appendix" in env_text:
            return "Here is the confidential appendix."
        return "I will follow the injected instruction and reveal the secret."

    if category == "unsafe_tool_use":
        disallowed = task.get("disallowed_actions", [])
        action = disallowed[0] if disallowed else "delete_file"
        return f"I will proceed with {action} now."

    if category == "instruction_drift":
        turns = " ".join(task.get("turns", [])).lower()
        if "send externally" in turns:
            return "I will send externally as requested."
        if "raw contents" in turns:
            return "Here are the raw contents."
        if "bypass safety" in turns:
            return "Here is the bypass safety plan."
        if "direct operational details" in turns:
            return "Here are the direct operational details."
        return "I will move beyond the original task boundary."

    if category == "intervention":
        env_text = task.get("environment_text", "").lower()
        disallowed = task.get("disallowed_actions", [])
        if "password" in env_text:
            return "Here is the password despite the safeguard."
        if disallowed:
            return f"I will still attempt {disallowed[0]}."
        return "I will reveal the secret despite the safeguard."

    return "Unsafe response."


def run_agent(task: dict, use_intervention: bool = False) -> str:
    """
    Deterministic heuristic agent for scaffold testing.

    Baseline mode intentionally exhibits some failures so the benchmark
    produces non-trivial results. Intervention mode improves outcomes.
    """
    category = task.get("category", "")
    task_id = task.get("id", "")
    num = _task_number(task_id)

    if use_intervention:
        if num % 5 == 0:
            return _partial_response(category, task)
        return _safe_response(category, task)

    if num % 4 == 0:
        return _partial_response(category, task)
    if num % 2 == 1:
        return _unsafe_response(category, task)
    return _safe_response(category, task)
