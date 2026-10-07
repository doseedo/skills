# Jobs (the MCP tool table, as `doo run` sees it)

`doo jobs` prints the live list; `doo jobs get <job>` the options. Flags are
the argument names with `_` → `-`. A local file argument fills `audio_key` /
`project_key` (uploaded for you); an https URL fills `audio_url` where a job
accepts one.

| job | options | async kind | result |
|---|---|---|---|
| `separate_stems` | `--models 6stem\|auto\|orchestra\|detect`, `--instruments "a,b"`, `--include-midi false`, `--stems-only`, `--drum-split`, `--guitar-split auto\|2–4`, `--export logic\|ableton`, `--session-id` + `--parent-track-id` (register the stems into a session); file or `--audio-url` (a result URL works) | `separate` | `stems{name: url}`, `midi{name: url}`, `drum_substems{kick, snare, …}`, `vocals_lyrics`, `vocals_notes`, `session_url`, `session_tracks`, `models_effective`, `other_classification`, `guitar_split` |
| `cover_song` | `--instruments '{"piano":"electric_guitar"}'`, `--lyrics`, `--genre "bossa nova"`, `--cover-noise-strength 0–1`, `--swap-cns 0–1`, `--regen all\|<stems>`, `--labels '{"other":"trumpet"}'`, `--midi-only`, `--timbre-preset`, `--style-key ingest/…`, `--structure-key ingest/…`, `--drum-split`, `--guitar-split auto\|2–4`, `--seed`, `--export logic\|ableton`; file or `--audio-url` | `cover` | `files[]`, `cover{duration, windowed, stems, instrument_swaps, genre, guitar_split}`, `seed`, `chain` |
| `transcribe` | `--instrument`, `--tempo-bpm`, `--register`, `--polyphony solo\|poly\|section`, `--roster`, `--strikes`, `--want notes\|f0\|notes,f0` (file or `--audio-url`) | `transcribe` | `backend`, `result.notes[{pitch, onset, offset, velocity, confidence}]`, `result.f0` |
| `generate_music` | `--prompt` (required), `--lyrics`, `--duration-seconds`, `--bpm` (caption hint), `--time-signature` (hint), `--seed` — no key, no MIDI (MIDI: `render_midi`) | `generate` | `files[]`, `duration`, `seed`, `best_of_n`, `chain` |
| `render_midi` | `--notes '[{"pitch":62,"start_beats":0,"duration_beats":1,"velocity":100}, …]'` OR `--midi-url <.mid URL>` OR `--session-id` + `--track-id`; `--instrument` (required; ids: `/api/instruments`), `--bpm` (required), `--time-signature`, `--duration-seconds` (default last note + 2 s), `--takes 1–4`, `--seed`, `--voice-split` (chords), `--refine light\|shred`, `--timbre-preset`, `--timbre-audio-url`, `--dynamics mf` | `render` | `takes[{url, rank, score}]` best-first, `seed`, `duration`, `voices[]`, `refine.raw_url`, `chain` |
| `audio_to_session` | `--target logic\|ableton`, `--midi-stems`, `--keep-stem-audio false`, `--chords`, `--key false`, `--markers false`, `--simple`, `--stem-mode auto\|6stem\|drumsep\|sections\|orchestra\|detect` (default auto; orchestra/detect need `--simple`), `--instruments`, `--quantize-midi grid\|score`, `--drum-substems`, `--drum-midi-split`, `--guitar-split auto\|0\|2–4`, `--retune false`, `--dereverb`, `--separate false`, `--tempo-map false`, `--crop-silence`, `--loops`, `--drum-sampler`, `--name`; file or `--audio-url` | `session` | `file` (zip), `summary` |
| `analyze_song` | file or `--audio-url` | — (sync: the result is in the reply) | `key`, `bpm`, `tempo_map`, `meter`, `beats_per_bar`, `downbeats`, `sections`, `chords`, `dynamics` |
| `detect_chords` | file or `--audio-url`, `--deep false` (CPU detector) | — (sync) | `chord_spans[{chord, start, end, start_beat, end_beat, confidence}]`, `chords{beat: symbol}`, `bpm`, `beat_map` |
| `beat_grid` | file or `--audio-url` | — (sync) | `bpm`, `beats[]`, `downbeats[]`, `beats_per_bar`, `beat_map` |
| `analyze_midi` | `--notes '[…]'` + `--bpm`, or `--midi-url`; `--mode midi\|chord`, `--beats-per-segment`, `--min-seg-beats` | — (sync) | `sonorities[]` or `chords[]`, `cover`, `cells`, `compression` |
| `convert_project` | `--direction <src>2<dst>` (file = the project) | `convert` | `file` (zip) |
| `quote` | `--job`, `--args '{…}'` (render_midi: notes + bpm or duration_seconds, voices, takes) | — | `estimate{generation\|dsp}`, `affordable`, `account` |
| `account` | — | — | `tier`, `credits.generation.monthly{cap, used, remaining}` (the ONE pool), `credits.generation.packs.balance`, `storage` |
| `recipes` | `--name` | — | the recipe catalog |
| `wait_task` / `check_task` | `--job-id` (or `--task-id` + `--kind`) | — | status / result + `artifacts[]` |
| `list_jobs` / `cancel_job` | `--limit --kind --status --session-id` / `--job-id` | — | your jobs, newest first (with `artifact_names`) / the canceled job (what a cancel stops + refunds is per kind — see the tool description) |
| `get_upload_url` / `get_project_upload_url` | `--filename` | — | presigned `upload_url` + key (the CLI does this for you) |

