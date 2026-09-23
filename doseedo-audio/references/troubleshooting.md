# Troubleshooting

| Symptom | Meaning | Do |
|---|---|---|
| exit 3, "Not signed in" / "API key rejected" | no key, or the key was revoked | ask the user to run `doo login`; or set `DOO_API_KEY` |
| exit 1, "has no option --x" | flag typo; the message lists the real ones | fix the flag (`doo jobs get <job>`) |
| exit 2, HTTP 429 | daily or monthly allowance reached | tell the user the reset time from the message; https://doseedo.com/plans |
| exit 2, HTTP 402 | the job needs a paid plan | say so; don't retry |
| `⚠ generation: need 4, have 2` before submit | the quote says the account is short | stop and tell the user; the gate would refuse anyway |
| "timed out … rejoin with doo wait" | the CLI's wait deadline passed, the job may still be running | `doo wait <task_id> --kind <kind>` |
| a stem is missing from `stems` | the model heard none of that instrument | report it; try `--models auto` or `orchestra --instruments …` only if the user says the instrument is really there |
| `result.cover.instrument_swaps` shows a swap not applied | the stem to swap wasn't found / the target isn't a supported instrument | report the reason from that field; ask before re-running (4 credits) |
| transcribe returns 0 notes | polyphonic mix, or the wrong instrument hint | run `doo stems` first and transcribe the stem; pass `--instrument` |
| first call after idle is slow (~1 min) | the GPU plane scales to zero and cold-starts | normal; the CLI waits |
| "no such file" with a path containing spaces | shell quoting | quote the path |

## Bash tool timeouts

Coding agents' shell tools often default to a 2-minute timeout. stems ~2 min,
cover 3–8 min, generate 1–3 min. Either raise the tool timeout to 10 minutes
for the call, or:

```bash
doo cover song.wav --no-wait --json      # → {"task_id": "...", "kind": "cover"}
doo wait <task_id> --kind cover --out cover_song
```

## What the CLI does under the hood

The CLI is an MCP client of `https://api.doseedo.com/mcp`: jobs are the
server's tools, recipes come from its public server card, waiting is the
server-side poller (`doseedo_wait_task`, ~45 s per round trip), prices are
`doseedo_quote`. If a job exists on the MCP it exists as `doo run <job>`.
Details: https://doseedo.com/mcp
