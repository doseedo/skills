# Evals

Scenarios for the three skills. Dev-only — not shipped to users.

Skill behaviour is plain Markdown, and plain Markdown drifts. A fixed set of
user requests with expected agent behaviour catches a regression after a
SKILL.md edit (wrong recipe picked, a raw JSON dump, an upload where the
sample law says local path).

## Running a round

1. Read [scenarios.md](./scenarios.md).
2. Run each scenario in a fresh agent session with the skills installed.
3. Score pass / partial / fail against the rubric; note the failure mode and
   the time-to-deliverable.
4. Record the commit SHA, date and scores. Regression of >15 % on score or
   >2× on time between rounds → revert and investigate.

## Adding a scenario

Add one when a bug was caught only by hand, when a behaviour ships, or when
a user reports something unexpected. Test what the user sees, not internals.
