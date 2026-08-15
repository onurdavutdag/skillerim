# Vendored: video-processing-editing

This folder is **not** something I wrote — it is a copy of the `video-processing-editing`
skill from [erichowens/some_claude_skills](https://github.com/erichowens/some_claude_skills)
(upstream path `.claude/skills/video-processing-editing/`), taken at commit `d6f30eb`
(5 March 2026). It was placed here for my own archive/backup.

License: MIT (see `LICENSE`, copyright belongs to Erich Owens — the original notice is preserved).

For the current/original source, see the repo above; for installation, using the skills
registry is more correct — this is only a personal archive copy:

```
npx skills add erichowens/some_claude_skills@video-processing-editing -g -y
```

## Why I use it

It is the ffmpeg engine behind my own [`skills/instagram-icerik/`](../../skills/instagram-icerik/)
skill: cutting, trimming, concatenating, audio mixing and export presets all live here.
`instagram-icerik` does not modify this folder (an upstream update would overwrite it) —
it sits on top and adds what is missing for Instagram: photo slideshows, and aspect-ratio
fitting that crops or pads instead of stretching.

Requires `ffmpeg` and `ffprobe` on PATH (`winget install --id Gyan.FFmpeg` on Windows).
