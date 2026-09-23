---
version: 0.1.3
name: doseedo-convert
description: |
  Convert a DAW project to another DAW with doseedo — Logic Pro, Ableton
  Live, FL Studio, Pro Tools, REAPER, Cubase and Dorico, any pair, both
  ways. The project is rebuilt natively: tracks, MIDI, audio clips, tempo
  and markers arrive editable (Logic↔Ableton also carries automation,
  buses/sends and plugin state). Use when: "open this Ableton set in
  Logic", "send my Logic project to a Pro Tools user", "FL Studio to
  REAPER", "convert my project", ".als to .logicx", "Cubase to Ableton",
  "get this score into Dorico". NOT for: building a session from AUDIO
  (use doseedo-session), separating stems (use doseedo-audio), or
  converting audio file formats.
argument-hint: "<project folder or file> [--to logic|ableton|fl|reaper|protools]"
allowed-tools: Bash, mcp__doseedo__*
---

# doseedo convert

## Step 0 — bootstrap

`doo version` (else `npm install -g @doseedo/cli`), then `doo whoami` (else
ask the user to run `doo login`). Without a shell, use the MCP path below.

## Run

```bash
doo convert "My Song Project/" --to logic        # Ableton folder → .logicx.zip
doo convert "My Song.logicx" --to ableton         # Logic package → .als
doo convert beat.flp --to reaper
doo convert "Session Folder/" --to protools
doo convert song.cpr --to ableton                 # Cubase → Ableton
doo convert score.mxl --to logic                  # MusicXML (from Dorico) → Logic
```

`--to` defaults to the "other" flagship DAW (Ableton → Logic, everything
else → Logic). Output lands next to you as `<name>.logicx.zip`, `<name>.als`,
`<name> FL.zip`, `<name> REAPER.zip`, `<name> Pro Tools.zip`; unzip and open.
Cost: one conversion from the monthly allowance (paid plans: 1,000+). Time
15 s – 2 min; multi-GB sessions are fine (the bundle streams, no size cap).

## What to pass — this decides whether audio travels

| source | pass | why |
|---|---|---|
| Ableton | the **project folder** (contains the `.als` and `Samples/`) | a lone `.als` references audio by path; without `Samples/` you get structure + MIDI only (the CLI warns) |
| Logic | the `.logicx` package (or a `.logicx.zip`) | bundled by the CLI |
| FL Studio / REAPER / Pro Tools | the **project folder** (`.flp`/`.rpp`/`.ptx` + its audio) | a bare file resolves external media only by absolute path |
| Cubase | the `.cpr` | tracks, tempo, signature, MIDI parts carry; the audio pool does not → audio tracks arrive named but empty |
| Dorico | a **MusicXML** export (`.musicxml`/`.mxl`), not the `.dorico` | a `.dorico` carries players and flows but NO notes |

## ★ Cubase and Dorico are asymmetric — say so before the user finds out

Neither native format is documented, so a file the app might refuse is never
written:

| target | you get | opens in |
|---|---|---|
| Cubase | **`.dawproject`** (not `.cpr`) | Cubase 14+, Nuendo, Studio One, Bitwig — as a real editable session |
| Dorico | **MusicXML `.mxl`** (not `.dorico`) | Dorico, MuseScore, Finale, Sibelius |

A `.dawproject` for "convert to Cubase" is the correct result, not a failure.
Details: [references/formats.md](references/formats.md).

## Verify, then hand over

1. The output exists and its extension is the target format (`.logicx` /
   `.als` / `.flp` / `.rpp` / `.ptx` / `.dawproject` / `.mxl`).
2. Report what the conversion said it could not carry (plugin state across
   ecosystems, Cubase audio pool, Dorico notes from a `.dorico`). Silence is
   not "lossless".
3. Give the PATH. The converted project is the deliverable.

## Without a shell (pure MCP)

`doseedo_get_project_upload_url {filename}` → `curl -X PUT --data-binary
@project.zip "<upload_url>"` → `doseedo_convert_project {project_key,
direction: "ableton2logic"}` → `doseedo_wait_task kind="convert"` → `curl -OJ`
the result URL. Directions are `<source>2<target>` over logic | ableton |
fl | protools | reaper | cubase | dorico. Zip a project FOLDER so its audio
travels.

## Failures

`503` — the converter is cold-starting; retry in a moment. `413` — over the
upload limit for this route (use the CLI, which streams). `429` — the
monthly conversion allowance is used up; the message names the reset and
https://doseedo.com/plans. `400 could not read the project` — wrong input
kind (see the table above).