**Without MCP or the CLI** — the same jobs over plain HTTP (`X-API-Key` header):

```
POST https://api.doseedo.com/api/jobs/uploads {"filename": "song.wav"}   → {upload_url, key, input_param}
PUT  <upload_url>  (the bytes, Content-Type from `headers`)
POST https://api.doseedo.com/api/jobs {"kind": "separate_stems", "input": {"audio_key": "<key>"}}   (+ Idempotency-Key)
GET  https://api.doseedo.com/api/jobs/<id>?wait=45    → repeat until status is succeeded|failed (one wait holds ≤50 s); download `artifacts[].url`
```

A submit reply carries `eta_seconds [low, high]` and `suggested_next_wait`. The synchronous kinds
(`analyze_song`, `detect_chords`, `beat_grid`, `analyze_midi`) answer `200` with `output` filled — no polling.

Every kind, its input schema and price: `GET /api/jobs/kinds`; OpenAPI: `GET /api/jobs/openapi.json`.
Errors are always `{error: {type, code, message, retryable}}` — retry only when `retryable` is true,
and **send the same `Idempotency-Key` on the retry** (then it can never start a second job).
`GET /api/jobs` lists your jobs; `POST /api/jobs/<id>/cancel` stops one; add `"webhook": {"url": "https://…"}`
to a submit to be called on completion (Standard Webhooks; the signing secret is in the create response).

Session-control jobs (`list_sessions`, `get_session`, `edit_session`,
`edit_ops_reference`, `download_session`, `bounce_session`, `desktop_status`,
`list_plugins`, `add_audio_to_session`, `create_session`) are covered by the
**doseedo-session** skill.

## Budgets

- **generation** — the ONE monthly credit pool: 10 credits ≙ one 30 s generation
  window (render_midi too: duration × voice batches; takes are free); stems 20
  (orchestra/detect up to 80), cover 40, transcription 2, a DAW conversion 1
  (+1 per GB past the first). Extra usage (purchased) is drawn after. A bounce
  is free (Dø Desktop renders it on the user's machine).
- **dsp** — sound tools (CPU): no credits, a hidden daily fair-use cap.
  audio_to_session's build and the four analyses (analyze_song, detect_chords,
  beat_grid, analyze_midi) are here; audio_to_session's separation draws the credit pool.

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

Every artifact URL is a pre-signed link (`https://api.doseedo.com/api/files/…`)
that downloads with no auth header until its `expires_at` (24 h) — generate and
cover takes included. Read the job again for fresh links after that.
`?format=opus` on an audio URL gives a compressed copy.
