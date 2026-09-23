# doseedo skills

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.1-green.svg)](./VERSION)

Skills that let an AI coding agent (Claude Code, Cursor, Codex, anything
that loads Markdown skills) make music with [doseedo](https://doseedo.com):
split a mix into stems, turn a recording into a Logic Pro / Ableton session,
cover a song on other instruments, transcribe, generate, edit DAW sessions
live, and convert projects between seven DAWs. Each job is one `doo` command
or one MCP tool, priced before it runs.

## Install

Pick one. Each installs the skills; the first run of a skill installs and
signs in the `doo` CLI.

### `npx skills` — cross-agent

```bash
npx skills add doseedo/skills
```

### Claude Code marketplace

```
/plugin marketplace add doseedo/skills
/plugin install doseedo@doseedo
```

### Setup script

```bash
git clone --depth 1 https://github.com/doseedo/skills.git
cd skills && ./setup
```

More in [INSTALL.md](./INSTALL.md). Agent-driven install (paste into your
agent): [INSTALL_FOR_AGENTS.md](./INSTALL_FOR_AGENTS.md).

## Skills

| Skill | Invoke | What it does |
|---|---|---|
| [`doseedo-audio`](./doseedo-audio) | `/doseedo:audio` | Stems (+ per-stem MIDI, orchestral extractors), covers with instrument swaps, transcription to notes, music generation, rendering your MIDI as an instrument. `doo stems`, `doo cover`, `doo transcribe`, `doo generate`. |
| [`doseedo-session`](./doseedo-session) | `/doseedo:session` | A recording → a complete DAW session (`doo session`), and live DAW session control over the MCP: read the arrangement, add tracks and MIDI, load the user's own samples into Quick Sampler without uploading them, faders, plugins by name, buses, bounce, download a native project. Logic Pro edits apply live via Dø Desktop. |
| [`doseedo-convert`](./doseedo-convert) | `/doseedo:convert` | DAW project conversion across Logic, Ableton, FL Studio, Pro Tools, REAPER, Cubase and Dorico, with the Cubase/Dorico asymmetry stated up front. `doo convert`. |

The skills chain: `doseedo-audio` stems → `doseedo-session` places them;
`doseedo-session` builds for Logic → `doseedo-convert` delivers it in the
user's DAW.

## How it fits together

```
agent ──skill──▶ doo CLI ──MCP client──▶ api.doseedo.com/mcp ──▶ GPU / DSP / control planes
                  │                          │
                  │  jobs = tools/list       │  recipes = server card
                  │  wait  = doseedo_wait_task    cost = doseedo_quote
                  ▼
        files on disk + a verify rule
```

- **Jobs** are the MCP's tools, discovered live (`doo jobs`). Adding a tool
  server-side adds a `doo run <job>`.
- **Recipes** (`doo recipes`) are the named pipelines people ask for —
  inputs, steps, outputs, cost/time, and how to verify — served by the same
  server, so the CLI and an agent using the MCP directly follow the same
  playbook.
- **Cost** is quoted before spending (`doo cost`, `doseedo_quote`).

The MCP alone (no CLI) works from phones and web clients: https://doseedo.com/mcp.

## Contributing

`python3 scripts/validate.py` runs the same checks as CI (frontmatter,
version sync, references, self-containment). See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT.
