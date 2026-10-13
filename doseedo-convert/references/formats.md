# Formats and directions

Directions are `<source>2<target>`; every ordered pair of
`logic | ableton | fl | protools | reaper | cubase | dorico` is accepted, and:

- `garageband` is a SOURCE only, to any of those seven (nothing writes a `.band`);
- `bitwig` (= any `.dawproject`) pairs both ways with all seven;
- `studioone` pairs both ways with logic, ableton, fl, protools, reaper and
  cubase — no Dorico leg;
- there is no Studio One ↔ Bitwig and no GarageBand → Studio One / Bitwig,
  and no same-format rebuild (`<daw>2<daw>`) for Cubase, Dorico, Studio One
  or Bitwig. `auto2<target>` works for every target.

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
| GarageBand | `.band` package (GarageBand 10 / iOS; zip it like a `.logicx`): tracks, MIDI notes, tempo/meter, mutes and faders, audio regions | — (source only) | Apple's instrument SOUNDS do not travel (notes + patch name only); region loops are placed once; Apple Loops kept outside the project arrive as offline clips; a GarageBand 6 ('11) project must be re-saved in GarageBand 10 first; iOS projects are untested on real files |
| Studio One / Fender Studio Pro | native `.song` (bare, or the song folder with `Media/`): tracks, audio events, MIDI, tempo/meter maps, markers, mixer volume/pan/mute, sends, third-party plugin identity + state; Pro EQ → EQ Eight with its settings; other Studio One built-ins by name only | **`.dawproject`** | Studio One 6.5+ imports it (File > Import) — not yet verified by opening in Studio One itself |
| Bitwig Studio | any **`.dawproject`** (Bitwig 5+, Studio One 6.5+, Cubase 14+ export it): tracks incl. groups, clips, notes, audio, tempo/meter, markers, mixer, sends, plugins with state, built-in EQ / compressor / gate / limiter | **`.dawproject`** | Bitwig built-in instruments, CLAP plugins and clip gain are reported as lost. A native `.bwproject` is not read (export DAWproject from Bitwig). Bitwig 5+ imports the output — not yet verified by opening in Bitwig itself |

## Why the asymmetry

Reading a format only needs the fields we recognise; writing one needs every
field the app validates. `.cpr`, `.song`, `.bwproject` and `.dorico` have no
public specification. A native file the app refuses to open looks like a
conversion and is a dead end, so those targets get the interchange file each
app imports natively instead (DAWproject for Cubase, Studio One and Bitwig;
MusicXML for Dorico). Everything else is written native.

## Defaults the CLI applies

- `--to` omitted: Logic → Ableton; every other source → Logic.
- Output name: `<project name>.logicx.zip` / `.als` / `<name> FL.zip` /
  `<name> REAPER.zip` / `<name> Pro Tools.zip` / `<name> Cubase.dawproject` /
  `<name> Studio One.dawproject` / `<name> Bitwig.dawproject` / `<name>.mxl`;
  the server may suggest a better name, which is honoured unless `--out` was
  given.
- A pair the converter does not serve (e.g. `--to bitwig` from a `.song`) is
  refused before anything is uploaded; a native `.bwproject` likewise.
- `--project-rate 48000` pins the Logic project sample rate (default: the
  highest clip rate; off-rate clips are resampled by Logic).
