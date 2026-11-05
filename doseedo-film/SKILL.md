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
| 3. Hit points → tempo | per cue: `doo run tempo_map --json` with the cue's `tempo_map_input` as flags (`--bpm --fps --start-timecode --hits '[…]'`; `--time-signature 3/4`, `--bpm-range '[66,96]'`, `--land downbeat` optional). An ad or a song-form cue holds ONE tempo: `--fixed-bpm true --max-deviation-bpm 2 --tolerance-ms 40` (`--land eighth` for quick cuts) → the tempo and `music_offset_s`, the hits it can't land named `landed:false` | free, instant |
| 4. Write the parts | YOU write every part as notes on that beat grid (`[{pitch, start_beats, duration_beats, velocity}]`, beats from bar 1), accents on the hits' beats, thinner under dialogue spans; players from `doo run instruments` (ranges in concert pitch; an unpitched entry's `hit_notes` are the notes to write — a tambourine is 54); a section = one part with `players: N`. Under a voice-over: the full band from bar 1, the body within 4–6 dB, the button 1–1.5 s before the end in a gap in the VO | — |
| 5. Play them | `doo run render_score --parts "$(cat parts.json)" --tempo-map "$(jq -c .tempo_map tm.json)" --bpm <bpm> --time-signature 3/4` (≤ 32 lines, ≤ 96 player rows, ≤ 600 s; a big score as a file: `--score-key cue.mid` uploads it; drums: the drum model plays a real kit by default; `"drum_engine": "oneshot"` on the part — or for a file's part `--instruments '{"Drums":{"drum_engine":"oneshot"}}'` — is a programmed one-shot kit, for an electronic / drum-machine genre only; an acoustic kit stays on the drum model, and a take that drops a hit is taken again) | 10 credits per 30 s window per 6 parts · 1–4 min |
| 6. Sound design | `doo sound-design --prompt "heavy door slam in a stone hall" --kind hit` | 10 credits · ~20 s |
| 7. Mix the cue | `doo run mix --from-job <render job_id> --style <style>` — pick the style for the picture: `cartoon-studio` for animation, `film-orchestral` (default hall) for drama, `film-scoring-stage` for TV / documentary, `film-epic-hybrid` for trailers; `--target-lufs` = the delivery loudness (delivery never limits), `--length-s` cuts it with an end fade | no credits · ~40 s |
| 8. On the picture | `doo run score_to_picture --video-key film.mp4 --tracks '[{"audio_url":"<mix_url>","start_timecode":"01:00:11:21","name":"1M1"},{"audio_url":"door.wav","start_timecode":"01:00:15:18","role":"sfx"}]' --loudness web` (`--production-audio drop` to replace the soundtrack; local track files upload too) | no credits · ~20 s per minute |
| 9. The session | `doo run session_from_stems --from-job <render job_id> --mix-job <mix job_id> --target logic` (or `ableton`) | no credits · 30–90 s |

`doo cost` / `doseedo_quote` prices step 5 before it runs; stop on `⚠ short`.

## Rules

1. **You write the music.** `doo generate` is a prompt-only sketch with no
   notes behind it; never the deliverable for a film.
2. **The cue sheet is a proposal.** It marks where the picture's tension and
   the dialogue allow music. A composer may score one long cue where it
   proposes three; say what you chose and why. Its cues' energy and
   `suggested_bpm` are a guess from light and motion; the intensity decides.
   How much music: an ad, a promo, a trailer or a music video is scored wall
   to wall (first frame to end card); a dialogue drama is spotted.
3. **Intensity decides how hard and when; the picture decides what.**
   `cue_sheet.intensity` is the picture's energy (motion, cutting, camera,
   sound) in sections `{start_s, end_s, level, rel: low|medium|high|peak}`, and
   each scene carries its `intensity_rel`. The music changes where it steps:
   up = drums driving, the full band, louder; down = thinner, quieter or
   silent. A short film's score (an ad, a promo, a trailer) is ONE piece at
   one tempo that builds — a step is that piece changing on the frame (drums
   out or back, a pad or the full band), not a new cue; a new cue only where
   the music's world changes (the source on screen switched, a hard cut to
   another time or place, the end card). A rush, shouting or a whip-pan is
   high however calm the place; a calm band's music (jazz, a crooner) waits
   until the intensity falls and they play. The loudest music is the peak, or
   a payoff the intensity rises to (lay it `"duck": false`), and a low
   section's cue is mastered 10–14 LU under it; an ending that falls low falls
   with it (a button, a soft chord, or silence over the end card).
4. **Verify from the receipts, then listen.** Every part's `fit.verdict` is
   `pass` (coverage = the share of its written notes heard); a failed part is
   re-rendered once automatically. A pass is a measurement, not a listen: a
   part can pass and still clip or add hits. Re-take one part with
   `doo render-midi --notes '[…]' --instrument <id> --takes 3` and pick.
5. **Read the delivery report.** `report.tracks[]` shows where each cue
   landed and what was trimmed at the film's edges; `report.duck` how far the
   music sits under the lines; `report.loudness.final` the LUFS and true peak.
   Delivery never limits: `short_of_target_lu` + `why_short` say when the
   peaks stopped the program short; master the mix louder
   (`doo run mix … --target-lufs -14`) if the target matters.
6. **Hand over paths.** The scored video, the printmaster WAV, the M&E stem,
   the stems and the project: give the user the local paths, not raw JSON.
7. **Long jobs need a long timeout** (render 1–4 min): run with a 10-minute
   tool timeout, or `--no-wait` and `doo wait <task_id> --kind <kind>`.
8. **Players on screen are the music.** A band, a singer or a DJ seen
   performing plays THEIR piece: their genre and the instruments in their
   hands, from the moment they start playing (not on the cut to them; earlier
   only where the intensity rises into their scene; while a band sets up,
   silence or the music before still playing), through
   cutaways until they are stopped, at ONE tempo (`--fixed-bpm true`) that is
   the performance's (punk 150–180, swing 130–200, house 120–128). Lay that
   cue with `"duck": false` in `score_to_picture`. A genre is a recipe: house
   is a kick on every beat, claps on 2 and 4, off-beat hats and bass, 8-bar
   phrases and a drop that is the loudest moment; nothing outside it.
9. **A film with its own music**: `doo run analyze_song --audio-url <the
   music stem>` → `cues[]`, each piece read on its own (start, `full_at_s`,
   end, bpm, key, level vs the loudest) and the `gaps[]` between. The cut was
   made to those entries, stops and silences: score on them. With more than
   one cue, the whole-file bpm and key mean nothing.

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
