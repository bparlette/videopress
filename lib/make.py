#!/usr/bin/env python3
"""videopress make — build a viral-format episode from a manifest.

Usage: python3 make.py episode.json

Manifest schema (see examples/episode.json):
{
  "clips_dir": "clips_raw",          # <id>.mp4 files
  "vo_dir": "vo",                    # vo1.mp3, vo2.mp3...
  "output": "episode.mp4",
  "width": 1280, "height": 720, "fps": 30,
  "beats": [                         # edit decision list
    {"clip": "abc123", "start": 0.5, "dur": 4.0, "caption": "TEXT", "caption_pos": "top"},
    ...
  ],
  "vo_place": [                      # (vo_file, beat_index, offset)
    {"file": "vo1.mp3", "beat": 0, "offset": 0.2}
  ]
}

Output: 1280x720 @30fps. Real clips with blurred pillarbox (no stretch),
sparse captions, VO mixed over native audio. No title card, no end card.
"""
import json
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

MANIFEST = sys.argv[1]
with open(MANIFEST) as f:
    M = json.load(f)

BASE = os.path.dirname(os.path.abspath(MANIFEST))
CLIPS = os.path.join(BASE, M.get("clips_dir", "clips_raw"))
VO = os.path.join(BASE, M.get("vo_dir", "vo"))
OUT = os.path.join(BASE, M.get("output", "episode.mp4"))
W, H, FPS = M.get("width", 1280), M.get("height", 720), M.get("fps", 30)
FONT = M.get("font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
TMP = os.path.join(BASE, ".vp_tmp")
os.makedirs(TMP, exist_ok=True)


def run(*a):
    subprocess.run(a, check=True)


def ffprobe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1", path],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out.split("=")[-1])


def font_for(text, max_w, start=120):
    size = start
    while size > 40:
        f = ImageFont.truetype(FONT, size)
        bb = ImageDraw.Draw(Image.new("RGB", (8, 8))).textbbox(
            (0, 0), text, font=f, stroke_width=max(2, size // 14))
        if bb[2] - bb[0] <= max_w:
            return f
        size -= 8
    return ImageFont.truetype(FONT, 40)


def caption_png(text, pos, idx):
    """Burn a caption overlay PNG for one beat."""
    p = os.path.join(TMP, f"cap_{idx}.png")
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font_for(text, W - 120)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=4)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (W - tw) // 2
    y = 60 if pos == "top" else H - th - 80
    # shadow + white text with black stroke
    d.text((x + 4, y + 4), text, font=f, fill=(0, 0, 0, 220))
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255),
           stroke_width=4, stroke_fill=(0, 0, 0, 255))
    im.save(p)
    return p


def build_beat(i, beat):
    """Cut one clip segment, scale/pad to WxH, overlay caption."""
    src = os.path.join(CLIPS, beat["clip"] + ".mp4")
    seg = os.path.join(TMP, f"seg_{i}.mp4")
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        # punch-in zoom: subtle zoom over the segment
        f"zoompan=z='1+0.06*on/{int(beat['dur'] * FPS)}':d={int(beat['dur'] * FPS)}:s={W}x{H}:fps={FPS}"
    )
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-ss", str(beat.get("start", 0)), "-t", str(beat["dur"]),
           "-i", src, "-vf", vf, "-r", str(FPS),
           "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-an", seg]
    if beat.get("caption"):
        cap = caption_png(beat["caption"], beat.get("caption_pos", "top"), i)
        cmd = ["ffmpeg", "-y", "-v", "error",
               "-ss", str(beat.get("start", 0)), "-t", str(beat["dur"]),
               "-i", src, "-i", cap,
               "-filter_complex",
               f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
               f"zoompan=z='1+0.06*on/{int(beat['dur'] * FPS)}':d={int(beat['dur'] * FPS)}:s={W}x{H}:fps={FPS}[bg];"
               f"[bg][1:v]overlay=0:0",
               "-r", str(FPS), "-c:v", "libx264", "-preset", "fast", "-crf", "20",
               "-an", seg]
    run(*cmd)
    return seg


def main():
    beats = M["beats"]
    segs = [build_beat(i, b) for i, b in enumerate(beats)]

    # concat video
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    vonly = os.path.join(TMP, "video.mp4")
    run("ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", lst, "-c", "copy", vonly)

    # mix VO over native audio at beat offsets
    total = sum(b["dur"] for b in beats)
    inputs = ["-i", vonly]
    fc_parts = []
    for j, vp in enumerate(M.get("vo_place", [])):
        vofile = os.path.join(VO, vp["file"])
        # offset = sum of beat durations before this beat + offset
        off = sum(b["dur"] for b in beats[:vp["beat"]]) + vp.get("offset", 0)
        inputs += ["-i", vofile]
        fc_parts.append(f"[{j + 1}:a]adelay={int(off * 1000)}|{int(off * 1000)}[vo{j}]")
    if fc_parts:
        # native audio at 0.35, VO at 1.0
        amix = "".join(fc_parts) + "".join(f"[vo{j}]" for j in range(len(fc_parts)))
        amix += f"amix=inputs={len(fc_parts)}:normalize=0[vox];[0:a]volume=0.35[nat];[vox][nat]amix=inputs=2:normalize=0[aout]"
        run("ffmpeg", "-y", "-v", "error", *inputs,
            "-filter_complex", amix, "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k", "-shortest", OUT)
    else:
        run("ffmpeg", "-y", "-v", "error", "-i", vonly,
            "-c", "copy", OUT)

    print(f"wrote {OUT} ({total:.1f}s, {len(beats)} beats)")


main()
