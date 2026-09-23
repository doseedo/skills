---
version: 0.1.1
name: doseedo-session
description: |
  Build, read and edit DAW sessions with doseedo: a recording → a complete
  Logic Pro / Ableton session (stems as tracks, tempo map, per-stem MIDI,
  chord guide) with one `doo session` call, or drive the user's sessions
  over the doseedo MCP — read the arrangement, add tracks, write MIDI, load
  the user's own samples into Quick Sampler without uploading, set faders,
  insert plugins by name, route buses, bounce through real plugin chains,
  download a native project. With Dø Desktop running, edits land in the
  open Logic project live. Use when: "open this song in Logic as tracks",
  "build a session from this recording", "make a drum kit from these
  samples", "add a MIDI bass line to my session", "set the vocal to -6 dB",
  "put the drums on a bus", "bounce my session's stems", "swap my project
  onto this drum pack". NOT for: loose stems or covers (doseedo-audio),
  converting a project to another DAW (doseedo-convert); live editing is
  Logic Pro only (build/download: Logic and Ableton).
argument-hint: "[audio-file | session request] [--target logic|ableton] [--midi-stems piano,bass]"
allowed-tools: Bash, mcp__doseedo__*
---

# doseedo session

Two paths, one product:

- **A. Audio → session** — `doo session <mix>` (the CLI). One call, ~4 min,
  a `.logicx` / `.als` with stems as tracks, tempo map, optional MIDI tracks
  and a chords guide.
- **B. Session control** — the doseedo MCP tools. Read a session's full
  arrangement, edit it op-by-op, bounce, download. Works from anywhere
  (including a phone); with Dø Desktop open on the user's Mac the edits
  apply to the open Logic project live.

## Step 0 — bootstrap

**CLI (path A):** `doo version` (else `npm install -g @doseedo/cli`), then
`doo whoami` (else ask the user to run `doo login`).

**MCP (path B):** the `doseedo_*` tools must be available to you. If they
are not, ask the user to connect the server — Claude Code:

```bash
claude mcp add --transport http --scope user doseedo https://api.doseedo.com/mcp
```

(OAuth sign-in on the first tool call, or add
`--header "X-API-Key: dsk_live_…"` from https://doseedo.com/settings/api-keys.)
Cursor / Codex / Claude apps: https://doseedo.com/mcp.

## A. Audio → session (`doo session`)

```bash
doo session song.wav                                  # Logic, chords guide on
doo session song.wav --target ableton
doo session song.wav --midi-stems piano,bass          # + MIDI tracks for those stems
doo session song.wav --simple                         # meter + tempo + stems only, faster
```

Cost: 1 DSP credit + 1 generation credit (the separation). Time ~4 min — run
with a 10-minute tool timeout, or `--no-wait` then `doo wait <task_id> --kind session`.

Result: `session_<name>/<Name>.logicx.zip` (or `.als` zip) + a `summary`
(tracks, tempo, what was placed). **Verify** from the summary — one track per
stem and per `--midi-stems` entry, a tempo — then hand over the PATH. The
session IS the deliverable; don't build anything else to "show" it.

## B. Session control (MCP) — the 5-call workflow

1. `doseedo_list_sessions` (or `doseedo_create_session {name}`) → `session_id`.
2. `doseedo_get_session` → every track's ids (`track_id t_…`, its mixer strip
   `channel_id ch_…`), regions in beats AND seconds, mixer in dB, plugins,
   tempo, markers, and a `sync` block (is the desktop live? how far behind?).
3. `doseedo_edit_ops_reference` — **once per session**: the op catalog with
   args and units, the workflow, and **recipes** (drum kit from local samples,
   one-shots on an audio track, remote sample, submix bus, verify). Copy a
   recipe; don't discover op order by trial.
4. `doseedo_edit_session` with ALL the ops in ONE call (up to 500, applied
   in order — `add_track`, `load_quick_sampler_sample`, `set_midi_notes`,
   `set_channel_volume` for every track can go together). **Always pass a
   `batch_key`** (any stable id, e.g. `"drumkit-build-1"`): a call that
   times out may have been stored, and re-sending with the same key dedups
   instead of duplicating. Batches are **atomic by default** — one rejected
   op means nothing was stored and the response lists every rejection with
   a `code` (`unknown_op`, `forbidden_group`, `invalid`); fix and re-send
   the whole batch with the same `batch_key`.
