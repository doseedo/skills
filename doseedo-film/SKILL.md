---
version: 0.1.16
name: doseedo-film
description: |
  Score a film or video as an agent: doseedo watches the cut and hands you
  the cue sheet (every cut frame-exact, shots with keyframes, dialogue,
  proposed cues with SMPTE in/out, hit points and a tempo), lands the hits
  on downbeats, plays the parts YOU write on 50+ AI instruments (a stem per
  part, each checked against its notes), mixes the cue for the picture and
  lays it on the video, ducked under the dialogue and normalised to a
  delivery loudness, via the `doo` CLI (doseedo). Use when: "score this
  video", "music for my short film", "a cue that hits the cuts", "spot this
  reel", "a cue sheet for this cut", "underscore under the dialogue", "put
  music on this video", "score to picture", "temp score replacement",
  "music for a trailer / an ad / an animation". NOT for: a song or a piece
  with no picture (use doseedo-audio), stems or a cover of a recording
  (doseedo-audio), editing a DAW session (doseedo-session), or video editing
  itself (cutting, colour, titles): the picture is never re-encoded.
argument-hint: "<video file or https URL> [--coverage 0.55] [--loudness web|streaming|broadcast]"
allowed-tools: Bash
---

# doseedo film

doseedo does the parts of scoring to picture an agent cannot do alone:
watching every frame, making an orchestra play, and delivering a scored
file. YOU do the musical thinking in between. The same loop runs over MCP
(`https://api.doseedo.com/mcp/film` lists only these tools); this skill runs
it with the `doo` CLI.

## Step 0 — bootstrap

1. `doo version` — 0.4.2 or later uploads a local video for you. Missing or
   older: `npm install -g @doseedo/cli@latest` (Node ≥ 20). On an older CLI,
   pass a public `--video-url https://…` instead of a file.
2. `doo whoami` — if not signed in, ask the user to run `doo login` and wait
   for their confirmation (or `export DOO_API_KEY=dsk_live_…` from
   https://doseedo.com/settings/api-keys).
3. `doo recipes get score-a-film` — the server's own step list for this loop.

## The loop

| Step | Run | Cost · time |
|---|---|---|
| 1. Spot the cut | `doo run spot_video --video-key film.mp4 --json` (mp4 / mov / m4v / webm / mkv, ≤ 2 GB, ≤ 3 h; `--start-timecode 01:00:00:00` if the film starts there; `--coverage` 0.05–0.98 = how much of it gets music) | no credits · ~15 s per minute of 1080p |
| 2. Look | open the keyframe JPEGs it saved: it sees light, motion and editing, not story. Decide what each cue is about, keep, move or drop cues and hits | — |
| 3. Hit points → tempo | per cue: `doo run tempo_map --json` with the cue's `tempo_map_input` as flags (`--bpm --fps --start-timecode --hits '[…]'`; `--time-signature 3/4`, `--bpm-range '[66,96]'`, `--land downbeat` optional) | free, instant |
| 4. Write the parts | YOU write every part as notes on that beat grid (`[{pitch, start_beats, duration_beats, velocity}]`, beats from bar 1), accents on the hits' beats, thinner under dialogue spans; players from `doo run instruments` (ranges in concert pitch); a section = one part with `players: N` | — |
| 5. Play them | `doo run render_score --parts "$(cat parts.json)" --tempo-map "$(jq -c .tempo_map tm.json)" --bpm <bpm> --time-signature 3/4` (≤ 32 lines, ≤ 96 player rows, ≤ 600 s; or `--musicxml-url` / `--midi-url`) | 10 credits per 30 s window per 6 parts · 1–4 min |
| 6. Sound design | `doo sound-design --prompt "heavy door slam in a stone hall" --kind hit` | 10 credits · ~20 s |
| 7. Mix the cue | `doo run mix --from-job <render job_id> --style <style>` — pick the style for the picture: `cartoon-studio` for animation, `film-orchestral` (default hall) for drama, `film-scoring-stage` for TV / documentary, `film-epic-hybrid` for trailers | no credits · ~40 s |
| 8. On the picture | `doo run score_to_picture --video-key film.mp4 --tracks '[{"audio_url":"<mix_url>","start_timecode":"01:00:11:21","name":"1M1"},{"audio_url":"door.wav","start_timecode":"01:00:15:18","role":"sfx"}]' --loudness web` (`--production-audio drop` to replace the soundtrack; local track files upload too) | no credits · ~20 s per minute |
| 9. The session | `doo run session_from_stems --from-job <render job_id> --mix-job <mix job_id> --target logic` (or `ableton`) | no credits · 30–90 s |

`doo cost` / `doseedo_quote` prices step 5 before it runs; stop on `⚠ short`.

## Rules

1. **You write the music.** `doo generate` is a prompt-only sketch with no
   notes behind it; never the deliverable for a film.
2. **The cue sheet is a proposal.** It marks where the picture's tension and
   the dialogue allow music. A composer may score one long cue where it
   proposes three; say what you chose and why.
3. **Verify from the receipts, then listen.** Every part's `fit.verdict` is
   `pass` (coverage = the share of its written notes heard); a failed part is
   re-rendered once automatically. A pass is a measurement, not a listen: a
   part can pass and still clip or add hits. Re-take one part with
   `doo render-midi --notes '[…]' --instrument <id> --takes 3` and pick.
4. **Read the delivery report.** `report.tracks[]` shows where each cue
   landed and what was trimmed at the film's edges; `report.duck` how far the
   music sits under the lines; `report.loudness.final` the LUFS and true peak.
   Delivery never limits: `short_of_target_lu` + `why_short` say when the
   peaks stopped the program short; master the mix louder
   (`doo run mix … --target-lufs -14`) if the target matters.
5. **Hand over paths.** The scored video, the printmaster WAV, the M&E stem,
   the stems and the project: give the user the local paths, not raw JSON.
6. **Long jobs need a long timeout** (render 1–4 min): run with a 10-minute
   tool timeout, or `--no-wait` and `doo wait <task_id> --kind <kind>`.

## Verify

- spot: the cuts you can check by eye (a frame sheet around a cut) fall on
  the first frame of the new shot.
- tempo: every hit you kept has `beat_in_bar: 1` (or a `notes` line saying
  why not) and `timing_error_ms` is a fraction of a millisecond.
- render: every part `pass`; listen to the parts flagged by
  `doo run check_take`.
- picture: each cue's `start_s` matches its timecode and `trimmed_s` is only
  the tail you expected; the final LUFS is the target or `why_short` says why.

A worked example with every call and receipt: Big Buck Bunny, scored by an
AI agent — https://doseedo.com/guides/big-buck-bunny-scored-by-an-ai-agent.
