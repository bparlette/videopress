#!/usr/bin/env bash
# Usage: clip_vertical.sh <src> <start-sec> <dur-sec> <out.mp4>
# Centre-crop to 9:16, lanczos-scale to 1080x1920, source audio, faststart.
# NO burned-in text/captions — owner's hard rule for Shorts.
# Handles both source orientations (portrait fix, Nov 24, 2026):
#   source at least as wide as 9:16 (landscape, square, mild portrait):
#     crop full height to 9:16, then scale — the original filter chain.
#   source taller than 9:16 (e.g. 780x1688 phone captures): the crop width
#     ih*9/16 exceeds the frame width and ffmpeg aborts, so scale to width
#     1080 first, then centre-crop 1080x1920 (the proven clip_portrait math).
set -euo pipefail
read -r iw ih < <(ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height -of csv=p=0 "$1" | tr ',' ' ')
if [ $(( iw * 16 )) -ge $(( ih * 9 )) ]; then
  vf="crop=ih*9/16:ih,scale=1080:1920:flags=lanczos"
else
  vf="scale=1080:-2:flags=lanczos,crop=1080:1920"
fi
ffmpeg -y -v error -ss "$2" -i "$1" -t "$3" \
  -vf "$vf" \
  -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 160k \
  -movflags +faststart "$4"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$4"
