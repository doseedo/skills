# Scenarios

Score each: **pass** (all expected behaviours), **partial** (deliverable
right, process wrong), **fail**.

## 1. Stems

**User:** "Separate `~/Music/take.wav` into stems."

Expected: `doo stems ~/Music/take.wav` (nothing else); prints the local
paths; if a stem is missing, says the model heard none of that instrument;
no raw JSON in chat. Fail: uses `doo run` with hand-built flags, narrates
polling, re-runs on a missing stem.

## 2. Orchestral extractors

**User:** "Pull the sax and trumpet out of this big-band recording."

Expected: `doo stems <file> --models orchestra --instruments "saxophone,trumpet"`;
mentions the cost is 1 + ⌈2/8⌉ = 2 credits only if credits look low or the
user asks. Fail: `6stem` (no sax/trumpet stems), or `detect` without saying
it prices for the whole bank.

## 3. Session from audio

**User:** "I want to remix this song in Logic — set me up."

Expected: `doo session <file>` (chords default on), run with a long timeout
or `--no-wait` + `doo wait`; hands over the `.logicx.zip` path and the
track list from `summary`. Fail: runs stems then tries to assemble a project
by hand; builds a "preview" page.

## 4. Drum kit from local samples

**User:** "Make me a Logic session with a kit from `~/Drums/`: kick, snare,
hat, four-on-the-floor at 124."

Expected (MCP): create_session → edit_ops_reference once → ONE edit_session
with add_track / load_quick_sampler_sample (LOCAL paths) / set_midi_notes
(pitch 60) / set_channel_volume 0.709 per drum → download_session → verifies
from `replay` → curl + unzip + runs `place_local_files`. Fail: uploads the
samples; forgets place_local_files; sets no fader; unzips
to inspect instead of reading `replay`.

## 5. Fader edit on an existing session

**User:** "Drop the vocal on 'Demo 3' to −6 dB."

Expected: list_sessions → get_session (finds the vocal's `ch_…`) →
edit_session `set_channel_volume` with the dB→linear value the ops reference
gives → reports whether the desktop applied it live (`sync`/desktop_status).
Fail: guesses the channel id; passes −6 as the value.

## 6. Cover with a swap

**User:** "Cover this with the piano as an electric guitar."

Expected: `doo cover <file> --instruments '{"piano":"electric_guitar"}'`;
reads `result.cover.instrument_swaps` and reports whether the swap applied;
mentions 4 credits before running only if short. Fail: claims the swap
happened without reading the field.

## 7. Cost question

**User:** "How many credits would a 4-minute generation cost me?"

Expected: `doo cost generate --duration-seconds 240` → answers 9 credits and
whether the account can afford it; spends nothing. Fail: runs a generation.

## 8. Convert to Cubase

**User:** "Convert my Logic project for a Cubase user."

Expected: `doo convert <.logicx> --to cubase` (or the MCP direction
`logic2cubase`) and says up front the result is a `.dawproject` that Cubase
14+ imports natively. Fail: reports a `.dawproject` as a failed conversion.

## 9. Not signed in

**User:** "Transcribe this clip." (no key on the machine)

Expected: exit 3 → asks the user to run `doo login` (or set DOO_API_KEY),
waits, then runs `doo transcribe`. Fail: tries to mint a key, or gives up.

## 10. Long job in a 2-minute shell

**User:** "Cover this 5-minute song."

Expected: runs with a 10-minute tool timeout, or `--no-wait` then
`doo wait <id> --kind cover`. Fail: the shell times out and the agent
reports failure while the job is still running.

## 11. GarageBand into Ableton

**User:** "Here's my GarageBand song, can I open it in Ableton?" (a
`My Song.band` folder)

Expected: `doo convert "My Song.band" --to ableton` (the CLI zips the
package; by MCP, zip the `.band` folder and use `garageband2ableton`), then
tells the user GarageBand's own instrument sounds do not travel — the notes
and patch names do. Fail: uploads the bare `.band` as a file, calls it a
Logic project, or promises the Apple instrument sounds.

## 12. Bitwig native project

**User:** "Convert this to Logic." (a `Track.bwproject`)

Expected: does not upload it; tells the user to export DAWproject from
Bitwig (File > Export… > DAWproject) and converts the `.dawproject` with
`--to logic`. Fail: reports the converter as broken.

## 13. Score a short film

**User:** "Here's my 3-minute short (`cut.mp4`). Score it, and make the
music hit the cuts."

Expected: picks doseedo-film. `doo run spot_video --video-key cut.mp4`,
looks at the keyframes, says which proposed cues it keeps, runs
`doseedo_tempo_map` per cue, WRITES the parts as notes, renders them with
`doseedo_render_score`, checks every part's `fit`, mixes with a style chosen
for the picture, delivers with `doo run score_to_picture`, and reads the
report (where each cue landed, the duck, the final LUFS, `why_short` if it
fell short). Hands over the scored video, the printmaster, the M&E stem and
the project paths. Fail: uses `doo generate` for the score, spots the cut
by hand with ffmpeg, or muxes the audio itself.
