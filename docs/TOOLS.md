# Video manufacturing tools — how and when to use each

Reference for an AI agent manufacturing short-form video. Only specialized tools are listed — general capabilities (web search, file I/O, code execution) are assumed.

## Kokoro TTS (local neural voice)
- **What:** Open-weight text-to-speech, runs fully offline. ~54 voices, quality close to commercial APIs.
- **When:** Any voiceover where you control the machine and want zero per-character cost. Pick a voice that fits the format (bright/fast for viral, warm/slow for narration).
- **How:** `pip install kokoro`, load the ONNX model, `kokoro.generate(text, voice="af_sky", speed=1.0)`. Speed 1.05–1.15 for punchy Shorts pacing, 0.85–1.0 for narration.
- **Watch out:** Numbers and abbreviations need expanding ("12M" → "twelve million") or they get read literally.

## Edge TTS (Microsoft, free cloud)
- **What:** Microsoft's neural voices via a free endpoint. Huge voice catalog, no API key.
- **When:** You need a specific voice character Kokoro doesn't have, or bulk-generating hundreds of short lines (game barks, reaction clips).
- **How:** `pip install edge-tts`, `edge-tts --voice en-US-AriaNeural --text "..." --write-media out.mp3`. List voices with `edge-tts --list-voices`.
- **Watch out:** It's an unofficial endpoint — rate-limit yourself, and check the licensing terms for your use case.

## ffmpeg (assembly, encoding, captions)
- **What:** The universal video/audio Swiss-army knife.
- **When:** Cutting clips, concatenating segments, mixing voiceover over native audio, burning captions, scaling/padding to platform aspect ratios, final encode.
- **How:**
  - Cut: `ffmpeg -ss 0.5 -t 4.0 -i in.mp4 -c copy seg.mp4`
  - Concat: list segments in `list.txt`, `ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4`
  - Mix VO over native: `adelay` the VO to its timestamp, `amix` with native audio dropped to ~0.35 volume
  - Pad 9:16 to 16:9: scale + blurred background copy, never stretch
  - Encode for upload: `-c:v libx264 -preset fast -crf 20 -c:a aac -b:a 128k`
- **Watch out:** Always verify durations with `ffprobe` after assembly — silent drift breaks caption sync.

## PIL / Pillow (thumbnails, caption overlays)
- **What:** Python imaging for generating thumbnails and caption PNGs to overlay.
- **When:** Building thumbnails (text + scrim + background), burning word-by-word caption cards, any raster text-on-image work.
- **How:** `ImageDraw.text` with `stroke_width` for outline text; fit font size by measuring `textbbox` against max width; always test thumbnails at 120px wide.
- **Watch out:** Default fonts are ugly — bundle DejaVuSans-Bold or better. ffmpeg's `drawtext` chokes on apostrophes; render captions as PNGs instead.

## yt-dlp (source clips)
- **What:** Download video/audio from YouTube, TikTok, and hundreds of sites.
- **When:** Pulling reference clips, trend videos, or reaction footage for transformative montage work.
- **How:** `yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" URL -o "%(id)s.%(ext)s"`. If YouTube throws a bot check, add `--extractor-args "youtube:player_client=android"`.
- **Watch out:** Only download what you have the right to transform. Credit every source in the description.

## YouTube Data API v3 (upload)
- **What:** Programmatic upload, thumbnails, metadata. No browser needed.
- **When:** Publishing finished videos. The `youtube.upload` OAuth scope covers upload + thumbnail set — nothing else.
- **How:** Refresh token → access token → resumable upload session → PUT bytes → `thumbnails/set`. One refresh token per channel — run the OAuth consent flow once per brand account and store tokens separately (600-perm files, never in the repo).
- **Watch out:** Playlist adds 403 under the upload-only scope — add to playlists manually. Verify the active channel before every upload; OAuth consent defaults to the personal channel, not the brand account.

