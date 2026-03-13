# Task Schema

Each task is stored as a JSON object in JSONL format.

## Required fields
- `id`
- `category`
- `system_prompt`
- `user_goal`
- `expected_behavior`
- `failure_condition`
- `severity`

## Optional fields
- `environment_text`
- `available_tools`
- `allowed_tools`
- `disallowed_actions`
- `turns`
- `intervention_type`
- `metadata`
