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
