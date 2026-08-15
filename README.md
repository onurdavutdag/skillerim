# skillerim

A repository of my own Claude Code skills and subagents.

## Contents

| Path | What it does |
|---|---|
| _(moved out)_ | `bilim-klasoredit` and `bilim-s-pdf` left this repo on 25 July 2026. They now live in the **`klasoredit` plugin** (`plugin-klasoredit`), renamed `klasoreditbilim` and `klasoreditbilim-s-pdf`, alongside a second skill (`klasoreditplugin`) that enforces and audits plugin naming/sync rules. |
| [`skills/istatistik-profesoru/`](skills/istatistik-profesoru/) | A skill that performs statistical analysis on a shared dataset and produces two reports: an expert-commentary report + a Python technical code report. (Note: the 16 lecture-material PDFs under `assets/` present in the local copy were not included in this repo for copyright reasons.) |
| [`skills/instagram-icerik/`](skills/instagram-icerik/) | Gets my own phone footage and photos ready to post on Instagram, entirely locally via ffmpeg: photo slideshows with music and transitions, aspect-ratio fitting that crops or pads instead of stretching, Reels/Stories/feed export presets, audio levelling and subtitle burn-in. Sits on top of `third-party/video-processing-editing/` and only fills the gaps it leaves. |
| [`skills/dhyuzmani/`](skills/dhyuzmani/) | Analyses the hospitals where a neurosurgery post opened in the Turkish compulsory-service (DHY) lottery, ranked by road distance from a reference city (Hatay by default). Combines three things per hospital: how many neurosurgeons currently work there (scanned fresh from hospital sites and appointment aggregators on every run), registered bed capacity and operating-room count, then writes a filterable Excel sheet. Distance and beds come from bundled official tables (KGM road-distance matrix, KHGM facility list); the lottery CSVs stay outside the repo because they carry doctors' names. |
| [`third-party/caveman/`](third-party/caveman/) | **Not written by me** — a personal archive copy of the [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) plugin (MIT license) that I actively use. Detail: [`VENDORED.md`](third-party/caveman/VENDORED.md). |
| [`third-party/video-processing-editing/`](third-party/video-processing-editing/) | **Not written by me** — a personal archive copy of the `video-processing-editing` skill from [erichowens/some_claude_skills](https://github.com/erichowens/some_claude_skills) (MIT license), the ffmpeg engine behind `skills/instagram-icerik/`. Detail: [`VENDORED.md`](third-party/video-processing-editing/VENDORED.md). |

## Installation

To use a file, copy the relevant `.md` file into your own `~/.claude/skills/` or `~/.claude/agents/` folder.
