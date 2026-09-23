# Jobs (the MCP tool table, as `doo run` sees it)

`doo jobs` prints the live list; `doo jobs get <job>` the options. Flags are
the argument names with `_` → `-`. A local file argument fills `audio_key` /
`project_key` (uploaded for you); an https URL fills `audio_url` where a job
accepts one.

| job | options | async kind | result |
|---|---|---|---|
| `separate_stems` | `--models 6stem\|auto\|orchestra\|detect`, `--instruments "a,b"`, `--include-midi false`, `--export logic\|ableton` | `separate` | `stems{name: url}`, `midi{name: url}`, `session_url` |
| `cover_song` | `--instruments '{"piano":"electric_guitar"}'`, `--lyrics`, `--cover-noise-strength 0–1`, `--export logic\|ableton` | `cover` | `files[]`, `cover{duration, windowed, stems, instrument_swaps}` |
| `transcribe` | `--instrument`, `--tempo-bpm`, `--register`, `--polyphony solo\|poly\|section`, `--roster`, `--strikes` (file or `--audio-url`) | `transcribe` | `backend`, `result.notes[{pitch, onset, offset, velocity, confidence}]` |
| `generate_music` | `--prompt` (required), `--lyrics`, `--duration-seconds`, `--bpm`, `--time-signature`, `--seed` | `generate` | `files[]`, `duration` |
| `audio_to_session` | `--target logic\|ableton`, `--midi-stems`, `--chords`, `--simple`, `--stem-mode 6stem\|drumsep\|detect`, `--separate false`, `--tempo-map false`, `--crop-silence`, `--loops`, `--drum-sampler`, `--name` | `session` | `file` (zip), `summary` |
| `convert_project` | `--direction <src>2<dst>` (file = the project) | `convert` | `file` (zip) |
| `quote` | `--job`, `--args '{…}'` | — | `estimate{generation\|dsp\|convert}`, `affordable`, `account` |
| `account` | — | — | `tier`, `credits.generation/dsp{cap, used, remaining}` |
| `recipes` | `--name` | — | the recipe catalog |
| `wait_task` / `check_task` | `--job-id` (or `--task-id` + `--kind`) | — | status / result + `artifacts[]` |
| `get_upload_url` / `get_project_upload_url` | `--filename` | — | presigned `upload_url` + key (the CLI does this for you) |

**Without MCP or the CLI** — the same jobs over plain HTTP (`X-API-Key` header):

```
POST https://api.doseedo.com/api/jobs/uploads {"filename": "song.wav"}   → {upload_url, key, input_param}
PUT  <upload_url>  (the bytes, Content-Type from `headers`)
POST https://api.doseedo.com/api/jobs {"kind": "separate_stems", "input": {"audio_key": "<key>"}}   (+ Idempotency-Key)
GET  https://api.doseedo.com/api/jobs/<id>?wait=45    → repeat until status is succeeded|failed; download `artifacts[].url`
```

Every kind, its input schema and price: `GET /api/jobs/kinds`; OpenAPI: `GET /api/jobs/openapi.json`.
Errors are always `{error: {type, code, message, retryable}}` — retry only when `retryable` is true.

Session-control jobs (`list_sessions`, `get_session`, `edit_session`,
`edit_ops_reference`, `download_session`, `bounce_session`, `desktop_status`,
`list_plugins`, `add_audio_to_session`, `create_session`) are covered by the
**doseedo-session** skill.

## Budgets

- **generation** — GPU jobs: 1 credit ≙ one 30 s generation window.
  stems 1 (orchestra/detect up to 8), cover 4, generate ⌈windows⌉.
- **dsp** — CPU jobs: transcribe 1, audio_to_session 1 (+ the separation it
  runs on the GPU plane).
- **convert** — the monthly conversion allowance.

`doo cost <job> [--flags]` = `doseedo_quote`: an estimate from the planes'
own table plus the account's remaining balance. The gate is authoritative; a
refusal names the exact price. Failed jobs are refunded.

## Output shape (`--json`)

```json
{
  "recipe": "stems",
  "inputs": { "audio": "song.wav", "models": "6stem", "include_midi": true },
  "steps": [ { "tool": "doseedo_separate_stems", "task_id": "…", "result": { "status": "completed", "stems": { "vocals": "https://api.doseedo.com/…" } } } ],
  "files": [ { "name": "vocals", "path": "/abs/stems_song/vocals.wav", "bytes": 5312044, "url": "https://…" } ],
  "verify": "Every requested stem is a key in result.stems …"
}
```

Artifact URLs are downloadable without auth (the unguessable task id is the
capability); `?format=opus` on an audio URL gives a compressed copy.
