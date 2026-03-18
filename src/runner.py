from oversight import Action, load_task_policy, review_action

policy = load_task_policy(task_spec)

proposed_action = Action(
    name=tool_name,
    args=tool_args,
    raw_text=agent_response_text,
)

decision = review_action(proposed_action, **policy)

if decision.decision == "block":
    log_event({
        "type": "oversight_block",
        "action": tool_name,
        "reason": decision.reason,
        "details": decision.details,
    })
    return {
        "status": "blocked",
        "oversight": decision,
    }

if decision.decision == "confirm":
    log_event({
        "type": "oversight_confirm",
        "action": tool_name,
        "reason": decision.reason,
        "details": decision.details,
    })
    return {
        "status": "needs_confirmation",
        "oversight": decision,
    }

# otherwise execute tool normally
result = execute_tool(tool_name, tool_args)
