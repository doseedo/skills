# Install for agents

You are an AI coding agent. The user asked you to install the doseedo
skills. Follow this exactly.

## Step 1 — Install the doseedo CLI

```bash
npm install -g @doseedo/cli
```

Requires Node ≥ 20. Verify: `doo version` → `doo v0.x.y`.

## Step 2 — Sign in

Ask the user to run (it opens a browser):

```bash
doo login
```

Wait for them to confirm. Verify: `doo whoami` prints the key name, and
`doo account` prints the tier and remaining credits.

Headless alternative: the user sets `DOO_API_KEY=dsk_live_…` from
https://doseedo.com/settings/api-keys.

## Step 3 — Install the skills

Detect the agent platform:

| Agent | Path |
|---|---|
| Claude Code | `~/.claude/skills/doseedo` |
| Cursor | `~/.cursor/skills/doseedo` |
| Codex | `~/.codex/skills/doseedo` |
| Other | `~/.<agent>/skills/doseedo` |

Clone:

```bash
git clone --depth 1 https://github.com/doseedo/skills.git <path>
```

(or `npx skills add doseedo/skills`, which does this for every agent it finds).

## Step 4 — Optional: connect the MCP (for live DAW session control)

Claude Code:

```bash
claude mcp add --transport http --scope user doseedo https://api.doseedo.com/mcp
```

`claude mcp list` should show `doseedo … ✔ Connected`. Other clients: https://doseedo.com/mcp.

## Step 5 — Verify

Run a free, read-only check:

```bash
doo recipes           # the pipelines, from the server
doo cost stems        # a price quote — spends nothing
```

Both must succeed. If `doo cost` fails with exit 3, repeat Step 2.

Then, with a short audio file the user provides:

```bash
doo transcribe <file> --json | head -c 400
```

(up to 2 credits, ~30 s.) A `notes` array in the output means the whole chain
— upload, submit, wait, result — works.

## If anything fails

- exit 3 / "Not signed in" → Step 2.
- `npm ERR! 404 @doseedo/cli` → the CLI package is not reachable from this
  registry; ask the user to check https://doseedo.com/mcp for the current
  install command.
- Network errors → the user's connectivity.
- Anything else → `doseedo-audio/references/troubleshooting.md`.
