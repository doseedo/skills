# Session ops — what `doseedo_edit_ops_reference` serves

Read the live catalog (`doseedo_edit_ops_reference`, also public at
`GET https://api.doseedo.com/api/session-ops`); this page is the map, not the
territory. Every op has `args`, a `group`, and `applies`:

- `live` — applied to the open Logic project by Dø Desktop within seconds
  (project open + desktop connected).
- `next_open` — persisted now; baked into the project when that session is
  next opened or rebuilt.
- `state` — recorded in the cloud session state only.

## Groups

| group | what | id it targets |
|---|---|---|
| project | tempo, meter | — |
| tracks | add / rename / delete / reorder tracks | `track_id t_…` |
| regions | audio regions (`attach_audio`, `set_track_clips`), MIDI notes (`set_midi_notes`), sampler content (`load_quick_sampler_sample`) | `track_id` |
| mixer | faders, pans, mutes, sends, buses (`add_channel role=submix\|return`, `set_channel_output`) | `channel_id ch_…` / `ch_b_…` |
| plugins | device chains on a strip (`add_device {device:{name}}`, slot) | `channel_id` + slot |
| automation | envelopes | `track_id` / `channel_id` |
| markers | arrangement markers | `m_…` |
| history | commits, `checkout` a commit | — |

## Recipes in the catalog (`recipes[]`)

1. **Drum kit in Quick Sampler from files on the user's Mac** — no upload, no
   desktop: `set_tempo` → per drum `add_track {content_type:"instrument",
   auto_channel:true}` → `load_quick_sampler_sample {sample_path:"/abs/kick.wav"}`
   → `set_midi_notes` (pitch 60) → `set_channel_volume 0.709`; download; run
   every `place_local_files` command.
2. **One-shots as audio regions on an audio track** — `add_track
   {content_type:"audio"}` → `set_track_clips` with `audio_ref {local_path,
   audio_info}` per hit.
3. **Sample that is NOT on this machine** — `doseedo_get_upload_url` → PUT →
   `doseedo_add_audio_to_session {audio_key}` → `load_quick_sampler_sample
   {sample_path: "<sha256>"}`; baked into the bundle server-side.
4. **Submix bus** — `add_channel {channel_id:"ch_b_…", role:"submix"}` →
   `set_channel_output {channel_id:"ch_<member>", target_channel_id:"ch_b_…"}`
   per member → `set_channel_volume`.
5. **Verify without unzipping** — `doseedo_download_session` → read
   `replay.tracks[*].sampler_sample / midi_notes / audio_regions`,
   `replay.deferred`, `warnings`; only then curl + unzip.

## Batching

One `doseedo_edit_session` call carries the whole build (up to 500 ops).
Ops apply in order, so `add_track` precedes the ops that target it. The tool
mints a `client_op_id` per op; the response gives each op a cursor.

## The MCP session tools

| tool | does |
|---|---|
| `doseedo_list_sessions` | sessions in the account |
| `doseedo_create_session {name}` | a new empty session |
| `doseedo_get_session {session_id}` | the arrangement summary + `sync` |
| `doseedo_edit_session {session_id, ops[]}` | apply ops |
| `doseedo_edit_ops_reference` | catalog + workflow + units + recipes |
| `doseedo_download_session {session_id, daw?}` | native project zip URL + `replay` + `warnings` + `place_local_files` |
| `doseedo_bounce_session {session_id}` | render tracks through their plugin chains (async, kind `bounce`) |
| `doseedo_desktop_status` | is Dø Desktop connected, which sessions, cursors |
| `doseedo_list_plugins` | stock palette + plugins installed on the desktop |
| `doseedo_add_audio_to_session {session_id, audio_url\|audio_key}` | server-fetch audio → sha256 for sampler / regions |
