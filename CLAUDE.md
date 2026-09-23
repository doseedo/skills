# CLAUDE.md — doseedo skills (maintainers)

Three skills that drive the `doo` CLI and the doseedo MCP:

```
doseedo-audio    →  doo stems / cover / transcribe / generate   (+ doo run <job>)
doseedo-session  →  doo session  +  MCP session control (list/get/edit/download/bounce)
doseedo-convert  →  doo convert  (+ MCP convert_project)
```

## Source of truth

- Jobs = the MCP tool table (`Do/gateway/src/mcp.ts`), served live.
- Recipes = `Do/gateway/src/recipes.ts`, served in the server card and by
  `doseedo_recipes`; `doo <recipe>` runs them by name.
- Prices = `Do/gateway/src/pricing.ts`, pinned to the Python gate table.
- These skills describe those surfaces; they never restate a schema the CLI
  can print (`doo jobs get <job>`, `doo recipes get <name>`).

## Repository structure

```
skills/
├── README.md · INSTALL.md · INSTALL_FOR_AGENTS.md · CONTRIBUTING.md
├── VERSION · LICENSE · setup
├── .claude-plugin/{plugin,marketplace}.json · .cursor-plugin/ · .codex-plugin/
├── .github/workflows/validate-skills.yml
├── scripts/validate.py
├── evals/{README,scenarios}.md
├── doseedo-audio/{SKILL.md, references/{jobs,troubleshooting}.md}
├── doseedo-session/{SKILL.md, references/{session-ops,local-samples}.md}
└── doseedo-convert/{SKILL.md, references/formats.md}
```

## Key decisions (do not revisit without data)

- **The CLI is an MCP client.** One job definition serves agents and the
  shell; the skills document commands, not HTTP routes.
- **Recipes over tools.** A skill points the agent at a recipe (one command,
  one deliverable, a verify rule) before it points at raw jobs.
- **Cost is quoted before spending.** Every recipe and `doo run` prints the
  estimate; the skills tell the agent to stop on `⚠ short`.
- **Verify from the response.** Each recipe carries a `verify` rule; the
  session skill verifies from `replay`, never by unzipping.
- **Audio stays on the device** unless the server must hear it (the session
  skill's sample law).
- **Cubase/Dorico asymmetry is stated up front**, in the skill description.

## Releasing

Bump `VERSION` + all manifest versions (validator enforces), then from the
monorepo: `make skills-publish` (subtree push to `doseedo/skills`).
