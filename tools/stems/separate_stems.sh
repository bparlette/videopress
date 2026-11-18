#!/usr/bin/env bash
# separate_stems.sh — split a clip's audio into vocals / drums / bass / other
# with Demucs (htdemucs, CPU). Filed Nov 18, 2026 — see README.md.
#
# Usage: separate_stems.sh <media-or-audio-file> <outdir>
# Needs: a venv with demucs + CPU torch + numpy, e.g.
#   python3 -m venv venv
#   venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch
#   venv/bin/pip install demucs numpy
# Point DEMUCS_PY at that venv's python if it isn't on PATH as `demucs`.
set -euo pipefail
SRC="${1:?usage: separate_stems.sh <media> <outdir>}"
OUT="${2:?usage: separate_stems.sh <media> <outdir>}"
PY="${DEMUCS_PY:-python3}"
TMP="$(mktemp -d)"
# Demucs separates audio; normalise any input to 44.1k stereo wav first.
ffmpeg -y -v error -i "$SRC" -vn -c:a pcm_s16le -ar 44100 -ac 2 "$TMP/in.wav"
"$PY" -m demucs -d cpu -o "$OUT" "$TMP/in.wav"
rm -rf "$TMP"
echo "stems in $OUT/htdemucs/in/ (vocals.wav = isolated speech/voice)"
