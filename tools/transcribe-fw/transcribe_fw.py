#!/usr/bin/env python3
"""transcribe_fw.py — media -> per-line SRT with faster-whisper (CPU, int8).

Usage: python3 transcribe_fw.py <media.mp4|mp3|wav> [--model small] [--out out.srt] [--pause 0.8]

Why this exists (measured Nov 18, 2026 — see README.md): faster-whisper's
`small` model on CPU int8 transcribed a 47s narrated clip word-perfect
(WER 0.000 vs the known-good SRT) at RTF 0.14 (~7x realtime) on a 1.5 vCPU
VM, with NO PyTorch install (ctranslate2). Raw segments are too coarse for
captions (3 blocks for 10 spoken lines), so this script always uses word
timestamps and regroups words into lines at pauses > --pause seconds,
which reproduced the ground-truth SRT's 10 lines and timings.

Install (pin matters — faster-whisper 1.2.1 breaks against PyAV >= 15):
  python3 -m venv venv && venv/bin/pip install faster-whisper "av==14.2.0"
"""
import argparse, sys, time
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("media")
ap.add_argument("--model", default="small")
ap.add_argument("--out", default=None)
ap.add_argument("--pause", type=float, default=0.8, help="new SRT line after a pause longer than this (s)")
ap.add_argument("--lang", default=None)
a = ap.parse_args()

OUT = a.out or a.media.rsplit(".", 1)[0] + ".srt"

t0 = time.time()
model = WhisperModel(a.model, device="cpu", compute_type="int8")
print(f"model {a.model} loaded in {time.time()-t0:.1f}s", file=sys.stderr)

t1 = time.time()
segments, info = model.transcribe(a.media, language=a.lang, beam_size=5,
                                  vad_filter=True, word_timestamps=True)
words = [w for s in segments for w in (s.words or [])]
dur = info.duration
print(f"transcribed {dur:.1f}s of audio in {time.time()-t1:.1f}s "
      f"(RTF {(time.time()-t1)/max(dur,1):.3f}), lang={info.language}", file=sys.stderr)

lines, cur, last_end = [], [], None
for w in words:
    if last_end is not None and w.start - last_end > a.pause and cur:
        lines.append(cur); cur = []
    cur.append(w); last_end = w.end
if cur:
    lines.append(cur)

def ts(s):
    return (f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d},"
            f"{int(round((s-int(s))*1000)):03d}")

with open(OUT, "w") as f:
    for i, ln in enumerate(lines, 1):
        text = "".join(w.word for w in ln).strip()
        f.write(f"{i}\n{ts(ln[0].start)} --> {ts(ln[-1].end)}\n{text}\n\n")

print(f"wrote {OUT}: {len(lines)} lines, {len(words)} words")
