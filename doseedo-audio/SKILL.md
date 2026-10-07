---
version: 0.1.8
name: doseedo-audio
description: |
  Separate a mix into stems (with per-stem MIDI), re-perform a song as a
  cover with different instruments, transcribe audio to notes, or generate
  music from a prompt — via the `doo` CLI (doseedo). Each job is one command
  that uploads, waits and downloads; every job is priced before it runs.
  Use when: "separate this song", "give me the stems / vocals / drums / an
  acapella", "isolate the sax", "cover this song on guitar", "swap the piano
  for strings", "transcribe this solo", "what notes is this", "make me a
  track that sounds like…", "30 seconds of lo-fi piano", "render this MIDI
  as a trombone". NOT for: turning a recording into a full DAW session or
  editing a DAW session (use doseedo-session), converting a project between
  DAWs (use doseedo-convert), or audio-format conversion.
argument-hint: "[file-or-prompt] [--models orchestra] [--instruments sax,trumpet] [--json]"
allowed-tools: Bash
---

# doseedo audio

Stems, covers, transcription and generation through the `doo` CLI. One
command per deliverable; the result is files on disk plus a verify hint.

## Step 0 — bootstrap

1. `doo version` — if missing: `npm install -g @doseedo/cli` (Node ≥ 20).
2. `doo whoami` — if not signed in, ask the user to run `doo login`
   (interactive: it opens a browser) and wait for their confirmation. A
   headless alternative is `export DOO_API_KEY=dsk_live_…` from
   https://doseedo.com/settings/api-keys.
3. `doo account` — tier, the monthly credit pool (every tool draws it: free
   120, Pro 2,000), purchased extra-usage credits, and storage.

## Pick the recipe

| The user wants | Run | Cost · time |
|---|---|---|
| stems, an acapella / instrumental, one instrument isolated | `doo stems <audio>` | 20 credits · ~2 min |
| orchestral / horn / named instruments out of a mix | `doo stems <audio> --models orchestra --instruments "saxophone,trumpet"` | 1 + ⌈n/8⌉ · ~2–4 min |
| the same song re-performed, instruments swapped, new lyrics | `doo cover <audio> [--instruments '{"piano":"electric_guitar"}'] [--lyrics …]` | 40 credits · 3–8 min |
| the notes of a clip (JSON: pitch, onset, offset, velocity) | `doo transcribe <audio or https URL> [--instrument sax] [--tempo-bpm 120]` | up to 2 credits · 15–60 s |
| a new track from a description (style/mood — NOT a key or exact tempo) | `doo generate "<prompt>" [--duration-seconds 30] [--lyrics …] [--bpm 100]` | 10 credits per 30 s · 1–3 min |
| the key / tempo / meter / sections / chords of a recording | `doo analyze-song <audio or https URL>` (synchronous) | free · 5–20 s |
| a part in a given key / at a session's tempo, or MIDI rendered as an instrument | write the notes yourself, then `doo render-midi --notes '[…]' --instrument trombone --bpm 92` (or `--midi-url`, or `doo generate --midi part.mid -i trombone`; see "Key, tempo and takes") | 10 credits per 30 s · 1–3 min |
| a full DAW session from a mix | → doseedo-session (`doo session`) | |

`doo recipes` prints this list from the server; `doo recipes get <name>`
shows a recipe's inputs, steps, outputs and verify rule. `doo jobs` lists
every underlying job and `doo run <job> [--opt v] [file]` runs one directly
(see [references/jobs.md](references/jobs.md)).

## Rules

1. **One command, then hand over the paths.** Every recipe prints the local
   files it wrote (default `./<recipe>_<name>/`). Give the user those paths;
   don't narrate uploading or polling, don't paste raw JSON.
2. **Long jobs need a long tool timeout.** stems ~2 min, cover 3–8 min,
   generate 1–3 min. Run the command with a 10-minute timeout, or submit
   with `--no-wait`, do other work, and `doo wait <task_id> --kind <kind>`.
3. **Cost is shown before spending** (`≈ N credit(s) · M left`). If the line
   says `⚠ short`, stop and tell the user rather than letting the gate refuse.
   `doo cost <recipe> [--flags]` answers "how much" without submitting.