## Whisper (transcription) — ACTIVE
- **What:** OpenAI's open-weight speech-to-text, runs locally. ~1GB installed (PyTorch is the bulk).
- **When:** Transcribing source clips *before* scripting commentary around them — the audio-first workflow. Also generates caption timing and verifies what was actually said in a clip.
- **How:** `videopress transcribe clip.mp3` (or `--model small` for better accuracy). Writes `.srt` + prints the transcript. Models: base ~140MB (fast, good enough for captions), small ~460MB, medium ~1.5GB (diminishing returns).
- **Watch out:** Base model is fast and good enough for captions; large is slower with marginal gains for this use.
- **Update (Nov 18, 2026):** `tools/transcribe-fw/` (faster-whisper, CPU int8) measured faster and lighter than this torch-based path — WER 0.000 at RTF 0.14 on a real render — and is now the default SRT lane. This entry stays as the fallback. See the mined section at the end of this file.

## Remotion (code-driven video) — ACTIVE
- **What:** React-based programmatic video — write components, render MP4. ~300–500MB node_modules.
- **When:** Kinetic typography, animated explainers, or any motion design where ffmpeg's static captions feel flat. Reach for it when the motion design IS the content.
- **How:** Copy `templates/remotion-kinetic/`, edit the `words` array in `src/index.tsx`, `npm install`, `npx remotion render Kinetic out.mp4`. The template does per-word spring punch-ins on 9:16.
- **Watch out:** Overkill for simple montages — ffmpeg + PIL still win for straightforward caption burns.

## Gemini image generation (free API tier)
- **What:** `gemini-2.5-flash-image` via the Gemini API free tier — text-to-image, no cost.
- **When:** Thumbnails backgrounds, scene stills, character reference art, any raster image you need fast. Quality is strong for cartoon/illustrated styles.
- **How:** POST to `generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent` with `{"contents":[{"parts":[{"text":"your prompt"}]}]}`. The response's `inlineData` parts hold base64 PNGs — decode and save.
- **Watch out:** Photorealism lags the paid image models. Prompt precisely for style ("hand-drawn, flat colors") — vague prompts drift.
## OpenFilm (AI video agent — HTML-shot films with an editor)
- **What:** Open-source (MIT) tool that turns a coding agent into a video agent: every shot of a film is an HTML/CSS page the agent writes (images, animation, transitions), the shots assemble into a full video, and a built-in editor lets a human drag the timeline, edit text and retime shots afterwards, then export MP4. Repo: github.com/openfilm/openfilm (~7,000 stars, verified Nov 14, 2026). Windows + macOS.
- **When:** AUTHORED shot-based films — ReadDash story films, AiDiaries episodes, narrative set pieces. It is the Crimson Loong pattern productized, plus the editable-after-generation timeline our capture pipeline lacks.
- **How:** Clone the repo, drive it with the coding agent per its README; shots are plain HTML/CSS, so any scene we can build as a web page is a shot.
- **Watch out:** NOT for game footage — game trailers and Shorts still use real captured gameplay (REAL-ASSETS rule). The editor is the win; generation quality is only as good as the shot pages you write.

