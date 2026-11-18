# stems — Demucs stem separation (filed into videopress Nov 18, 2026)

Split a finished mix into vocals / drums / bass / other. The pipeline use:
**isolate narration from a music bed** — pull clean speech out of a render
or a source clip so it can be re-timed, re-mixed, transcribed, or fed to a
silence cutter (a separated vocals track has true silence between lines,
which is exactly what auto-editor needs and a music bed defeats).

## How
```bash
bash tools/stems/separate_stems.sh <media> <outdir>
# -> <outdir>/htdemucs/in/{vocals,drums,bass,other}.wav
```
Install (CPU torch index keeps it ~200MB instead of the multi-GB CUDA stack):
```bash
python3 -m venv venv
venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch
venv/bin/pip install demucs numpy   # numpy is a real runtime dep pip may skip
```

## Measured evidence (Nov 18, 2026, this VM: 1.5 vCPU, no GPU)
Test clip: ReadDash story 073 render (46.96s, narration over a music bed).
- **Separation:** in an inter-line gap the original mix measures −28.4 dB
  mean (the bed); the vocals stem measures **−91.0 dB (silence)** there —
  the bed is simply gone between lines.
- **Speech intact:** faster-whisper on the vocals stem scores **WER 0.000**
  vs the known-good SRT — nothing spoken was lost or garbled.
- **Cost:** 2m28s wall for 47s of audio (~3.1× realtime) incl. model fetch.
  Fine for clip-length work; budget ~3× duration for long VODs.

## Verdict
**ADOPT** as an audio utility lane. Note: DeepFilterNet was the first pick
for speech cleanup but is **not installable here** — no wheel for
Python 3.12 (source build demands a Rust toolchain). Demucs covers the
actual pipeline need (bed removal) better anyway. Full trial data:
~/workspace/videopress-tests/.