4. **Verify from the result, not from optimism.** Each recipe ends with a
   `verify:` line — read it. stems: every requested stem is present (a
   missing one means the model heard none of that instrument; say so). cover:
   `result.cover.instrument_swaps` reports each swap as applied or not.
   transcribe: notes non-empty and in the instrument's range. generate:
   duration near the request.
5. **`--json` for anything you parse.** Progress goes to stderr; stdout is
   the result: `{recipe, inputs, steps[], files[{name, path, bytes, url}], verify}`.
6. **Big files are fine.** The CLI uploads straight to storage (no proxy body
   cap). Pass paths with spaces quoted.
7. **Prefer the quality default; don't downgrade to save credits unless
   asked.** `--models auto` adapts the stem set; `orchestra` needs
   `--instruments`; `detect` picks from the orchestra bank and refunds what
   it skips.

## Key, tempo and takes

- **Prompt generation does not take a key, and `--bpm` is only a caption
  hint** (the output can drift from it). Never promise "in D minor at 92 BPM"
  from a prompt.
- **For a part that must fit a key and tempo, YOU write the MIDI**: get the
  key and tempo from the material — `doo analyze-song <reference>` (key, bpm,
  meter, sections, chords; synchronous, free) — never by guessing or asking;
  compose the notes in that key at that tempo as
  `[{pitch, start_beats, duration_beats, velocity}]` (beats from bar 1), then
  render them: `doo render-midi --notes '[…]' --instrument <id> --bpm <tempo>`
  (instrument ids: `curl https://api.doseedo.com/api/instruments`; `--midi-url`
  takes a .mid instead; `--voice-split` for chords; `--takes 1–4`; `--refine
  light|shred`). Keep one voice per part. Check the harmony first for free with
  `doo run analyze_midi --notes '[…]' --bpm <tempo> --mode chord`. The notes are
  rendered AS WRITTEN — no snapping. Shell fallback, same request: `doo generate
  --midi part.mid -i <id>` or `curl -X POST
  https://api.doseedo.com/api/generate-stemphonic -H "X-API-Key: $DOO_API_KEY"
  -F midiFile=@part.mid -F instrument=<id> -F prompt=<id> -F duration=<s>
  -F bpm=<tempo> -F lyrics="[Instrumental]"`.
- **Several takes come back** for a pitched one-voice MIDI part
  (`takes[{url, rank, score}]`, best-first by a scorer; the CLI saves the top
  one; `seed` re-renders close to it). The model sometimes misses or changes a
  note — expected. Hand the user the takes, or pick one by listening /
  transcribing each (`doo transcribe <take url>`) and comparing against the
  notes you sent, and say how you chose.
- **Covers re-play transcribed notes**: an instrument swap transcribes the
  stem and re-performs it, so small note differences from the source are
  normal. Read `result.cover.instrument_swaps`, offer the result to judge.
  Knobs on `doo cover`: `--swap-cns 0–1` (how far a swapped stem may
  depart, default 0.35), `--regen all|<stems>` (default: only swapped stems
  regenerate); via `doo run cover_song`: also `--labels
  '{"other":"trumpet"}'` (fix a mislabelled stem) and `--midi-only`.
- Every result URL is a pre-signed link: a plain `curl -OJ <url>` downloads
  it with no auth header until its `expires_at` (24 h). Pass a result URL
  straight to `transcribe` as `audio_url`.

## Examples

```bash
doo stems "My Song.wav"                                  # vocals drums bass guitar piano other (+ .mid each)
doo stems solo.wav --models orchestra --instruments "saxophone,trumpet,trombone"
doo cover song.wav --instruments '{"piano":"electric_guitar","sax":"violin"}'
doo transcribe riff.wav --instrument sax --json | jq '.steps[0].result.result.notes | length'
doo generate "warm jazz trio, brushed drums, late-night ballad" --duration-seconds 45
doo analyze-song song.wav --json | jq '{key, bpm, meter}'
doo render-midi --notes '[{"pitch":62,"start_beats":0,"duration_beats":2},{"pitch":65,"start_beats":2,"duration_beats":2}]' --instrument cello --bpm 92
doo session song.wav --midi-stems piano,bass               # → doseedo-session
```

## When something fails

Exit `3` → not signed in (`doo login`). Exit `2` → the job failed; the
message names the plane and the reason. `429` → daily/monthly allowance
reached (the message gives the reset time and https://doseedo.com/plans).
More in [references/troubleshooting.md](references/troubleshooting.md).
