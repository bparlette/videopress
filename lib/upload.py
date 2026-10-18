#!/usr/bin/env python3
"""videopress upload — upload a video to YouTube via the Data API v3.

Usage: python3 upload.py video.mp4 --title "TITLE" [--desc "DESCRIPTION"]
       [--thumb thumbnail.png] [--category 24] [--privacy public|unlisted|private]

Auth: reads from env or ~/.videopress/:
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
Never put credentials in the repo. One refresh token per channel — run the
OAuth consent flow once per brand account and store each token separately.

Upload path: refresh token -> access token -> resumable upload session ->
PUT video bytes -> set thumbnail. Playlist adds need a broader scope than
youtube.upload and will 403 — add to playlists manually.
"""
import json
import os
import sys
import urllib.request
import urllib.parse

args = sys.argv[1:]
VIDEO = args[0]
TITLE = DESC = THUMB = None
CATEGORY = "24"  # Entertainment
PRIVACY = "public"
i = 1
while i < len(args):
    if args[i] == "--title" and i + 1 < len(args): TITLE = args[i + 1]; i += 2
    elif args[i] == "--desc" and i + 1 < len(args): DESC = args[i + 1]; i += 2
    elif args[i] == "--thumb" and i + 1 < len(args): THUMB = args[i + 1]; i += 2
    elif args[i] == "--category" and i + 1 < len(args): CATEGORY = args[i + 1]; i += 2
    elif args[i] == "--privacy" and i + 1 < len(args): PRIVACY = args[i + 1]; i += 2
    else: i += 1

if not TITLE:
    sys.exit("error: --title is required")

CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")
REFRESH = os.environ.get("YT_REFRESH_TOKEN")
if not (CLIENT_ID and CLIENT_SECRET and REFRESH):
    sys.exit("error: set YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN")


def post(url, data, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {},
                                 method="POST")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


# 1. access token
tok = post("https://oauth2.googleapis.com/token", urllib.parse.urlencode({
    "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH, "grant_type": "refresh_token",
}).encode())
AT = tok["access_token"]
H = {"Authorization": f"Bearer {AT}", "Content-Type": "application/json"}

# 2. resumable session
body = json.dumps({
    "snippet": {"title": TITLE, "description": DESC or "",
                "categoryId": CATEGORY},
    "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False},
}).encode()
req = urllib.request.Request(
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    data=body, headers={**H, "X-Upload-Content-Type": "video/mp4"}, method="POST")
with urllib.request.urlopen(req) as r:
    session = r.headers["Location"]

# 3. upload bytes
size = os.path.getsize(VIDEO)
req = urllib.request.Request(session, method="PUT",
    headers={"Content-Length": str(size), "Content-Type": "video/mp4"})
with open(VIDEO, "rb") as f:
    req.data = f.read()
with urllib.request.urlopen(req) as r:
    vid = json.load(r)
VID = vid["id"]
print(f"uploaded: https://www.youtube.com/watch?v={VID}")

# 4. thumbnail
if THUMB and os.path.exists(THUMB):
    boundary = "vp-boundary"
    with open(THUMB, "rb") as f:
        img = f.read()
    payload = (f"--{boundary}\r\nContent-Type: image/png\r\n\r\n".encode() + img
               + f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={VID}",
        data=payload, method="POST",
        headers={"Authorization": f"Bearer {AT}",
                 "Content-Type": f"multipart/related; boundary={boundary}"})
    with urllib.request.urlopen(req) as r:
        json.load(r)
    print("thumbnail set")
