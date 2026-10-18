# Use cases

## Homebrew Game Trailers — game trailer factory
Manufacture game trailers at scale from a manifest instead of a film crew:
- **Gameplay trailers**: spectate-mode capture → `videopress make` assembles the best kills/moments with punch-in zooms and captions, trailer VO mixed over native game audio.
- **Viral gameplay Shorts**: one spectacular moment per video, hook in the first second, big bold captions. The format that drives itch.io clicks.
- **Character/voice spotlights**: recurring characters get a continuity sheet (see `docs/CHARACTER-SHEETS.md`) so the same face appears across every trailer.
- **Launch announcements**: title + date + CTA in the last 5s only, never front-loaded.

Pipeline: gamepress captures the footage (`gamepress drive`, `gamepress video`) → videopress manufactures the trailer → upload to YouTube → link back to the itch.io page.
