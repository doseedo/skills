# Contributing

The source of these skills lives in the doseedo monorepo (`Do/skills/`) and
is published here with a subtree push. Pull requests against this repo are
welcome; they are ported back.

## Checklist

- `python3 scripts/validate.py` passes.
- The skill's `description` says **when to use it** ("Use when: …") and
  **when not to** ("NOT for: …") — that is what an agent matches on.
- Every command in a SKILL.md exists in the `doo` CLI or the MCP tool table
  (`doo jobs`, `doo recipes`). Don't document a flag from memory.
- New reference files are linked from the SKILL.md; no `../` paths.
- Bump `VERSION` and every manifest's `version` together (the validator
  enforces it).
- Add an eval scenario under `evals/` for a new behaviour.
