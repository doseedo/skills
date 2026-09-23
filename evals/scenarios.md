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
samples; forgets place_local_files; sets no fader (tracks at +6 dB); unzips
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

Expected: `doo convert <.logicx> --to cubase`… (via the MCP direction
`logic2cubase` if the CLI target list lacks cubase) and says up front the
result is a `.dawproject` that Cubase 14+ imports natively. Fail: reports a
`.dawproject` as a failed conversion.

## 9. Not signed in

**User:** "Transcribe this clip." (no key on the machine)

Expected: exit 3 → asks the user to run `doo login` (or set DOO_API_KEY),
waits, then runs `doo transcribe`. Fail: tries to mint a key, or gives up.

## 10. Long job in a 2-minute shell

**User:** "Cover this 5-minute song."

Expected: runs with a 10-minute tool timeout, or `--no-wait` then
`doo wait <id> --kind cover`. Fail: the shell times out and the agent
reports failure while the job is still running.
