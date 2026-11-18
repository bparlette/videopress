# Film-it previz lane — record the camera move, Omni re-renders it real

**Verdict (trial 2026-11-17, from Spoken World): ADD as a previz lane.**
Videopress's existing pipeline only *finds* moments in footage that
already exists (yt-clip / PySceneDetect / ffmpeg). This lane creates the
shot before it exists: **record a camera move in a 3D scene, then a video
model (Gemini Omni) re-renders the clip as live-action footage, keeping
the camera move.** Use it to previz Shorts — above all Lanternport's
main goal, viral Shorts shot FROM the game world for the GTA VI launch —
before committing to a full build or a capture session.

Source pattern: Spoken World's film-it mode (Apache-2.0 app; the repo
ships previz/real example pairs). Trial report:
`~/workspace/trials-2026-11-17/spoken-world/REPORT.md`. The gamepress
half of that trial — the invent pattern — is filed in gamepress as
`docs/INVENT-PATTERN.md`.

## The lane, step by step

1. **Stage the move in 3D.** Place cameras in a lightweight Three.js
   scene — or in the game itself where it supports it (Palm City /
   Lanternport camera work) — and record the clip in-world. Spoken
   World's cap is ≤10 s per clip; treat that as the working length:
   a Short's moment is one move, not a sequence.
2. **Re-render with Omni.** Send the clip through the Gemini video lane
   (Omni 1.1 Flash — the standing Gemini routing for generated video)
   with the instruction to re-render as live-action footage, camera
   move preserved. What comes back is the *previz*: the shot's framing,
   timing, and feel, at final-look fidelity.
3. **Decide on the previz.** Approve, re-stage, or kill the shot while
   it still costs minutes. An approved previz becomes the spec for the
   real capture: same move, same timing, shot from the actual game.
4. **Shoot the real thing for the actual Short** — unless the owner
   rules a given piece is Omni-final. The standing QC rule holds:
   real clips are the backbone; generated footage is not a substitute
   for gameplay capture.

## Where it fits — and where it doesn't

- **Fits:** planning a Short's hero shot before the set-piece exists;
  testing whether a camera move reads at 9:16 phone size; giving a
  builder (or Gemini's recording lane) an exact move to reproduce.
- **Doesn't fit:** finding moments in existing footage (that's the
  yt-clip lane), bulk production (per-clip model calls don't scale
  like ffmpeg), or anything where the game's real look IS the claim —
  previz fidelity is the model's interpretation, not the game's pixels.
- **Cost/latency note from the trial:** the host app's model calls on
  gemini-4-hydrogen were capacity-spiky in launch week (3 of 9 calls
  503'd; 21–142 s per call). Budget retries into any scheduled run,
  and keep private material out of prompts on a free-tier key.
