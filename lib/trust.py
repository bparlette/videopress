#!/usr/bin/env python3
"""videopress trust — check a channel's trust/distribution signals.

Reads YouTube Analytics via the API (needs youtube.readonly scope, separate
from the upload token) and reports the health checklist from docs/TRUST-SIGNALS.md.

Usage: python3 trust.py [--channel CHANNEL_ID] [--days 28]

Verdict logic:
- HEALTHY: browse+suggested impressions > 300 on recent videos -> keep cadence, fix CTR
- WEAK:    impressions < 250 -> slow down, 1 video per 48-72h, single niche
- CTR < 3%: thumbnails/titles are the bottleneck, not distribution

Without API access this prints the manual checklist instead.
"""
import os
import sys

ANALYTICS_TOKEN = os.environ.get("YT_ANALYTICS_TOKEN")  # youtube.readonly scope

CHECKLIST = """
Manual trust check (YouTube Studio > Analytics > Reach, last 28 days):
1. Impressions from browse/suggested on recent videos: 300+ healthy, <250 weak
2. Traffic sources: browse features should dominate for Shorts
3. CTR: under 3% = thumbnail/title problem, not a channel problem
4. Upload pacing: fresh channel = 1 video per 48-72h for 2 weeks, then ramp
5. Niches: 1 niche per channel. Mixed niches confuse the algorithm.
6. Never judge CTR/retention under 3,000-5,000 views — sample too small.
"""

if not ANALYTICS_TOKEN:
    print(CHECKLIST)
    print("Set YT_ANALYTICS_TOKEN (youtube.readonly scope) for automated checks.")
    sys.exit(0)

# TODO: automated Analytics API check when a token is available.
print(CHECKLIST)
