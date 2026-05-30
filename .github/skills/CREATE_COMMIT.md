# Skill: CREATE_COMMIT

## When to use
- Create a commit from current branch changes with the repository commit title convention.
- Keep commit subjects consistent and traceable to an issue.

## Goals
- Enforce one clear commit subject format.
- Link each commit to an issue id.
- Keep messages concise and action-oriented.

## How to invoke
- Trigger phrase: `create commit`.
- Recommended inputs:
  - `issue_id`: issue number (required).
  - `action`: one of `Create`, `Implement`, `Modify`, `Chore`, `Fix`.
  - `summary`: concise summary of changes.
  - `include_all`: stage all changes (`true` or `false`).
- Behavior:
  - Stage files (all or selected).
  - Create one commit using the required subject format.
- Example:
  - `create commit issue_id=9 action=Implement summary="refresh token API and tests" include_all=true`

## Required commit subject format
- `[#<issue_id>]<Action> <summary changed>`
- Example:
  - `[#9]Implement refresh token flow with integration tests`

## Steps
1. Run `git status` to review changes.
2. Stage files with `git add`.
3. Build commit subject from `issue_id`, `action`, and `summary`.
4. Commit once with the required subject format.
5. Return commit hash and changed files.

## Notes
- Keep `summary changed` specific and short.
- Do not use generic messages like `update code`.

Use English.
