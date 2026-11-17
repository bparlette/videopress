#!/usr/bin/env bash
# Usage: clip_vertical.sh <src> <start-sec> <dur-sec> <out.mp4>
# Centre-crop to 9:16, lanczos-scale to 1080x1920, source audio, faststart.
# NO burned-in text/captions — owner's hard rule for Shorts.
set -euo pipefail
ffmpeg -y -v error -ss "$2" -i "$1" -t "$3" \
  -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos" \
  -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 160k \
  -movflags +faststart "$4"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$4"