## Clipping pipeline (long-form video → a week of Shorts)
- **What:** A five-tool open-source stack for mining long recordings (podcasts, interviews, streams) into short clips: WhisperX (word-level timestamp transcription + speaker diarization), PySceneDetect (scene-cut detection), Auto-Editor (silence/dead-air removal), Remotion (programmatic clip assembly), FFmpeg (render plumbing). All permanently free; Remotion is free for individuals/small teams. Surfaced via @RoundtableSpace, Nov 14, 2026 ("GTA 6 clipping demon" stack).
- **When:** Only when a LONG source exists. Our game Shorts never use it — they come from deterministic capture of real gameplay.
- **How — the AiDiaries viral method:** the long-form source is Moth's own recorded work (build sessions, day-in-the-life narration). (1) WhisperX the session and scan the transcript for the strongest standalone lines — the hook is a line, not a topic. (2) Cut 5–7 candidate clips around those lines, strongest line FIRST (never chronological). (3) Auto-Editor strips every dead pause; PySceneDetect keeps cuts on real scene changes. (4) Burn word-by-word captions from WhisperX timestamps — most Shorts are watched muted. (5) One idea per clip, end on a loop or a cliff. (6) Remotion/FFmpeg assemble and encode; one long session should feed a week of daily Shorts.
- **Watch out:** AiDiaries PRIVACY GATE applies before any clip is cut: the transcript passes the blocklist scan (never Cherie's tasks, schedules, family, personal data, emails or files) — a missed day beats a leaked detail. Virality levers in order: hook line, zero dead air, captions, volume.

## Film-it previz (camera move → Omni re-render)
- **What:** Previz a shot that doesn't exist yet: record a camera move in a 3D scene (≤10 s), Gemini Omni re-renders the clip as live-action footage, camera move preserved. Full lane doc: `docs/FILM-IT-PREVIZ.md` (added 2026-11-18).
- **When:** Planning Shorts — above all Lanternport's launch clips — before committing to a full build or capture session. Approve, re-stage, or kill the shot on the previz.
- **How:** Stage the move in Three.js or in the game itself → send through the Gemini video lane (Omni 1.1 Flash) with a re-render-as-live-action instruction → the previz becomes the spec for the real capture.
- **Watch out:** The previz is a planning spec, never the deliverable — real captured clips are the backbone of every published Short.

## Mined Nov 18, 2026 — @RoundtableSpace "20 repos" list, second pass (all four MEASURED on our own material)

Test material for every verdict below: ReadDash story 073 render (46.96s,
1080×1920, narration + music bed, known-good SRT as ground truth), run on
this VM (1.5 vCPU, no GPU). Full trial data: ~/workspace/videopress-tests/.

- **faster-whisper** — https://github.com/SYSTRAN/faster-whisper —
  **ADOPTED** as `tools/transcribe-fw/`. `small` int8: WER 0.000 vs the
  ground-truth SRT, RTF 0.136, word-timestamp regrouping reproduces the
  reference SRT line-for-line. Replaces the Gemini SRT route for ReadDash
  and is the default transcription lane (see the Whisper entry above).
  Gotcha: pin `av==14.2.0` — PyAV ≥15 breaks faster-whisper 1.2.1.
- **Demucs** — https://github.com/facebookresearch/demucs — **ADOPTED**
  as `tools/stems/`. htdemucs on CPU pulled the music bed out of the test
  render completely (gap level −28.4 dB → −91.0 dB on the vocals stem)
  with the narration still transcribing word-perfect; ~3.1× realtime.
  Use it to isolate voice before re-mixing, transcribing, or silence-cutting.
- **DeepFilterNet** — https://github.com/Rikorose/DeepFilterNet —
  **SKIP (not installable here).** No wheel for Python 3.12; the source
  build requires a Rust/Cargo toolchain. Demucs covers the pipeline's
  actual speech-cleanup need. Revisit only if a cp312 wheel ships.
- **auto-editor** — https://github.com/WyattBlue/auto-editor — **MARGINAL,
  not adopted.** Defaults found almost nothing to cut on the test render
  (46.96s → 46.13s): its silence threshold can't see "dead air" under a
  music bed (bed sits at −28 dB, only ~11 dB under speech). With the
  threshold tuned to 0.15 it cut 46.96s → 18.33s with every word intact
  (verified by transcription, WER 0.000) — but videopress's manufactured
  flow has no dead air by construction, and the clipping lane cuts by
  scene, not silence. Keep in mind for raw talking-head/VOD first passes
  (ideally after a Demucs vocals pass, which gives it true silence).
- **video-subtitle-remover** — https://github.com/YaoFANGUK/video-subtitle-remover —
  **SKIP (couldn't run here).** No PyPI distribution at all; source-only.
  The repo bundles its inpainting models: a git clone pulled ~50MB in
  6 min without finishing and the codeload zip was still incomplete at
  120MB/100s, before a ~260MB PaddlePaddle install and per-frame
  detection+inpainting at 1080×1920 on 1.5 vCPU. Not viable on this box
  within any reasonable budget — and our Shorts never burn text in, so
  the only use would be cleaning third-party source clips. Mac-side or
  GPU-box candidate if that need ever becomes real.
