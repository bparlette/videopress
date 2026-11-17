#!/usr/bin/env python3
"""Usage: detect_scenes.py <source-video> <workdir>
Builds a 320px proxy, runs PySceneDetect ContentDetector (threshold 27) on it,
then scores per-scene motion in one sequential decode pass.
Boundaries transfer to the original within ~0.1s."""
import csv, json
import cv2
from scenedetect import ContentDetector, SceneManager, open_video

import subprocess, sys
SRC, OUT = sys.argv[1], sys.argv[2]
PROXY = f"{OUT}/proxy.mp4"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC,
                "-vf", "scale=320:-2", "-an", PROXY], check=True)

video = open_video(PROXY)
sm = SceneManager()
sm.add_detector(ContentDetector(threshold=27.0))
sm.detect_scenes(video, show_progress=False)
scenes = sm.get_scene_list()
bounds = [(s.seconds, e.seconds) for s, e in scenes]
print(f"scenes={len(bounds)}")

# sequential motion pass over the proxy (no seeking)
cap = cv2.VideoCapture(PROXY)
fps = cap.get(cv2.CAP_PROP_FPS)
diff_sum = [0.0] * len(bounds)
diff_n = [0] * len(bounds)
prev = None
idx = 0
fnum = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    t = fnum / fps
    while idx < len(bounds) - 1 and t >= bounds[idx][1]:
        idx += 1
    gray = cv2.cvtColor(cv2.resize(frame, (160, 90)), cv2.COLOR_BGR2GRAY)
    if prev is not None:
        diff_sum[idx] += float(cv2.absdiff(gray, prev).mean())
        diff_n[idx] += 1
    prev = gray
    fnum += 1
cap.release()

rows = []
for i, (s, e) in enumerate(bounds):
    rows.append({"scene": i + 1, "start": round(s, 2), "end": round(e, 2),
                 "duration": round(e - s, 2),
                 "motion": round(diff_sum[i] / diff_n[i], 2) if diff_n[i] else 0.0})
with open(f"{OUT}/scenes.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["scene", "start", "end", "duration", "motion"])
    w.writeheader()
    w.writerows(rows)
with open(f"{OUT}/scenes.json", "w") as f:
    json.dump({"fps": fps, "scenes": rows}, f, indent=1)
for r in rows:
    print(f"  #{r['scene']:>2} {r['start']:>7.2f}s -> {r['end']:>7.2f}s  dur {r['duration']:>6.2f}s  motion {r['motion']:.2f}")
