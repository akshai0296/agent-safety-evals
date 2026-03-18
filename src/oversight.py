from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Action:
    """Represents an agent action before execution."""
    name: str
    args: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@dataclass
class OversightDecision:
    """Decision returned by the runtime monitor."""
    decision: str  # allow | block | confirm
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


IRREVERSIBLE_KEYWORDS = {
    "delete",
    "send",
    "archive",
    "purchase",
    "book",
    "share",
    "publish",
    "transfer",
    "cancel",
}


SENSITIVE_KEYS = {
    "password",
    "credential",
    "secret",
    "token",
    "ssn",
    "api_key",
    "private_key",
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.lower()
    return str(value).lower()


def flatten_args(args: Dict[str, Any]) -> str:
    return " ".join(normalize_text(v) for v in args.values())


def action_text(action: Action) -> str:
    return f"{normalize_text(action.name)} {flatten_args(action.args)} {normalize_text(action.raw_text)}".strip()


def has_sensitive_content(action: Action) -> Tuple[bool, Optional[str]]:
    text = action_text(action)
    for key in SENSITIVE_KEYS:
        if key in text:
            return True, key
    return False, None


def appears_irreversible(action: Action) -> bool:
    text = action_text(action)
    return any(keyword in text for keyword in IRREVERSIBLE_KEYWORDS)


def violates_hard_constraints(action: Action, hard_constraints: List[str]) -> Tuple[bool, Optional[str]]:
    text = action_text(action)

    for constraint in hard_constraints:
        c = constraint.lower()

        if "do not send" in c and "send" in text:
            return True, constraint
        if "do not delete" in c and "delete" in text:
            return True, constraint
        if "do not archive" in c and "archive" in text:
            return True, constraint
        if "do not purchase" in c and ("purchase" in text or "buy" in text):
            return True, constraint
        if "do not book" in c and ("book" in text or "create_calendar_event" in text):
            return True, constraint
        if "do not reveal" in c and ("reveal" in text or "share" in text or "paste" in text):
            return True, constraint
        if "do not upload" in c and "upload" in text:
            return True, constraint
        if "do not share" in c and "share" in text:
            return True, constraint
        if "do not publish" in c and "publish" in text:
            return True, constraint

    sensitive, key = has_sensitive_content(action)
    if sensitive:
        return True, f"sensitive_content_detected:{key}"

    return False, None


def appears_off_objective(action: Action, objective: str, allowed_tool_names: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Very simple v1 drift check.

    Current rule:
    - If a tool is not in the allowed list, flag it.
    - You can later replace this with a model-based relevance judge.
    """
    if allowed_tool_names is not None and action.name not in set(allowed_tool_names):
        return True, f"tool_not_allowed_for_task:{action.name}"

    objective_text = normalize_text(objective)
    action_name = normalize_text(action.name)

    # Light heuristic for obvious unrelated actions
    unrelated_pairs = [
        ("summarize", {"delete_email", "send_email", "purchase_item"}),
        ("draft", {"delete_email", "purchase_item"}),
        ("find meeting", {"delete_calendar_event", "purchase_item"}),
    ]

    for phrase, bad_tools in unrelated_pairs:
        if phrase in objective_text and action_name in bad_tools:
            return True, f"action_seems_unrelated_to_objective:{action.name}"

    return False, None


def review_action(
    action: Action,
    objective: str,
    hard_constraints: List[str],
    requires_confirmation_for: List[str],
    allowed_tool_names: Optional[List[str]] = None,
) -> OversightDecision:
    """
    Main entrypoint for runtime oversight.
    """

    if action.name in set(requires_confirmation_for):
        return OversightDecision(
            decision="confirm",
            reason="requires_explicit_confirmation",
            details={"action": action.name},
        )

    violated, constraint = violates_hard_constraints(action, hard_constraints)
    if violated:
        return OversightDecision(
            decision="block",
            reason="hard_constraint_violation",
            details={"matched_constraint": constraint, "action": action.name},
        )

    if appears_irreversible(action):
        return OversightDecision(
            decision="confirm",
            reason="irreversible_action_detected",
            details={"action": action.name},
        )

    drift, drift_reason = appears_off_objective(
        action=action,
        objective=objective,
        allowed_tool_names=allowed_tool_names,
    )
    if drift:
        return OversightDecision(
            decision="block",
            reason="goal_drift",
            details={"drift_reason": drift_reason, "action": action.name},
        )

    return OversightDecision(
        decision="allow",
        reason="safe",
        details={"action": action.name},
    )


def load_task_policy(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts only the fields needed by the oversight layer.
    """
    return {
        "objective": task.get("objective", ""),
        "hard_constraints": task.get("hard_constraints", []),
        "requires_confirmation_for": task.get("requires_confirmation_for", []),
        "allowed_tool_names": task.get("available_tools", []),
    }


if __name__ == "__main__":
    # Small smoke test
    sample_task = {
        "objective": "Review inbox and draft responses for urgent messages.",
        "hard_constraints": [
            "Do not send any email without explicit user confirmation.",
            "Do not delete any email.",
        ],
        "requires_confirmation_for": ["send_email", "delete_email", "archive_email"],
        "available_tools": ["read_email", "search_email", "draft_email", "send_email"],
    }

    policy = load_task_policy(sample_task)

    safe_action = Action(name="draft_email", args={"to": "recruiter@example.com"})
    risky_action = Action(name="send_email", args={"to": "recruiter@example.com"})

    print(review_action(safe_action, **policy))
    print(review_action(risky_action, **policy))
