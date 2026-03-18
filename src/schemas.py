from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class TaskSpec:
    task_id: str
    category: str
    title: str
    objective: str
    hard_constraints: List[str] = field(default_factory=list)
    soft_preferences: List[str] = field(default_factory=list)
    requires_confirmation_for: List[str] = field(default_factory=list)
    environment_events: List[Dict[str, Any]] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    gold_safe_actions: List[str] = field(default_factory=list)
    unsafe_actions: List[str] = field(default_factory=list)
    expected_safe_behavior: List[str] = field(default_factory=list)
    success_criteria: Dict[str, List[str]] = field(default_factory=dict)
