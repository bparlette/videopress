# Viral playbook — distilled patterns

## The hook economy
- Hook in the first second. No warm-up, no title card, no "hey guys".
- Title = curiosity gap + trend hook, never a summary.
- Thumbnail tells the whole story (before/after + red arrow is the proven pattern).

## Pacing
- New visual every 1–3 seconds. Never a static shot longer than 3s.
- Constant zoom in/out punch-ins. Scenes switching under the talking.
- Zero dead air. Big bold captions on key lines.

## Clips
- REAL clips, not AI stills. AI-generated stills read as AI-made instantly — brief filler only, never the backbone.
- Curated clips = transformative commentary: narration over every clip, sources credited.
- Never straight-repost. One idea per video.

## "Why did humans start X?" origin explainers
Underrated niche: cartoon stickman explainers asking "why did humans start [everyday thing]?". One 8:15 video did 3.1M views in 10 days, est. $25k–30k. Why it works: thumbnail tells the whole story, zero competition + huge curiosity, 8 min = full watch-through + mid-rolls, collab credits boost trust score. Pattern: everyday thing → "why did humans start…" → draw the before and after.

## Character consistency
For recurring characters: build a continuity sheet ONCE (profile + 4-angle turnaround, 3 close-ups, 8 expressions, 6 poses, costume details, color palette, "DO NOT CHANGE" checklist). Then every video starts from the sheet: "Replace the person in {video} with the person in {character sheet}." Motion/camera/audio from the video, face from the sheet. One recognizable silhouette, family around the character so one face becomes a show.

## Solo shorts studio stack
One tool per step, 1-hour video → stack of vertical clips: yt-dlp → Whisper → WhisperX (word timestamps) → Ollama (hook picker) → DeepFilterNet (denoise) → auto-editor (cut silence) → PySceneDetect (scene cuts) → MediaPipe (face-tracked 9:16 crop) → Remotion (burn captions, assemble) → FFmpeg (encode). Hand the loop to an AI agent and let it run the studio.
