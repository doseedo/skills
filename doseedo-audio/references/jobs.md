# Jobs (the MCP tool table, as `doo run` sees it)

`doo jobs` prints the live list; `doo jobs get <job>` the options. Flags are
the argument names with `_` → `-`. A local file argument fills `audio_key` /
`project_key` (uploaded for you); an https URL fills `audio_url` where a job
accepts one.

| job | options | kind (for `doo wait --kind` / `doseedo_wait_task`) | result |
|---|---|---|---|
| `separate_stems` | `--models 6stem\|auto\|orchestra\|detect`, `--instruments "a,b"`, `--include-midi false`, `--stems-only`, `--drum-split`, `--guitar-split auto\|2–4`, `--export logic\|ableton`, `--session-id` + `--parent-track-id` (register the stems into a session); file or `--audio-url` (a result URL works) | `separate_stems` | `stems{name: url}`, `midi{name: url}`, `drum_substems{kick, snare, …}`, `vocals_lyrics`, `vocals_notes`, `session_url`, `session_tracks`, `models_effective`, `other_classification`, `guitar_split` |
| `cover_song` | `--instruments '{"piano":"electric_guitar"}'`, `--lyrics`, `--genre "bossa nova"`, `--cover-noise-strength 0–1`, `--swap-cns 0–1`, `--regen all\|<stems>`, `--labels '{"other":"trumpet"}'`, `--midi-only`, `--timbre-preset`, `--style-key ingest/…`, `--structure-key ingest/…`, `--drum-split`, `--guitar-split auto\|2–4`, `--seed`, `--export logic\|ableton`; file or `--audio-url` | `cover_song` | `files[]`, `cover{duration, windowed, stems, instrument_swaps, genre, guitar_split}`, `seed`, `chain` |
| `transcribe` | `--instrument`, `--tempo-bpm`, `--register`, `--polyphony solo\|poly\|section`, `--roster`, `--strikes`, `--want notes\|f0\|notes,f0` (file or `--audio-url`) | `transcribe` | `backend`, `result.notes[{pitch, onset, offset, velocity, confidence}]`, `result.f0` |
| `generate_music` | `--prompt` (required), `--lyrics`, `--duration-seconds`, `--bpm` (caption hint), `--time-signature` (hint), `--seed` — no key, no MIDI (MIDI: `render_midi`) | `generate_music` | `files[]`, `duration`, `seed`, `best_of_n`, `chain` |
| `generate_sound` | `--prompt` (required: what it sounds like — "punchy house kick drum, single hit"), `--kind` hit\|loop\|texture, `--duration-seconds` (hit default 2 s), `--bpm` / `--time-signature` (a loop's grid), `--seed` — Stable Audio Open; no tempo words in a hit's prompt | `generate_sound` | `files[]` (one sound), `seed`, `chain` = `sao_sound` |
| `render_midi` | `--notes '[{"pitch":62,"start_beats":0,"duration_beats":1,"velocity":100}, …]'` OR `--midi-url <.mid URL>` OR `--session-id` + `--track-id`; `--instrument` (required; the catalog is the MCP tool `doseedo_instruments` — every entry's exact call, range and presets; a World name such as `koto` resolves to its call; a mistyped name is refused with did_you_mean before any charge; raw registry `/api/instruments`), `--bpm` (required), `--time-signature`, `--duration-seconds` (default last note + 2 s), `--takes 1–4`, `--seed`, `--voice-split` (chords), `--refine light\|shred`, `--timbre-preset`, `--timbre-audio-url` (timbre transfer: a recording's tone), `--lora-id` + `--lora-strength 0–2` (a custom instrument from train_instrument; `lora.applied` confirms), `--tempo-map '[{beat, bpm}]'` (tempo changes; replaces --bpm), `--revise-take-url` + `--revise-start-beats` / `--revise-end-beats` (redo one region of a take), results carry `takes[].check` (notes heard, timing, LUFS) when you sent notes, `--dynamics mf`, `--drum-genre house` (electronic / 808 kits: a one-shot kit made for the genre), `--drum-engine oneshot\|model`, `--instrument synth --synth-role bass\|808\|pad\|lead\|pluck --synth-genre house --synth-words "warm analog"` (a one-shot patch made for the part) | `render_midi` | `takes[{url, rank, score}]` best-first, `seed`, `duration`, `voices[]`, `refine.raw_url`, `chain`, `oneshots[{role, url, notes}]` (a one-shot kit's samples) |
| `render_score` | `--parts '[{name, instrument, timbre_preset?, notes:[…]}]'` OR `--score-url` / `--midi-url` (multi-track) / `--musicxml-url`; `--instruments '{"Violin I": {"instrument": "violin"}}'` (override the name/GM-program match), `--bpm` or `--tempo-map '[{beat, bpm}]'`, `--time-signature`, `--duration-seconds`, `--mix` (default true), `--seed` — the whole orchestra in one call: ≤ 32 stems, any mix of plain, sampled and World / custom (LoRA) instruments (the server plays it as groups) | `render_score` | `parts[{name, instrument, url, fit{verdict, coverage, med_offset_ms}, timbre, level, lora{applied}, bus_group}]`, `mix_url`, `bus_groups`; the submit reply's `prepared.parts` shows which instrument plays each part |
| `mix` | `--from-job <render_score job_id>` (MCP) OR `--stems '[{name, audio_url, instrument?}]'`; `--style` (an id: film-orchestral — the default for an orchestra — classical-chamber, jazz-combo, 1970s-analog-rock, 2020s-pop…, or words), `--balance '{"Oboe": 3}'` (dB on top of the levelling; from_job also reads each part's written dynamics), `--target-lufs`; `--mixgraph '<the edited mix>'` re-renders an edit (free) | `mix` | `mix_url` (WAV, held 6 h — download it), `mixgraph` (strips[{stem, gain_db, pan, chain, sends}], buses (verb = the hall), master.chain, automation rides `strips.<stem>.gain_db` in seconds), `report.strips.<part>.active_lufs`, `report.master{lufs_i, true_peak_db}`, `style`, `rails_fixes` |
| `session_from_stems` | `--from-job <render_score job_id>` (MCP) + `--mix-job <mix job_id>` (each track at the mix's level and pan, the mix as a muted reference track) OR `--stems '[{name, audio_url, gain_db?, pan?}]'` + `--midi-tracks`, `--bpm` / `--tempo-map`, `--target logic\|ableton`, `--name` | `session_from_stems` | `file` — the zipped .logicx / .als (audio + MIDI + tempo map) |
| `check_take` | `--audio-url` (a take) + `--notes '[…]' --bpm` (or `--tempo-map`, or `--midi-url`), `--instrument` — synchronous, no credits | — | `verdict` (good/check/bad) + `reasons`, `notes{recall, precision, matched, sent, onset_error_ms}`, `loudness{integrated_lufs, peak_dbfs}`, `silence` |
| `train_instrument` | `--audio-key` / `--audio-keys` or `--audio-url` / `--audio-urls` (30 s–3 min of ONE instrument, solo and dry; ≤8 takes), `--instrument` (required: the closest catalog instrument, e.g. `acoustic_guitar` for a shamisen), `--name`, `--notes` (optional `[{pitch, start, end}]` seconds — else transcribed), `--bpm`, `--drum-mode`, `--steps 50–800` — 20 credits | `train_instrument` | `lora_id`, `use` (the render_midi args), `loss{first,last}`, `windows[]` |
| `cover_stem` | `--audio-key` or `--audio-url` (ONE recorded part: a stem, a solo, a region), `--instrument` (required), `--duration-seconds` (required: its length), `--timbre-preset`, `--fidelity 0–0.6` (default 0: structure from its FSQ codes only; more keeps that much of the recording's own sound), `--midi` (the server's own pitch roll of the recording beside the codes), `--bpm`, `--takes`, `--seed` — no MIDI, no transcription | `cover_stem` | `takes[{url, rank}]` |
| `fill_gap` | `--audio-key` or `--audio-url` (ONE recorded part with a gap in it — the silence between two clips, a bar to redo), `--duration-seconds` (required: its length), `--gap-start-seconds` / `--gap-end-seconds` (required, seconds of that audio), `--bpm` (required), `--time-signature`, `--bar-offset-seconds` (where a bar line falls in it), `--exact-grid` (cut from a DAW session: its grid is exact, keep it), `--fill auto\|loop\|written`, `--instrument`, `--role`, `--takes`, `--seed` — the take outside the gap is kept exactly | `fill_gap` | `takes[{url, rank}]` (whole-length, the gap filled) |
| `audio_to_session` | `--target logic\|ableton`, `--midi-stems`, `--keep-stem-audio false`, `--chords`, `--key false`, `--markers false`, `--simple`, `--stem-mode auto\|6stem\|drumsep\|sections\|orchestra\|detect` (default auto; orchestra/detect need `--simple`), `--instruments`, `--quantize-midi grid\|score`, `--drum-substems`, `--drum-midi-split`, `--guitar-split auto\|0\|2–4`, `--retune false`, `--dereverb`, `--separate false`, `--tempo-map false`, `--crop-silence`, `--loops`, `--drum-sampler`, `--name`; file or `--audio-url` | `audio_to_session` | `file` (zip), `summary` |
| `analyze_song` | file or `--audio-url` | — (sync: the result is in the reply) | `key`, `bpm`, `tempo_map`, `meter`, `beats_per_bar`, `downbeats`, `sections`, `chords`, `dynamics` |
| `detect_chords` | file or `--audio-url`, `--deep false` (CPU detector) | — (sync) | `chord_spans[{chord, start, end, start_beat, end_beat, confidence}]`, `chords{beat: symbol}`, `bpm`, `beat_map` |
| `beat_grid` | file or `--audio-url` | — (sync) | `bpm`, `beats[]`, `downbeats[]`, `beats_per_bar`, `beat_map` |
| `analyze_midi` | `--notes '[…]'` + `--bpm`, or `--midi-url`; `--mode midi\|chord`, `--beats-per-segment`, `--min-seg-beats` | — (sync) | `sonorities[]` or `chords[]`, `cover`, `cells`, `compression` |
| `convert_project` | `--direction <src>2<dst>` (file = the project) | `convert_project` | `file` (zip) |
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

Every kind, its input schema, aliases and price: `GET /api/jobs/kinds`; OpenAPI: `GET /api/jobs/openapi.json`.
**`kind` on a submit must be the exact registry name** (the first column above); an alias such as
`generate` or `stems` is refused with `400 unknown_kind` + `did_you_mean` so a typo never starts a
billable job. The old short codes (`separate`, `session`, `cover`, `generate`, `render`, `convert`,
`bounce`) are still accepted as aliases by `doo wait --kind` / `doseedo_wait_task`.
Errors are always `{error: {type, code, message, retryable, plane, next, request_id}}` — retry only when
`retryable` is true, ONCE after ~30 s for `service_unavailable` / `timeout` (then tell the user which
doseedo service — `plane` — is down; never loop), and **send the same `Idempotency-Key` on the retry**
(then it can never start a second job).
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
