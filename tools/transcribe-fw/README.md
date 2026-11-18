# transcribe-fw — faster-whisper SRT lane (filed into videopress Nov 18, 2026)

Local, offline transcription to per-line SRT. Use it wherever an SRT or a
verified transcript is needed: ReadDash caption files (replaces the Gemini
SRT route — no upload, no quota, no per-call cost), source-clip transcripts
before scripting commentary, and "what was actually said" checks.

## How
```bash
python3 -m venv venv && venv/bin/pip install faster-whisper "av==14.2.0"
venv/bin/python tools/transcribe-fw/transcribe_fw.py <media> [--model small] [--out out.srt] [--pause 0.8]
```
- **Pin `av==14.2.0`.** faster-whisper 1.2.1 calls `av.open(metadata_errors=...)`,
  which PyAV ≥15 removed — unpinned installs crash on the first transcribe.
- Word timestamps are always on; lines are regrouped at pauses >0.8s
  (raw whisper segments merge across pauses and are too coarse for captions).

## Measured evidence (Nov 18, 2026, this VM: 1.5 vCPU, no GPU)
Test clip: ReadDash story 073 "A Little Seed" render (46.96s, 1080×1920,
narration + music bed) with its known-good SRT as ground truth.
- **Accuracy: WER 0.000** — 47/47 words exact vs the ground-truth SRT.
- **Speed: 6.4s for 47s of audio (RTF 0.136)** with `small` int8; model
  download ~460MB once, load ~5s after.
- **Line timing:** word-regrouped output reproduced all 10 ground-truth
  lines, timings within ~0.3s.
- Install is ctranslate2-only (~150MB) — no PyTorch, unlike the OpenAI
  `whisper` package behind `lib/transcribe.py`.

## Verdict
**ADOPT** as the default SRT/transcription lane. `lib/transcribe.py`
(OpenAI Whisper + torch) stays as a fallback; this is faster, lighter, and
measured word-perfect on our own material. Full trial data:
~/workspace/videopress-tests/ (input, outputs, logs).
