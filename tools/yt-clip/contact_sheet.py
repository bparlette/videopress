#!/usr/bin/env python3
"""Usage: contact_sheet.py <workdir> — one frame at each detected cut (from the
proxy, sequential decode), labelled with scene number + start time."""
import json
import cv2
import numpy as np

import sys
W = sys.argv[1]  # workdir holding proxy.mp4 + scenes.json
data = json.load(open(f"{W}/scenes.json"))
scenes = data["scenes"]
starts = {round(s["start"], 2): s["scene"] for s in scenes}

cap = cv2.VideoCapture(f"{W}/proxy.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
thumbs = {}
fnum = 0
pending = sorted(starts.items())
pi = 0
while pi < len(pending):
    ok, frame = cap.read()
    if not ok:
        break
    t = fnum / fps
    while pi < len(pending) and t >= pending[pi][0] + 0.3:
        thumbs[pending[pi][1]] = cv2.resize(frame, (160, 90))
        pi += 1
    fnum += 1
cap.release()

cols, tw, th, lh = 8, 160, 90, 16
rows_n = (len(scenes) + cols - 1) // cols
sheet = np.zeros((rows_n * (th + lh), cols * tw, 3), dtype=np.uint8)
for s in scenes:
    n = s["scene"]
    r, c = divmod(n - 1, cols)
    y, x = r * (th + lh), c * tw
    if n in thumbs:
        sheet[y:y + th, x:x + tw] = thumbs[n]
    cv2.putText(sheet, f"#{n} {s['start']:.1f}s", (x + 3, y + th + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 0), 1, cv2.LINE_AA)
cv2.imwrite(f"{W}/contact-sheet.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
print(f"contact sheet: {len(thumbs)}/{len(scenes)} thumbs, {sheet.shape[1]}x{sheet.shape[0]}")
