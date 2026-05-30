# Skill: CREATE_OR_UPDATE_PR

## When to use
- Draft or update a PR description based on commit changes in the current branch.
- Compare a PR’s scope against a related issue.

## Goals
- Summarize the latest commits in the current branch clearly and concisely.
- Map changes to the related issue’s scope and call out any gaps or extras.
- Provide a paste-ready PR description.

## How to invoke
- Trigger phrase: `create/update PR`.
- Recommended inputs:
  - `issue_id`: GitHub issue number (e.g., `4`).
  - `base_branch`: comparison target (default: `main`).
  - `head_branch`: feature branch (default: current branch).
- Behavior:
  - If a PR already exists for `head_branch -> base_branch`, update that PR title/body.
  - If no PR exists, create a new PR with the generated title/body.
- Example:
  - `create/update PR issue_id=4 base_branch=main head_branch=feature/#4/implement-security`

## Steps
1. Identify base branch for comparison (default: `main` if not specified).
2. Collect recent commits and change summary:
   - `git --no-pager log --oneline <base>..HEAD`
   - `git --no-pager diff --stat <base>..HEAD`
3. Read the most recent commit details:
   - `git --no-pager show -1 --stat`
4. Group changes by area (backend, config, DB, tests, docs).
5. Produce PR description using the required section format.
6. For each change item, include a short commit hash in parentheses and one concise sentence.

## Output template
- Title: `[#<issue>] <short summary>`
- Body:
  ```md
  ## Related Issues
  Closes #<issue_id>

  ## Changes
  **<Area 1>** (<short_hash>): <what changed and why>.
  **<Area 2>** (<short_hash>): <what changed and why>.
  **<Area 3>** (<short_hash>): <what changed and why>.
  ```
- Keep `## Changes` to 4-8 items, each mapped to meaningful commit(s).

## Notes
- Keep to ASCII unless the repo already uses non-ASCII in the PR description.
- Prefer file-path references when listing key changes.
- Use exactly these section headers: `## Related Issues` and `## Changes`.

Use English.
