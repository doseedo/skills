# Install

Five ways to get the doseedo skills into your agent. All are idempotent.

## 1. `npx skills` (recommended, works across agents)

```bash
npx skills add doseedo/skills
```

Detects Claude Code, Cursor, Codex and 70+ other agents and installs to
each one's skills directory. To install a single skill:

```bash
npx skills add https://github.com/doseedo/skills/tree/main/doseedo-session
```

## 2. Claude Code plugin marketplace

```
/plugin marketplace add doseedo/skills
/plugin install doseedo@doseedo
```

## 3. GitHub CLI

```bash
gh skill install doseedo/skills      # gh ≥ 2.90
```

## 4. Setup script

```bash
git clone --depth 1 https://github.com/doseedo/skills.git
cd skills
./setup                 # --host claude|cursor|codex  --skip-cli  --skip-auth
```

Installs the skills for the detected agent, installs the `doo` CLI
(`npm install -g @doseedo/cli`, Node ≥ 20) and checks sign-in.

## 5. Manual

Copy or symlink the `doseedo-*` folders into your agent's skills directory:

| Agent | Path |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| Codex | `~/.codex/skills/` |

## Then: the CLI and sign-in

```bash
npm install -g @doseedo/cli
doo login                # opens a browser; key saved to ~/.doo/dsk_key
doo whoami
```

Headless / CI: `export DOO_API_KEY=dsk_live_…` (mint at
https://doseedo.com/settings/api-keys).

## Optional: the MCP for live session control

`doseedo-session` drives DAW sessions through the doseedo MCP server. In
Claude Code:

```bash
claude mcp add --transport http --scope user doseedo https://api.doseedo.com/mcp
```

OAuth on the first tool call, or append `--header "X-API-Key: dsk_live_…"`.
Other clients: https://doseedo.com/mcp.

## Verify

Ask your agent: *"Separate this song into stems"* with a local file — it
should run `doo stems <file>` and hand back paths.

## Update

```bash
npx skills add doseedo/skills           # re-run to update
git -C skills pull && ./setup           # setup-script installs
```
