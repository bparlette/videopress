#!/usr/bin/env python3
"""videopress transcribe — transcribe audio/video to SRT with word timing.

Usage: python3 transcribe.py <media.mp3|mp4> [--model base|small|medium] [--out out.srt]

Uses OpenAI Whisper locally. Use it to:
- Transcribe source clips before scripting commentary around them
- Generate caption timing for kinetic typography
- Verify what was actually said in a clip

Model sizes: base (~140MB, fast, good enough for captions),
small (~460MB, better accuracy), medium (~1.5GB, diminishing returns).
"""
import sys
import whisper

args = sys.argv[1:]
SRC = args[0]
MODEL = "base"
OUT = None
i = 1
while i < len(args):
    if args[i] == "--model" and i + 1 < len(args):
        MODEL = args[i + 1]; i += 2
    elif args[i] == "--out" and i + 1 < len(args):
        OUT = args[i + 1]; i += 2
    else:
        i += 1

if not OUT:
    OUT = SRC.rsplit(".", 1)[0] + ".srt"

print(f"loading whisper-{MODEL}...", file=sys.stderr)
model = whisper.load_model(MODEL)
print("transcribing...", file=sys.stderr)
result = model.transcribe(SRC, word_timestamps=True)


def ts(sec):
    h, m, s = int(sec // 3600), int(sec % 3600 // 60), sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


with open(OUT, "w") as f:
    n = 1
    for seg in result["segments"]:
        f.write(f"{n}\n{ts(seg['start'])} --> {ts(seg['end'])}\n{seg['text'].strip()}\n\n")
        n += 1

print(f"wrote {OUT} ({len(result['segments'])} segments)")
print("\n--- transcript ---")
print(result["text"].strip()[:500])
