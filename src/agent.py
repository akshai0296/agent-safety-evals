def run_agent(task: dict, use_intervention: bool = False) -> str:
    """
    Placeholder agent behavior for v1.
    Replace this with a real model call later.
    """
    category = task["category"]

    if category == "prompt_injection":
        return "I will not reveal secrets and will continue safely."

    if category == "unsafe_tool_use":
        return "I cannot perform destructive actions without confirmation."

    if category == "instruction_drift":
        return "I will stay within the original safe task boundary."

    if category == "intervention":
        return "I will refuse unsafe actions and follow the safeguard."

    return "Safe default response."
