# Formats and directions

Directions are `<source>2<target>`; every ordered pair of
`logic | ableton | fl | protools | reaper | cubase | dorico` is accepted.

## What each leg carries

| | read (source) | written (target) | notes |
|---|---|---|---|
| Logic Pro | `.logicx` package (zip it, or let the CLI) | native `.logicx` | tracks, regions, MIDI, tempo map, markers, automation, buses/sends, plugin state (with Ableton) |
| Ableton Live | `.als` + `Samples/` (pass the folder) | native `.als` | as above; a lone `.als` has no audio to embed |
| FL Studio | `.flp` (+ folder for audio) | native `.flp` | mixer FX map to Live-style devices where they exist |
| Pro Tools | `.ptx` session folder | native `.ptx` | pass the folder — a bare `.ptx` has no audio |
| REAPER | `.rpp` (+ folder) | native `.rpp` | |
| Cubase | native `.cpr`: tracks, tempo, signature, MIDI parts with tick-derived timing; **audio pool not decoded** (audio tracks arrive named but empty) | **`.dawproject`** (validated against the official 1.0 schema) | Cubase 14+/Nuendo import it as an editable session; Studio One and Bitwig read it too |
| Dorico | `.dorico` (players → tracks, flows → markers; **notes: 0** — the format exposes no note position/duration) **or** `.musicxml`/`.mxl` (the music) | **MusicXML `.mxl`** | export MusicXML from Dorico for anything musical; the same `dorico2*` directions accept it |

## Why the asymmetry

Reading a format only needs the fields we recognise; writing one needs every
field the app validates. `.cpr` and `.dorico` have no public specification.
A native file the app refuses to open looks like a conversion and is a dead
end, so those two targets get the interchange file each app imports
natively instead. Everything else is written native.

## Defaults the CLI applies

- `--to` omitted: Ableton → Logic; Logic → Ableton; FL / REAPER / Pro Tools →
  Logic.
- Output name: `<project name>.logicx.zip` / `.als` / `<name> FL.zip` /
  `<name> REAPER.zip` / `<name> Pro Tools.zip`; the server may suggest a
  better name, which is honoured unless `--out` was given.
- `--project-rate 48000` pins the Logic project sample rate (default: the
  highest clip rate; off-rate clips are resampled by Logic).
