# A drum kit from the user's own samples — worked example

The user has `/Users/me/Drums/{kick,snare,hat}.wav` and wants a Logic
session with a pattern. Nothing is uploaded: the cloud builds the session,
the download hands back copy commands that place the files.

```text
1. doseedo_create_session {name: "Trap kit"}                     → session_id
2. doseedo_edit_ops_reference                                     (read once)
3. doseedo_edit_session {session_id, ops: [
     {op:"set_tempo", args:{bpm:140}},

     {op:"add_track", args:{track_id:"t_1a2b3c4d5e6f", channel_id:"ch_1a2b3c4d5e6f",
                            name:"Kick", content_type:"instrument", auto_channel:true}},
     {op:"load_quick_sampler_sample", args:{track_id:"t_1a2b3c4d5e6f", slot:0,
                            sample_path:"/Users/me/Drums/kick.wav",
                            audio_info:{sample_rate:44100, frame_count:22050, channels:2,
                                        bits_per_sample:16, bytes:88244}}},   // header, see below
     {op:"set_midi_notes", args:{track_id:"t_1a2b3c4d5e6f", notes:[      // 0.5 s kick = 1.17 beats at 140
        {pitch:60, velocity:110, start_beats:0,   duration_beats:1.25},
        {pitch:60, velocity:100, start_beats:2,   duration_beats:1.25},
        {pitch:60, velocity:110, start_beats:4,   duration_beats:1.25},
        {pitch:60, velocity:100, start_beats:6.5, duration_beats:1.25}]}},
     {op:"set_channel_volume", args:{channel_id:"ch_1a2b3c4d5e6f", value:0.709}},

     … same four ops for Snare (t_…/ch_…) and Hat …

     {op:"add_channel", args:{channel_id:"ch_b_9f8e7d6c5b4a", name:"Drum Bus", role:"submix"}},
     {op:"set_channel_output", args:{channel_id:"ch_1a2b3c4d5e6f", target_channel_id:"ch_b_9f8e7d6c5b4a"}},
     … per member …
     {op:"set_channel_volume", args:{channel_id:"ch_b_9f8e7d6c5b4a", value:0.709}}
   ]}
4. doseedo_download_session {session_id}
   → download_url (no auth), replay, warnings, place_local_files
   VERIFY: replay.tracks has Kick/Snare/Hat with sampler_sample = the file
   name, sampler.plays_seconds = the file's length, midi_notes = 4 each;
   replay.deferred is empty and no warning says a sample is cut at note-off
   or has an unknown length.
5. curl -o ~/Downloads/Trap\ kit.logicx.zip "<download_url>"
   unzip → then run EVERY place_local_files command (cp … into
   Media/Samples/Quick Sampler/). Skip this and the samplers open empty.
```

**Note length vs. the sample.** Quick Sampler plays the WHOLE file (trim
with `sample_start_seconds` / `sample_end_seconds`). In mode `classic`
(default) the sample stops at note-off, so a note must be at least as long
as what should be heard: `frame_count / sample_rate` seconds × bpm/60 =
beats — `doseedo_get_session` shows it per sampler as `plays_beats`. For hits
that must always ring out whatever the note length, load with
`mode:"one_shot"`. To fix lengths afterwards, don't re-send the notes:
`edit_midi_notes {track_id, legato:true, max_duration_beats:<plays_beats>}`
(each note rings until the next, capped at the sample), or
`duration_beats` / `indices` / `pitches` for a subset.

One-shots as audio regions instead of a sampler: `add_track
{content_type:"audio"}` + `set_track_clips {clips:[{start_beats, end_beats,
name, audio_ref:{local_path, audio_info}}]}` where `audio_info` comes from
the header (the same `audio_info` a local `load_quick_sampler_sample` needs):

```bash
python3 -c 'import wave,os,json,sys; w=wave.open(sys.argv[1]); print(json.dumps({"sample_rate":w.getframerate(),"frame_count":w.getnframes(),"channels":w.getnchannels(),"bits_per_sample":w.getsampwidth()*8,"bytes":os.path.getsize(sys.argv[1])}))' hat.wav
```

Why this works: the Logic writer only ever needs an audio file's header and
size to lay out regions and wire samplers — the bytes are placed by the copy
commands on the user's machine. Audio leaves the device only when the server
genuinely has to hear it.
