# yt-clip — long video → vertical Shorts (filed into videopress Nov 17, 2026)

The clipping pipeline proven end-to-end in the Nov 17 trial of the @RoundtableSpace stack. Use it when a long video (YouTube gameplay, a livestream VOD, a local capture) needs to become vertical Shorts. For videopress's own manufactured trend episodes, the main `videopress make` flow still rules — this is the CLIPPING lane.

## The pipeline
1. **Download** — `yt-dlp --extractor-args "youtube:player_client=android"` (the ONLY client family that passes YouTube's bot check from an unauthenticated machine; ios/tv/web are bot-walled). Section-download with `--download-sections "*0:00-15:00"` for the part you need.
   - **HARD CEILING: the android client exposes only 360p (format 18).** No 720p+ without authenticated cookies. YouTube-sourced clips are therefore honest upscales — framing/cuts/sync are provable, sharpness is not. **Fed a local 1080p+ recording, the same pipeline is native quality.** Prefer local captures (game recordings) whenever they exist.
2. **Detect** — `detect_scenes.py <video> <workdir>`: builds a 320px proxy with ffmpeg, runs PySceneDetect ContentDetector (threshold 27) on the PROXY (boundaries transfer to the original within ~0.1s), then scores per-scene motion in ONE sequential decode pass (seek-sampling at full res is far too slow on a small box). Outputs `scenes.csv` + `scenes.json` (start/end/duration/motion).
3. **Triage** — `contact_sheet.py <workdir>`: one frame at every detected cut, labelled with scene # and start time. Read the sheet + the motion scores and pick scenes by eye + numbers (long, high-motion, self-contained).
4. **Clip** — `clip_vertical.sh <src> <start> <dur> <out.mp4>`: ffmpeg centre-crop → lanczos scale to 1080x1920, source audio AAC 160k, faststart. **NO burned-in text or captions — ever** (owner's hard rule for Shorts; variants differ by angle/cut, never by words on screen). Verify every output with ffprobe (video vs audio duration, fps) before calling it done — measure the delivered file, never repeat a spec sheet.

## Tool verdicts (measured in the trial)
- **yt-dlp:** works (android client only); 360p ceiling without cookies.
- **PySceneDetect 0.7.3:** the keeper. Install into a venv (system pip is PEP-668-locked on some boxes); `opencv-python-headless` substitutes for the GUI build. 69 scenes found in a 15-min GTA V video; the contact sheet alone shows the video's whole shape at a glance.
- **Remotion 4.x:** toolchain fully works (npm install, bundling, Headless Shell download, real renders) BUT ~2-2.4 s/frame on a small shared VM → a 30s Short ≈ 30-36 min. Use for short/templated pieces on an idle machine, not bulk clipping. The ffmpeg path above uses identical crop math.
- **WhisperX:** optional; its only rule-compliant use here is drafting titles/descriptions (never burned-in captions).
- **n8n:** glue only — adds automation, no capability. A cron + these scripts does the same. Adopt last, if ever; automating before the quality bar is proven just scales mediocrity.

## Trial evidence (Nov 17, 2026)
Source: 'GTA 5 — PS5 Gameplay' (Section Plays, 49:16; first 15:00 used). Three Shorts delivered, ffprobe-measured: 40.4s / 27.5s / 40.0s, 1080x1920, A/V sync within 0.007s, zero burned-in text. Full trial README + outputs live in the trial workspace; the scripts here are the generalised versions of the exact code that ran.