5. `doseedo_download_session` → a no-auth download URL **plus a `replay`
   report** of what actually landed in the file (per track: sample, note
   count, region count; `deferred` ops; `warnings`). **Verify from `replay`,
   never by unzipping and inspecting the bundle.** Then `curl` the URL into
   `~/Downloads`, unzip, and run every `place_local_files` command if present.

### IDs & units (get these right)

- Mint new ids as 12 random lowercase hex: track `t_<hex>`, its strip
  `ch_<same hex>`, bus `ch_b_<hex>`, marker `m_<hex>`.
- Beats are absolute from bar 1 (beat 0 = bar 1) at the project tempo; one
  bar of 4/4 = 4 beats.
- Faders: `set_channel_volume value 0.709` = 0 dB (unity). A new track
  defaults to 1.0 = +6 dB — set 0.709 explicitly.
- Quick Sampler plays a loaded one-shot at its recorded pitch on C3 = MIDI 60:
  drum hits at pitch 60, a tuned 808 line relative to 60.

### ★ Samples on the user's machine never leave it

For a drum pack or one-shot already on the user's disk, pass its LOCAL PATH:
`add_track {content_type: "instrument"}` (Quick Sampler is the default
instrument) → `load_quick_sampler_sample {track_id, sample_path: "/abs/file.wav"}`.
Audio regions from a local file: `attach_audio {track_id, local_path,
audio_info, start_beats}` or N hits with `set_track_clips` — `audio_info`
(sample_rate, frame_count, channels, bits_per_sample, bytes) is read from the
file header locally. The download then returns `place_local_files`: `cp`
commands that drop each file into the unzipped bundle — REQUIRED, or the
samplers open empty. Full recipe: [references/local-samples.md](references/local-samples.md).

Upload ONLY when the server must read the audio (separation, transcription,
cover, conversion, bounce) or the file is not on this machine (a phone):
`doseedo_get_upload_url` → `curl -X PUT` → `doseedo_add_audio_to_session
{audio_key}` → sha256 → `load_quick_sampler_sample {sample_path: "<sha256>"}`.

### Plugins, live vs offline, bounce

- Plugins insert BY NAME: `add_device {channel_id, device: {name: "Channel EQ"}}`
  — no AU codes. `doseedo_list_plugins` shows the stock palette and, when the
  desktop is connected, what is installed on the user's Mac.
- `doseedo_desktop_status`: is Dø Desktop running with Logic connected? If
  yes, edits reach the open project within seconds; if not, they persist and
  land in the next download or open. Download never needs the desktop.
  `replay.deferred` lists ops the offline build could not synthesize —
  rebuild those with a supported op or accept that they apply live; don't
  re-export blindly.
- `doseedo_bounce_session` renders tracks through their real plugin chains
  (live via Logic, or headless) → poll `doseedo_wait_task kind="bounce"`;
  `engine` in the result says which. From the shell: `doo bounce --session-id <id>`.

## Rules

1. Read the ops reference once, batch every op into one edit call, verify
   from `replay`, hand over the path. Four calls, not forty.
2. Never pass a local path where the SERVER must read the file, and never
   upload a file the server doesn't need (see the sample law above).
3. Don't guess ids, units or op names — they are in `get_session` and the
   ops reference. An op the catalog doesn't list doesn't exist.
4. Say what actually landed. `replay` and `warnings` are the truth; "the
   call returned 200" is not.
5. Live editing covers Logic Pro today. Building, reading and downloading
   cover Logic Pro and Ableton Live; for other DAWs, build for Logic and use
   doseedo-convert.
6. **Respect the key's policy.** A `403 code=read_only_key` means the
   connected key is read-only (`read:sessions`); `forbidden_group` means it
   may not touch that op category (`ops:<group>` scopes). Don't retry — tell
   the user which scope the key needs (`write:sessions`, or `ops:mixer` etc.)
   and where to mint it (https://doseedo.com/settings/api-keys).
7. **No undo group per batch.** The desktop applies stored ops one at a time;
   a mid-batch failure leaves the earlier ops applied. Prefer one well-formed
   atomic batch over many small calls, and verify from `replay`.

Op groups and the recipe list: [references/session-ops.md](references/session-ops.md).
