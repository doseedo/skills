---
version: 0.1.7
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
Cost: 1 credit (+1 per GB past the first) from the monthly credit pool. Time
15 s – 2 min; multi-GB sessions are fine (the bundle streams) up to the
plan's size cap — guest/free 2 GB, paid 12 GB; beyond that, Dø Desktop
converts locally with no upload.

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
the result `file` URL (a direct storage link — no proxy, multi-GB safe).
Directions are `<source>2<target>` over logic | ableton | fl | protools |
reaper | cubase | dorico, `auto2<target>` to let the server detect the
source, or `<daw>2<daw>` to rebuild a project in its own format (e.g. with
`options.third_party_plugins:"disable"`). Zip a project FOLDER so its audio
travels. Pass `size_bytes` to the upload tool: past 4 GB it hands you a
multipart upload (`split -b <part_size>`, PUT each part, then
`doseedo_complete_project_upload`). The finished task carries the transfer
report PARSED — `lossy`, `summary[]` (what changed), `warnings[]` (before
opening), `report_url` — relay every line; a missing report is not
"lossless".

## Edit a project, not just convert it

`doseedo_import_project {project_key}` → a `session_id` for the session
tools (tempo, meter, markers, every track with its MIDI, level and pan;
audio files are LISTED with their clip positions, not carried — the result's
`audio.next` says how to supply them). Edit with `doseedo_edit_session`,
save with `doseedo_download_session` (native Logic), and for another DAW
upload that download and run `doseedo_convert_project logic2<target>` — the
converter takes an uploaded project, never a session_id. Recipe:
`doseedo_recipes {name:"import-edit-export"}`.

## Failures

`503` — the converter is cold-starting; retry in a moment. `project_too_large`
(HTTP 413) — the project is over the SIZE cap of the plan (guest/free 2 GB,
paid 12 GB); the message carries the cap and an upgrade link. The CLI and the
web share that cap — the way around it is local conversion in Dø Desktop
(https://doseedo.com/downloads), the way up is the plan. `429` — the monthly
allowance is used up; the message names the reset and
https://doseedo.com/plans. `400 could not read the project` — wrong input
kind (see the table above). `400 invalid_direction` — the error lists the
directions the server accepts. Quote the `support_code` when a failure
carries one.
